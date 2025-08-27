import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from urllib.parse import urlparse

import gitlab
import requests
from gitlab import Gitlab
from gitlab.base import RESTObject
from gitlab.exceptions import GitlabError
from gitlab.v4.objects import Group, Project, ProjectBranch, ProjectCommit
from gitlab.v4.objects import User as GitlabUser

from jf_ingest import logging_helper
from jf_ingest.config import GitAuthConfig, GitLabAuthConfig
from jf_ingest.constants import Constants
from jf_ingest.graphql_utils import GQL_PAGE_INFO_BLOCK
from jf_ingest.jf_git.exceptions import (
    GitAuthenticationException,
    GqlPageTimeoutException,
)
from jf_ingest.jf_git.standardized_models import (
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedRepository,
)
from jf_ingest.utils import (
    GITLAB_STATUSES_TO_RETRY,
    RetryLimitExceeded,
    hash_filename,
    parse_gitlab_api_version,
    retry_for_status,
    retry_session,
)

logger = logging.getLogger(__name__)


class GitlabClient:
    # NOTE: We currently have some functions in this class that access GraphQL.
    # When trying to implement that, we ran into some authentication issues and limitations that moved us toward
    #   using the rest client instead.
    # Functions that make use of GraphQL are suffixed with _gql.
    # If we want to keep them, we'd ideally eventually move them to their own subclass of the client.
    GITLAB_GQL_USER_FRAGMENT = "... on User {login, id: databaseId, email, name, url}"
    GITLAB_GQL_USER_NODES = 'id, name, username, webUrl, publicEmail'
    GITLAB_GQL_SHORT_REPO_NODES = 'id, name, webUrl'

    def __init__(self, auth_config: GitAuthConfig, **kwargs):
        """Gitlab Client, used as a wrapper for getting raw data from the API.
        This client will get data mainly from the GraphQL API endpoints, although
        it will use the REST API endpoints for a small amount of functions as well.

        Args:
            auth_config (GitAuthConfig): A valid GitAuthConfiguration object. MUST BE A GitLabAuthConfig object, NOT A GitAuthConfig OBJECT!!
            kwargs: kwargs are used to pass arguments to the inner Session object, if no session object is provided as part of the GitAuthConfig
        """
        if type(auth_config) != GitLabAuthConfig:
            raise Exception(
                f'Unknown Auth Config provided to GitlabClient. GitAuthConfig type is expected to be a GitLabAuthConfig type, but received {type(auth_config)}'
            )
        self.company_slug: str = auth_config.company_slug
        self.rest_api_url: Optional[str] = auth_config.base_url
        self.gql_base_url: str = f'{auth_config.base_url}/api/graphql'
        if session := auth_config.session:
            self.session: requests.Session = session
        else:
            self.session = retry_session(**kwargs)
            self.session.headers.update(
                {
                    'Authorization': f'Bearer {auth_config.token}',
                    'Content-Type': 'application/json',
                    'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({requests.utils.default_user_agent()})',
                }
            )
        self.session.verify = auth_config.verify
        self.client: Gitlab = Gitlab(
            url=self.rest_api_url,
            session=self.session,
            ssl_verify=auth_config.verify,
            keep_base_url=auth_config.keep_base_url,
        )
        try:
            self.compatibility_config = self.get_api_compatibility_config()
        except RetryLimitExceeded:
            logging_helper.send_to_agent_log_file(
                'Max number of retries reached when attempting to get Server Version. '
                'I think it\'s safe to assume we are having authentication problems. '
                'Raising GitAuthenticationException.',
                level=logging.WARNING,
            )
            raise GitAuthenticationException(
                'Max number of retries reached when attempting to get the Gitlab Server version from API endpoint /api/v4/metadata. '
                'This likely indicates that we are having authentication problems.'
            )

    @property
    def supports_get_all_organizations(self):
        # listing all organizations is available for private Gitlab instances ONLY
        # otherwise, we will be querying the _entire_ public repository
        if not self.rest_api_url:
            return False

        hostname = urlparse(self.rest_api_url).hostname
        return not hostname.endswith(Constants.GITLAB_PUBLIC_HOSTNAME)

    def get_api_version(self) -> str:
        try:
            resp = retry_for_status(self.client.http_get, '/metadata')
        except Exception as e:
            logger.warning(
                f'Unable to fetch server version via /metadata. Checking /version... Exception: {e}'
            )
            resp = retry_for_status(self.client.http_get, '/version')

        return str(resp['version'])

    def get_api_compatibility_config(self) -> Dict:
        """
        Some versions of the api may be missing functionality. This function is designed to help us work around those.

        Returns:
            compatibility_mapping Dict: A collection of keys and values to help the client handle version differences.
        """
        compatibility_config = {
            'gql_skip_pr_closed_at': False,
            'gql_skip_commit_committed_date': False,
        }

        # Get version stripped of any tags or other letters. This should align roughly with semver
        api_version: str = self.get_api_version()

        if api_version:
            major_version = None
            minor_version = None

            try:
                api_version = parse_gitlab_api_version(api_version)
                version_split = api_version.split('.')
                major_version = int(version_split[0])

                if len(version_split) > 1:
                    minor_version = int(version_split[1])
            except ValueError:
                logger.warning(
                    ':WARN: Unable to determine GitLab server version. Enabling all compatability configuration.'
                )

            # API versions prior to 17.4 do not have closedAt available on the mergedRequest. We can still fetch the rest
            # of the data we want via GQL, but that field needs to be populated via the api for customers on older versions.
            if (not major_version or major_version < 17) or (
                major_version == 17 and (not minor_version or minor_version < 4)
            ):
                compatibility_config['gql_skip_pr_closed_at'] = True

            if not major_version or major_version < 16:
                compatibility_config['gql_skip_commit_committed_date'] = True

        return compatibility_config

    def get_organization_name_full_path_and_url(self, login: str) -> Tuple[str, str, str]:
        """In Jellyfish Land, the JFGithubOrganization is the normalization of Github Organizations,
        AzureDevops Organizations, Bitbucket Projects, and Gitlab Groups. The login field is the unique
        key. For Gitlab Groups, we set the login to the be the Group ID, which is a numeric value.
        The GraphQL Group Queries accept a "fullPath" argument, and NOT the Group ID. If we only have
        the GroupID (set by the login value), then this helper function can be used to translate the
        GroupID to a Full Path.
        NOTE: For performance reasons, we should probably graph the FullPath when we query GraphQL for
        Groups in general, and then cache those values. We should NOT call this function everytime,
        because it could have performance implications

        Args:
            login (str): The JFGithubOrganization login, which is the Group ID in Gitlab land
        Returns:
            name, full_path, url (str, str, str): The name, Full Path, and url for this gitlab Group
        """
        group_url = f'{self.rest_api_url}/api/v4/groups/{login}?with_projects=False'
        response: requests.Response = retry_for_status(
            self.session.get, url=group_url, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
        )
        response.raise_for_status()
        response_json = response.json()
        return (
            str(response_json['name']),
            str(response_json['full_path']),
            str(response_json['web_url']),
        )

    def get_raw_result_gql(self, query_body: str, max_attempts: int = 5) -> Dict:
        """Gets the raw results from a Graphql Query.

        Args:
            query_body (str): A query body to hit GQL with
            max_attempts (int, optional): The number of retries we should make when we specifically run into GQL Rate limiting.
                This value is important if the GQL endpoint doesn't give us (or gives us a malformed) rate limit header.
                Defaults to 5.

        Raises:
            GqlRateLimitExceededException: A custom exception if we run into GQL rate limiting (200 response) and we run out of attempts (based on max_attempts)
            RetryLimitExceeded: A custom exception thrown by retry_for_status if we exceed our retries (based on max_attempts)
            Exception: Any other random exception we encounter, although the big rate limiting use cases are generally covered

        Returns:
            dict: A raw dictionary result from GQL
        """
        response: requests.Response = retry_for_status(
            self.session.post,
            url=self.gql_base_url,
            json={'query': query_body},
            max_retries_for_retry_for_status=max_attempts,
        )
        json_str = response.content.decode()
        json_data: Dict = json.loads(json_str)
        if error_list_dict := json_data.get('errors'):
            error_message = ','.join([error_dict.get('message') for error_dict in error_list_dict])

            # If we received a "Timeout on..." response, we should raise this specific exception so we can attempt with
            # a smaller page size.
            if response.status_code == 200 and error_message.startswith('Timeout on'):
                logging_helper.send_to_agent_log_file(
                    f'Timeout detected when querying for data. Received error: {error_message}',
                    level=logging.WARNING,
                )
                raise GqlPageTimeoutException({error_message})
            else:
                raise Exception(
                    f'An error occurred when attempting to query GraphQL (response code {response.status_code}): {error_message}'
                )

        return json_data

    def page_results_gql(
        self,
        query_body: str,
        path_to_page_info: str,
        cursor: Optional[str] = None,
        page_size: int = 100,
    ) -> Generator[Dict, None, None]:
        """
        This is a helper function for paging results from GraphQL.
        It expects a query body that has "%s" for both `first` (page_size) and `after` (cursor).
        THE ORDER IS IMPORTANT, `first` (page_size)` MUST COME BEFORE `after` (cursor) IN THE QUERY BODY.
        BOTH MUST BE PRESENT.
        QUERY BODIES MUST INCLUDE VALID PAGE INFO (see GQL_PAGE_INFO_BLOCK).

        Args:
            query_body (str): The query body to hit GraphQL with
            path_to_page_info (str): A string of period separated words that lead
                to the part of the query that we are trying to page. Example: data.organization.userQuery
            cursor (str, optional): This argument is used to recursively to page.
                The cursor is provided by GitLab (endCursor) and is used to denote the next item to start from.
                Defaults to 'null'. LEAVE AS 'null' OR `None` if fetching first page.
            page_size (int): Page size to use in query. This can be altered by our backoff if we run into timeouts.
                Defaults to 100.

        Yields:
            Generator[dict, None, None]: This function yields each item from all the pages paged, item by item
        """
        hasNextPage = True
        if not cursor:
            cursor = 'null'
        else:
            cursor = f'"{cursor}"'

        while hasNextPage:
            try:
                # Fetch results
                result = self.get_raw_result_gql(query_body=query_body % (page_size, cursor))

                yield result

                # Check if there are additional pages.
                page_info = self.get_path_value(path_to_page_info + '.pageInfo', result) or {}
                _cursor = page_info.get('endCursor', None)
                hasNextPage = page_info.get('hasNextPage', False) and _cursor

                # Cursor must be wrapped in quotes.
                cursor = f'"{_cursor}"'
            except GqlPageTimeoutException as e:
                # Sometimes we time out on validation of a query or if some of the nested objects in a query timeout.
                # This can be helped by reducing the pagination size for the remainder of the queries.
                # GitLab reuses cursors even if the page size or payload selection changes.
                # In the future, we can choose to skip selecting nested fields if they consistently time out.
                if page_size <= 1:
                    # TODO: We should probably track this with JellyCounter
                    logging_helper.send_to_agent_log_file(
                        f"Unable to successfully query for data, due to excessive timeouts. Breaking out of paging loop",
                        level=logging.ERROR,
                    )
                    break
                else:
                    new_page_size = max(1, page_size - 10)
                    logging_helper.send_to_agent_log_file(
                        f"Received timeout with page size {page_size}. Reducing to {new_page_size}...",
                        level=logging.WARNING,
                    )
                    page_size = new_page_size
                    # Wait 30 seconds here to possibly help with any hung up resources
                    time.sleep(30)
            except RetryLimitExceeded as e:
                logging_helper.send_to_agent_log_file(
                    f"Exceeded retry limit when fetching data. Breaking out of paging loop. Exception: {e}",
                    level=logging.ERROR,
                )
                break

    def get_path_value(self, path_value: str, data_dict: Optional[dict] = None) -> Optional[Any]:
        """
        This function takes a path value separated by periods to determine nesting in a dict. This will be primarily
        used to safely access response pages from GQL. We log a warning if we're provided an empty dict or None.

        Args:
            path_value (str): A period-delineated string of keys to recursively traverse and then return the last key.
                If the key is not present, we will return an empty dictionary.
                Example: data.project.mergeRequests.nodes
            data_dict (Optional[dict]): Dictionary to traverse. If not provided

        Returns:
            Optional[Any]: If there is a value for the given key path, it's returned.
                Defaults to an empty dict.
        """
        if not data_dict:
            logging_helper.send_to_agent_log_file(
                f"Null or empty dict provided for path value {path_value}.",
                level=logging.WARNING,
            )
            return {}

        result = data_dict

        path_tokens = path_value.split('.')
        for token in path_tokens:
            result = result.get(token, {})

        return result

    def get_teams(self, *args, **kwargs) -> list:
        """
        This function is to align with other clients.
        GitLab does not have a concept of teams past groups, which we use as organizations.
        This will return an empty list, regardless of arguments.
        """
        return []

    def get_repos(
        self, jf_org: StandardizedOrganization, only_private: bool = False
    ) -> Generator[Project | RESTObject, None, None]:
        try:
            group = retry_for_status(
                self.client.groups.get, jf_org.login, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
            )

            kwargs_dict: dict[str, Union[bool, str]] = {'iterator': True, 'include_subgroups': True}
            if only_private:
                kwargs_dict['visibility'] = 'private'

            for repo in retry_for_status(group.projects.list, statuses_to_retry=GITLAB_STATUSES_TO_RETRY, **kwargs_dict):  # type: ignore
                yield repo
        except (requests.exceptions.ConnectionError, GitlabError, RetryLimitExceeded) as e:
            logger.warning(
                f"Failed to pull repos for group {jf_org.login}. Skipping. Exception: {e}"
            )

    def get_repos_count(self, login: str, only_private: Optional[bool] = False) -> int:
        url = f"{self.rest_api_url}/api/v4/groups/{login}/projects"
        params: dict[str, Union[str, int]] = {'per_page': 1}

        if only_private:
            params['visibility'] = 'private'

        try:
            response: requests.Response = retry_for_status(
                self.session.get, url=url, params=params, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
            )
            return int(response.headers.get('X-Total', 0))
        except (requests.exceptions.ConnectionError, GitlabError, RetryLimitExceeded) as e:
            logger.warning(f"Failed to get repo count for {login}. Skipping. Exception: {e}")
            return 0

    def get_commits(
        self,
        jf_repo: StandardizedRepository,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        branch_name: Optional[str] = None,
    ) -> Generator[ProjectCommit | RESTObject, None, None]:
        project_id = jf_repo.id
        project = retry_for_status(
            self.client.projects.get, project_id, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
        )

        kwargs_dict: dict[str, Any] = {
            'iterator': True,  # Returns a generator
        }
        if branch_name:
            kwargs_dict['ref_name'] = branch_name
        if since:
            kwargs_dict['since'] = since
        if until:
            kwargs_dict['until'] = until

        try:
            for commit in retry_for_status(project.commits.list, statuses_to_retry=GITLAB_STATUSES_TO_RETRY, **kwargs_dict):  # type: ignore
                yield commit
        except (requests.exceptions.ConnectionError, GitlabError, RetryLimitExceeded) as e:
            logger.warning(
                f"Failed to pull commits for repo {jf_repo.name}. Skipping. Exception: {e}"
            )

    def get_branches_for_repo(
        self, jf_repo: StandardizedRepository, branch_name: Optional[str] = None
    ) -> Generator[ProjectBranch | RESTObject, None, None]:
        """
        Attempts to pull branches for a given repository.

        Args:
            standardized_repo (StandardizedRepository): A standardized repo, which is used to pull repositories.
            branch_name (Optional[str]): Name of the branch to pull. If this is provided, only attempt to pull this
                branch. Otherwise, attempts to pull all branches.

        Yields:
            ProjectBranch | RESTObject: Objects generated by the GitLab client.
        """
        project_id = jf_repo.id
        project = retry_for_status(
            self.client.projects.get, project_id, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
        )
        branches_list: List[ProjectBranch | RESTObject] = []

        kwargs_dict: dict[str, Any] = {'iterator': True}
        if branch_name:
            try:
                branches_list.append(project.branches.get(branch_name))
            except gitlab.exceptions.GitlabGetError:
                try:
                    # Per legacy code (scc 1/9/2023), we may hit this for very old GitLab servers (<11.9).
                    # In this case, we hit the branch list endpoint and use the given branch name as the search term.
                    logger.info(
                        f"Failed to fetch branch '{branch_name}' for '{jf_repo.name}' via get, falling back to search."
                    )

                    # We technically could use regex here to reduce extra hits, but we're not guaranteed to have regex
                    # on very old versions of GitLab's api. Limit this to 10 per page, likely to have a hit there.
                    kwargs_dict['search'] = branch_name
                    kwargs_dict['per_page'] = 10
                    branches = retry_for_status(project.branches.list, statuses_to_retry=GITLAB_STATUSES_TO_RETRY, **kwargs_dict)  # type: ignore

                    # If we're given a branch name, we only expect one branch back. We *may* get more than one, so just
                    # return the first we get that completely matches the branch name.
                    found_branch = None
                    for branch in branches:
                        if branch.name == branch_name:
                            found_branch = branch
                            branches_list.append(branch)
                            break

                    if not found_branch:
                        logger.warning(
                            f"Failed to find branch '{branch_name}' for '{jf_repo.name}', skipping..."
                        )

                except gitlab.exceptions.GitlabListError:
                    # We believe Gitlab does this to mean "0 results".
                    logger.warning(
                        f"Failed to find branch '{branch_name}' for '{jf_repo.name}', skipping..."
                    )
        else:
            try:
                yield from retry_for_status(project.branches.list, statuses_to_retry=GITLAB_STATUSES_TO_RETRY, **kwargs_dict)  # type: ignore
            except gitlab.exceptions.GitlabListError:
                # We believe Gitlab does this to mean "0 results".
                logger.warning(f"Failed to fetch branches for '{jf_repo.name}', skipping...")

        for branch in branches_list:
            yield branch

    def get_organizations_rest_api(self) -> Generator[Group | RESTObject, None, None]:
        kwargs_dict: dict[str, Any] = {'iterator': True, 'query_data': {'all_available': True}}
        groups = retry_for_status(
            self.client.groups.list, statuses_to_retry=GITLAB_STATUSES_TO_RETRY, **kwargs_dict
        )

        for group in groups:
            if getattr(group, 'parent_id', None) is None:
                yield group

    def get_organizations_gql(
        self, page_size: int = 100, sort_key: str = 'id_asc'
    ) -> Generator[Dict, None, None]:
        query_body = f"""
        {{
            groupsQuery: groups(first: %s, sort: "{sort_key}", after: %s){{
                {GQL_PAGE_INFO_BLOCK}
                groups: nodes {{
                    groupIdStr: id
                    name
                    fullPath
                    webUrl
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.groupsQuery', page_size=page_size
        ):
            groups = self.get_path_value('data.groupsQuery.groups', page) or []
            for group in groups:
                yield group

    def get_repos_gql(
        self, group_full_path: str, page_size: int = 100
    ) -> Generator[Dict, None, None]:
        query_body = f"""
        {{
            group(fullPath: "{group_full_path}") {{
                projectsQuery: projects(first: %s, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    projects: nodes {{
                        ... on Project {{
                            name,
                            webUrl,
                            description,
                            isForked,
                            repository {{
                                ... on Repository {{
                                    defaultBranchName: rootRef
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.group.projectsQuery', page_size=page_size
        ):
            projects = self.get_path_value('data.group.projectsQuery.projects', page) or []
            for project in projects:
                yield project

    def get_users(self, group_id: str) -> Generator[Union[RESTObject, GitlabUser], None, None]:
        """
        Gets all users for a given Gitlab group (aka organization)

        Args:
            group_id: ID of the group (organization) to get users for

        Returns:
            Generator[Union[RESTObject, GitlabUser], None, None]: Generator yielding one user object at a time
        """
        try:
            group = retry_for_status(
                self.client.groups.get, group_id, statuses_to_retry=GITLAB_STATUSES_TO_RETRY
            )

            for user in retry_for_status(
                group.members.list,
                all=True,
                iterator=True,
                statuses_to_retry=GITLAB_STATUSES_TO_RETRY,
                max_retries_for_retry_for_status=3,
            ):
                yield user
        except Exception as e:
            logging_helper.send_to_agent_log_file(
                f'When attempting to get user data we ran in the following exception: {e}. '
                f'Giving up on pulling users for group {group_id} and moving on',
                level=logging.WARNING,
            )

    def get_prs(
        self,
        project_full_path: str,
        start_cursor: Optional[Any] = None,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,
        pull_files_for_pr: Optional[bool] = False,
        hash_files_for_pr: Optional[bool] = False,
        page_size: int = 100,
    ) -> Generator[Dict, None, None]:
        """
        Gets all pull requests for a given Gitlab project (aka repository) using GraphQL

        Args:
            project_full_path (str): Full path of the project (repository) to get pull requests for
            start_cursor (Optional[str]): A cursor string to start from when fetching prs, defaults to None
            start_window (Optional[datetime]): Filter prs to those updated after this date. defaults to None
            end_window (Optional[datetime]): Filter prs to those updated before this date. defaults to None
            pull_files_for_pr (Optional[bool]): Used to determine if we should pull file data with prs, defaults to False
            hash_files_for_pr (Optional[bool]): Used to determine if pulled filenames should be hashed, defaults to False
                Only applied to filenames, so will have no effect if pull_files_for_pr is False
            page_size (int): Page size for the API call, defaults to 100

        Returns:
            Generator[Dict, None, None]: Generator yielding one pull request dict at a time
        """
        query_body = f"""
        {{
            project(fullPath: "{project_full_path}") {{
                mergeRequests(first: %s, after: %s, sort: UPDATED_DESC{f', updatedAfter: "{start_window.isoformat()}"' if start_window else ''}{f', updatedBefore: "{end_window.isoformat()}"' if end_window else ''}) {{
                    {GQL_PAGE_INFO_BLOCK}
                    nodes {{
                        id
                        iid
                        {'closedAt' if not self.compatibility_config['gql_skip_pr_closed_at'] else ''}
                        updatedAt
                        mergedAt
                        createdAt
                        title
                        description
                        webUrl
                        sourceBranch
                        targetBranch
                        mergeCommitSha
                        diffStatsSummary {{ additions, deletions, fileCount }}
                        {'diffStats { additions, deletions, path }' if pull_files_for_pr else ''}
                        sourceProject {{ {self.GITLAB_GQL_SHORT_REPO_NODES} }}
                        targetProject {{ {self.GITLAB_GQL_SHORT_REPO_NODES} }}
                        author {{ {self.GITLAB_GQL_USER_NODES} }}
                        mergeUser {{ {self.GITLAB_GQL_USER_NODES} }}
                        {self._get_pr_commits_query_block(enable_paging=False)}
                        {self._get_pr_comments_query_block(enable_paging=False)}
                        {self._get_pr_approvals_query_block(enable_paging=False)}
                    }}
                }}
            }}
        }}
        """

        for page in self.page_results_gql(
            query_body=query_body,
            path_to_page_info='data.project.mergeRequests',
            cursor=start_cursor,
            page_size=page_size,
        ):
            pr_nodes = self.get_path_value('data.project.mergeRequests.nodes', page) or []
            for pr_node in pr_nodes:
                pr_iid = pr_node['iid']

                # Fetch any commits not fetched on initial page
                if self.get_path_value('commits.pageInfo.hasNextPage', pr_node):
                    commits = [
                        commit
                        for commit in self.get_pr_commits(
                            project_full_path=project_full_path,
                            pr_iid=pr_iid,
                        )
                    ]
                    pr_node['commits']['nodes'] = commits

                # Fetch any comments not fetched on initial page
                if self.get_path_value('notes.pageInfo.hasNextPage', pr_node):
                    comments = [
                        comment
                        for comment in self.get_pr_comments(
                            project_full_path=project_full_path,
                            pr_iid=pr_iid,
                        )
                    ]
                    pr_node['notes']['nodes'] = comments

                # Fetch any approvals not fetched on initial page
                if self.get_path_value('approvedBy.pageInfo.hasNextPage', pr_node):
                    approvals = [
                        approval
                        for approval in self.get_pr_approvals(
                            project_full_path=project_full_path,
                            pr_iid=pr_iid,
                        )
                    ]
                    pr_node['approvedBy']['nodes'] = approvals

                # Hash filenames if enabled and we have file paths to hash
                if pull_files_for_pr and hash_files_for_pr:
                    hashed_files = []
                    for unhashed_file in pr_node.get('diffStats', []):
                        unhashed_file['path'] = hash_filename(unhashed_file['path'])
                        hashed_files.append(unhashed_file)
                    pr_node['diffStats'] = hashed_files

                yield pr_node

    def get_pr_commits(
        self,
        project_full_path: str,
        pr_iid: str,
        page_size: int = 20,
    ) -> Generator[dict, None, None]:
        query_body = f"""   
        {{         
            project(fullPath: "{project_full_path}") {{
                mergeRequest(iid: "{pr_iid}") {{
                    {self._get_pr_commits_query_block(enable_paging=True)}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body,
            path_to_page_info='data.project.mergeRequest.commits',
            page_size=page_size,
        ):
            nodes = self.get_path_value('data.project.mergeRequest.commits.nodes', page) or []
            for node in nodes:
                yield node

    def get_pr_commits_rest_api(
        self, standardized_repo: StandardizedRepository, api_pr: dict
    ) -> Generator[dict, None, None]:
        commits_path = (
            f'/projects/{standardized_repo.id}/merge_requests/{int(api_pr["iid"])}/commits'
        )
        return retry_for_status(self.client.http_list, commits_path, iterator=True)  # type: ignore

    def get_pr_comments(
        self,
        project_full_path: str,
        pr_iid: str,
        page_size: int = 20,
    ) -> Generator[dict, None, None]:
        query_body = f"""
        {{      
            project(fullPath: "{project_full_path}") {{
                mergeRequest(iid: "{pr_iid}") {{
                    {self._get_pr_comments_query_block(enable_paging=True)}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body,
            path_to_page_info='data.project.mergeRequest.notes',
            page_size=page_size,
        ):
            nodes = self.get_path_value('data.project.mergeRequest.notes.nodes', page) or []
            for node in nodes:
                yield node

    def get_pr_approvals(
        self,
        project_full_path: str,
        pr_iid: str,
        page_size: int = 20,
    ) -> Generator[dict, None, None]:
        query_body = f"""
        {{       
            project(fullPath: "{project_full_path}") {{
                mergeRequest(iid: "{pr_iid}") {{
                    {self._get_pr_approvals_query_block(enable_paging=True)}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body,
            path_to_page_info='data.project.mergeRequest.approvedBy',
            page_size=page_size,
        ):
            nodes = self.get_path_value('data.project.mergeRequest.approvedBy.nodes', page) or []
            for node in nodes:
                yield node

    def _get_pr_commits_query_block(self, enable_paging: bool = False):
        return f"""
            commits(first: {'%s, after: %s' if enable_paging else '5'}) {{
                {GQL_PAGE_INFO_BLOCK}
                nodes {{
                    id
                    sha
                    webUrl
                    message
                    {'committedDate' if not self.compatibility_config['gql_skip_commit_committed_date'] else ''}
                    authoredDate
                    author {{ {self.GITLAB_GQL_USER_NODES} }}
                }}
            }}
        """

    def _get_pr_comments_query_block(self, enable_paging: bool = False):
        return f"""
            notes(first: {'%s, after: %s' if enable_paging else '5'}) {{
                {GQL_PAGE_INFO_BLOCK}
                nodes {{
                    id
                    body
                    createdAt
                    system
                    author {{ {self.GITLAB_GQL_USER_NODES} }}
                }}
            }}
        """

    def _get_pr_approvals_query_block(self, enable_paging: bool = False):
        return f"""
            approvedBy(first: {'%s, after: %s' if enable_paging else '5'}) {{
                {GQL_PAGE_INFO_BLOCK}
                nodes {{ {self.GITLAB_GQL_USER_NODES} }}
            }}
        """
