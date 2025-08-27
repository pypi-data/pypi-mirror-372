import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union

from gitlab.base import RESTObject
from gitlab.v4.objects import Group, Project, ProjectBranch, ProjectCommit
from gitlab.v4.objects import User as GitlabUser

from jf_ingest import logging_helper
from jf_ingest.config import GitConfig, IngestionType
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.clients.gitlab import GitlabClient
from jf_ingest.jf_git.standardized_models import (
    PullRequestReviewState,
    StandardizedBranch,
    StandardizedCommit,
    StandardizedFileData,
    StandardizedJFAPIPullRequest,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestAuthor,
    StandardizedPullRequestComment,
    StandardizedPullRequestMetadata,
    StandardizedPullRequestReview,
    StandardizedRepository,
    StandardizedShortRepository,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.utils import (
    GitLabGidObjectMapping,
    batch_iterable,
    get_attribute,
    get_id_from_gid,
    get_ingestion_type,
    hash_filename,
    parse_gitlab_date,
)

logger = logging.getLogger(__name__)


class GitlabAdapter(GitAdapter):

    def __init__(self, config: GitConfig):
        self.config = config
        self.client = GitlabClient(auth_config=config.git_auth_config)
        self.group_id_to_full_path: Dict[str, str] = {}

    def get_api_scopes(self) -> str:
        """Return the list of API Scopes. This is useful for Validation

        Returns:
            str: A string of API scopes we have, given the adapters credentials
        """
        raise NotImplementedError()

    @staticmethod
    def _get_id_from_gid(gitlab_gid: str, object_name: str) -> str:
        # Convenience wrapper for util function get_id_from_gid
        return get_id_from_gid(gitlab_gid, object_name)

    @staticmethod
    def _standardize_commit_author(api_user: dict) -> StandardizedUser:
        id = api_user.get('id') or api_user.get('email')  # Commit users may not have ids
        name = api_user.get('name')
        login = api_user.get('login') or api_user.get('email')
        email = api_user.get('email')

        return StandardizedUser(
            id=str(id),
            login=str(login),
            name=str(name),
            email=str(email),
        )

    @staticmethod
    def _standardize_gitlab_commit(
        gitlab_commit: ProjectCommit | RESTObject,
        standardized_repo: StandardizedRepository,
        branch_name: str,
    ) -> StandardizedCommit:
        """
        Converts a ProjectCommit from the gitlab client to a standardized jf commit.
        """
        author = GitlabAdapter._standardize_commit_author(
            {
                'name': gitlab_commit.author_name,
                'email': gitlab_commit.author_email,
            }
        )
        return StandardizedCommit(
            hash=gitlab_commit.id,
            author=author,
            url=gitlab_commit.web_url,
            commit_date=parse_gitlab_date(gitlab_commit.committed_date),
            author_date=parse_gitlab_date(gitlab_commit.authored_date),
            message=gitlab_commit.message,
            is_merge=len(gitlab_commit.parent_ids) > 1,
            repo=standardized_repo.short(),  # use short form of repo
            branch_name=branch_name,
        )

    @staticmethod
    def _standardize_gitlab_project(
        gitlab_repo: Project | RESTObject,
        standardized_organization: StandardizedOrganization,
    ) -> StandardizedRepository:
        """
        Converts a Project from the gitlab client to a standardized jf project.
        """
        repo_name = gitlab_repo.name
        default_branch_name: str | None = get_attribute(gitlab_repo, 'default_branch', default=None)
        return StandardizedRepository(
            id=str(gitlab_repo.id),
            name=repo_name,
            full_name=repo_name,
            url=gitlab_repo.web_url,
            default_branch_sha='',
            default_branch_name=default_branch_name,
            organization=standardized_organization,
            is_fork=bool(getattr(gitlab_repo, 'forked_from_project', False)),
            full_path=gitlab_repo.path_with_namespace,
        )

    @staticmethod
    def _standardize_gitlab_branch(
        gitlab_branch: ProjectBranch | RESTObject,
        standardized_repository: StandardizedRepository,
    ) -> StandardizedBranch | None:
        """
        Converts a Branch (ProjectBranch) from the gitlab client to a standardized jf branch.
        """
        if not gitlab_branch:
            return None
        branch_name = get_attribute(gitlab_branch, 'name', default=None)
        return StandardizedBranch(
            name=branch_name,
            sha=gitlab_branch.commit['id'],
            repo_id=standardized_repository.id,
            is_default=gitlab_branch.default,
        )

    @staticmethod
    def _standardize_user(api_user: Union[RESTObject, GitlabUser]) -> StandardizedUser:
        return StandardizedUser(
            id=api_user.id,
            name=api_user.name,
            login=api_user.username,
            email=None,
            url=api_user.web_url,
        )

    @staticmethod
    def _standardize_gitlab_pull_request_gql(
        gitlab_pr: dict,
        standardized_repository: StandardizedRepository,
    ) -> StandardizedPullRequest:
        """
        Converts a gql mergeRequest dict to a standardized jf pull request.
        """
        # Determine closed/merged status and build source/target short repos
        is_closed = bool(gitlab_pr['closedAt'])
        is_merged = bool(gitlab_pr['mergedAt'])
        standardized_head_repository = StandardizedShortRepository(
            id=get_id_from_gid(
                gitlab_pr['sourceProject']['id'], GitLabGidObjectMapping.PROJECT.value
            ),
            name=gitlab_pr['sourceProject']['name'],
            url=gitlab_pr['sourceProject']['webUrl'],
        )
        standardized_base_repository = StandardizedShortRepository(
            id=get_id_from_gid(
                gitlab_pr['targetProject']['id'], GitLabGidObjectMapping.PROJECT.value
            ),
            name=gitlab_pr['targetProject']['name'],
            url=gitlab_pr['targetProject']['webUrl'],
        )

        # Build out standardized commits
        standardized_short_repository: StandardizedShortRepository = standardized_repository.short()
        merge_commit_sha = gitlab_pr['mergeCommitSha']
        branch_name = gitlab_pr['sourceBranch']
        standardized_commits = []
        standardized_merge_commit = None
        for gitlab_commit in gitlab_pr['commits']['nodes']:
            standardized_commit = GitlabAdapter._standardize_gitlab_commit_gql(
                gitlab_commit,
                standardized_short_repository,
                branch_name=branch_name,
                is_merge=gitlab_commit['sha'] == merge_commit_sha,
            )
            standardized_commits.append(standardized_commit)
            if gitlab_commit['sha'] == merge_commit_sha:
                standardized_merge_commit = standardized_commit

        # Build PR comments
        standardized_comments = []
        for gitlab_note in gitlab_pr['notes']['nodes']:
            standardized_comment = GitlabAdapter._standardize_gitlab_pull_request_comment_gql(
                gitlab_note
            )
            standardized_comments.append(standardized_comment)

        # Build PR approvals
        standardized_approvals = []
        # Approvals here are essentially users with more steps
        for gitlab_approval in gitlab_pr['approvedBy']['nodes']:
            standardized_user = GitlabAdapter._standardize_gitlab_user_gql(gitlab_approval)
            standardized_approval = StandardizedPullRequestReview(
                user=standardized_user,
                foreign_id=standardized_user.id if standardized_user else '',
                review_state=PullRequestReviewState.APPROVED.name,
            )
            standardized_approvals.append(standardized_approval)

        # Build file data from diff stats
        standardized_file_data = {}
        for gitlab_file_data in gitlab_pr.get('diffStats', []):
            standardized_file_data[hash_filename(gitlab_file_data['path'])] = StandardizedFileData(
                status='',
                changes=gitlab_file_data['additions'] + gitlab_file_data['deletions'],
                additions=gitlab_file_data['additions'],
                deletions=gitlab_file_data['deletions'],
            )

        base_branch = gitlab_pr['targetBranch']
        head_branch = gitlab_pr['sourceBranch']

        return StandardizedPullRequest(
            id=int(get_id_from_gid(gitlab_pr['id'], GitLabGidObjectMapping.MERGE_REQUEST.value)),
            additions=gitlab_pr['diffStatsSummary']['additions'],
            deletions=gitlab_pr['diffStatsSummary']['deletions'],
            changed_files=gitlab_pr['diffStatsSummary']['fileCount'],
            is_closed=is_closed,
            is_merged=is_merged,
            created_at=parse_gitlab_date(gitlab_pr['createdAt']),
            updated_at=parse_gitlab_date(gitlab_pr['updatedAt']),
            merge_date=parse_gitlab_date(gitlab_pr['mergedAt']),
            closed_date=parse_gitlab_date(gitlab_pr['closedAt']),
            title=gitlab_pr['title'],
            body=gitlab_pr['description'],
            url=gitlab_pr['webUrl'],
            base_branch=base_branch,
            head_branch=head_branch,
            author=GitlabAdapter._standardize_gitlab_user_gql(  # type:ignore[arg-type]
                gitlab_pr['author']
            ),  # This will not be null, but this serialization returns `None` if nothing was passed in.
            merged_by=GitlabAdapter._standardize_gitlab_user_gql(gitlab_pr['mergeUser']),
            commits=standardized_commits,
            merge_commit=standardized_merge_commit,
            comments=standardized_comments,
            approvals=standardized_approvals,
            base_repo=standardized_base_repository,
            head_repo=standardized_head_repository,
            labels=[],  # TODO: Support labels (OJ-7202)
            files=standardized_file_data,
        )

    @staticmethod
    def _standardize_gitlab_user_gql(
        gitlab_user: Optional[dict] = None,
    ) -> Optional[StandardizedUser]:
        """
        Converts a gql user dict to a standardized jf user.
        """
        if not gitlab_user:
            return None

        return StandardizedUser(
            id=get_id_from_gid(gitlab_user['id'], GitLabGidObjectMapping.USER.value),
            login=gitlab_user['username'] or gitlab_user['publicEmail'],
            name=gitlab_user['name'],
            email=gitlab_user['publicEmail'],
            url=gitlab_user['webUrl'],
        )

    @staticmethod
    def _standardize_gitlab_commit_gql(
        gitlab_commit: dict,
        standardized_short_repo: StandardizedShortRepository,
        branch_name: Optional[str] = None,
        is_merge: Optional[bool] = False,
    ) -> StandardizedCommit:
        """
        Converts a gql commit dict to a standardized jf commit.
        """
        return StandardizedCommit(
            hash=gitlab_commit['sha'],
            url=gitlab_commit['webUrl'],
            message=gitlab_commit['message'],
            commit_date=parse_gitlab_date(gitlab_commit['committedDate']),
            author_date=parse_gitlab_date(gitlab_commit['authoredDate']),
            author=GitlabAdapter._standardize_gitlab_user_gql(gitlab_commit['author']),
            repo=standardized_short_repo,
            is_merge=bool(is_merge),
            branch_name=branch_name,
        )

    @staticmethod
    def _standardize_gitlab_pull_request_comment_gql(
        gitlab_pr_comment: dict,
    ) -> StandardizedPullRequestComment:
        """
        Converts a gql comment dict to a standardized jf comment.
        """
        return StandardizedPullRequestComment(
            user=GitlabAdapter._standardize_gitlab_user_gql(gitlab_pr_comment['author']),
            body=gitlab_pr_comment['body'],
            created_at=parse_gitlab_date(gitlab_pr_comment['createdAt']),
            system_generated=gitlab_pr_comment['system'],
        )

    def get_group_full_path_from_id(self, group_id: str) -> str:
        if group_id not in self.group_id_to_full_path:
            _, full_path, _ = self.client.get_organization_name_full_path_and_url(login=group_id)
            self.group_id_to_full_path[group_id] = full_path

        return self.group_id_to_full_path[group_id]

    def get_group_full_path_from_organization(self, org: StandardizedOrganization) -> str:
        return self.get_group_full_path_from_id(org.login)

    def get_organizations(self) -> List[StandardizedOrganization]:
        """Get the list of organizations the adapter has access to

        Returns:
            List[StandardizedOrganization]: A list of standardized organizations within this Git Instance
        """
        orgs: List[StandardizedOrganization] = []
        should_discover: bool = False

        if self.config.discover_organizations:
            if self.client.supports_get_all_organizations:
                should_discover = True
            else:
                logger.info(
                    'Discover new organizations is enabled, but this instance does not support getting all organizations. '
                    'This is because the instance is using the public gitlab.com domain and will return other public '
                    'organizations. Falling back to configured git organizations.'
                )

        if should_discover:
            try:
                # Discover Orgs
                for gql_org in self.client.get_organizations_gql():
                    group_id = get_id_from_gid(
                        gql_org['groupIdStr'], GitLabGidObjectMapping.GROUP.value
                    )
                    full_path = gql_org['fullPath']
                    self.group_id_to_full_path[group_id] = full_path
                    orgs.append(
                        StandardizedOrganization(
                            id=group_id, name=gql_org['name'], login=group_id, url=gql_org['webUrl']
                        )
                    )
            except Exception as e:
                logger.warning(
                    f':WARN: Unable to pull groups via GraphQL. Gitlab Server version {self.client.get_api_version()}. '
                    f'Falling back to api to discover organizations. Exception: {e}'
                )
                # We may have failed partially. Err on fetching all from the same source.
                orgs = []
                for api_org in self.client.get_organizations_rest_api():
                    self.group_id_to_full_path[api_org.id] = api_org.full_path
                    orgs.append(
                        StandardizedOrganization(
                            id=str(api_org.id),
                            name=api_org.name,
                            login=str(api_org.id),
                            url=api_org.web_url,
                        )
                    )
        else:
            ingestion_type = get_ingestion_type()
            for group_id in self.config.git_organizations:
                try:
                    name, full_path, url = self.client.get_organization_name_full_path_and_url(
                        login=group_id
                    )
                    self.group_id_to_full_path[group_id] = full_path
                    orgs.append(
                        StandardizedOrganization(id=group_id, name=name, login=group_id, url=url)
                    )
                except Exception as e:
                    if ingestion_type == IngestionType.AGENT:
                        response_code = getattr(e, 'response_code', '')
                        logger.warning(
                            f'Got {type(e).__name__} {response_code} when fetching data for group {group_id}'
                        )
                    else:
                        raise

        return orgs

    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        """
        Get all users in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object
            limit (int, optional): When provided, only returns this many users. Defaults to None.

        Returns:
            Generator[StandardizedUser, None, None]: A generator of StandardizedUser objects
        """
        for idx, user in enumerate(self.client.get_users(group_id=standardized_organization.login)):
            if limit and idx >= limit:
                return

            yield self._standardize_user(user)

    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedTeam, None, None]:
        """
        This function is to align with what the parent adapter class expects.
        GitLab does not have a concept of teams past groups, which we use as organizations.
        This will return an empty list, regardless of arguments.
        """
        teams: List[StandardizedTeam] = []
        yield from teams

    def get_repos(
        self,
        standardized_organization: StandardizedOrganization,
        limit: Optional[int] = None,
        only_private: bool = False,
    ) -> Generator[StandardizedRepository, None, None]:
        """Get a list of standardized repositories within a given organization. Currently uses
        the REST API endpoint. We have a GQL endpoint enabled in the client, but it's hard
        to get the full_path/name for each repo. If this becomes a performance bottleneck
        we should switch to the GQL endpoint

        Args:
            standardized_organization (StandardizedOrganization): A standardized organization
            limit (int, optional): When provided, only the given number of repos are returned
            only_private (bool): When True, only return private repos. Defaults to False.

        Returns:
            Generator[StandardizedRepository]: An iterable of standardized Repositories
        """
        for idx, client_repo in enumerate(
            self.client.get_repos(standardized_organization, only_private), start=1
        ):
            yield self._standardize_gitlab_project(
                client_repo,
                standardized_organization,
            )

            if limit and idx >= limit:
                return

    def get_repos_count(
        self, standardized_organization: StandardizedOrganization, only_private: bool = False
    ) -> int:
        return self.client.get_repos_count(standardized_organization.login, only_private)

    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the Default Branch.

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            limit (int): limit the number of commit objects we will yield
            pull_since (datetime): filter commits to be newer than this date
            pull_until (datetime): filter commits to be older than this date

        Returns:
            Generator[StandardizedCommit]: An iterable of standardized commits
        """
        default_branch_name: Optional[str] = standardized_repo.default_branch_name
        if default_branch_name:
            for j, api_commit in enumerate(
                self.client.get_commits(
                    standardized_repo,
                    since=pull_since,
                    branch_name=default_branch_name,
                ),
                start=1,
            ):
                yield self._standardize_gitlab_commit(
                    api_commit, standardized_repo, default_branch_name
                )
                if limit and j >= limit:
                    return

    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_branches: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedBranch, None, None]:
        """Function for pulling branches for a repository. By default, pull_branches will run as False,
        so we will only process the default branch. If pull_branches is true, than we will pull all
        branches in this repository

        Args:
            standardized_repo (StandardizedRepository): A standardized repo, which hold info about the default branch.
            pull_branches (bool): A boolean flag. If True, pull all branches available on Repo.
                If false, only process the default branch. Defaults to False.
            limit (int): limit the number of branch objects we will yield

        Yields:
            StandardizedBranch: A Standardized Branch Object
        """
        branch_name: Optional[str] = None
        if not pull_branches:
            if standardized_repo.default_branch_name:
                branch_name = standardized_repo.default_branch_name
            else:
                return

        branch_count = 0

        for api_branch in self.client.get_branches_for_repo(
            standardized_repo, branch_name=branch_name
        ):
            if branch := self._standardize_gitlab_branch(
                api_branch,
                standardized_repo,
            ):
                branch_count += 1
                yield branch

            if limit and branch_count >= limit:
                return

    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the included branches.
        Included branches are found by crawling across the branches pulled/available
        from get_filtered_branches

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            branches (List[StandardizedBranch]): A list of branches to pull commits from
            pull_since (datetime): A date to pull from
            pull_until (datetime): A date to pull up to
            limit (int): limit the number of commit objects we will yield

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        for branch in branches:
            for j, api_commit in enumerate(
                self.client.get_commits(
                    standardized_repo,
                    since=pull_since,
                    until=pull_until,
                    branch_name=str(branch.name),
                ),
                start=1,
            ):
                yield self._standardize_gitlab_commit(
                    api_commit, standardized_repo, str(branch.name)
                )

                if limit and j >= limit:
                    return

    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pr_pull_from_date: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        """Get all PRs, but only included the bare necesaties

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
            pr_pull_from_date: This is currently only used by the GithubAdapter. Probably won't be useful for this adapter

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        raise NotImplementedError()

    def get_pr_authors(
        self, pr_list: list[StandardizedJFAPIPullRequest]
    ) -> list[StandardizedPullRequestAuthor]:
        """
        Get the authors of a list of PRs

        This is currently NOT IMPLEMENTED for GitLab instances
        """
        return []

    def git_provider_pr_endpoint_supports_date_filtering(self) -> bool:
        """Returns a boolean on if this PR supports time window filtering.
        So far, Github DOES NOT support this (it's adapter will return False)
        but ADO does support this (it's adapter will return True)

        Returns:
            bool: A boolean on if the adapter supports time filtering when searching for PRs
        """
        return True

    def _backfill_pr_closed_at(
        self,
        standardized_repo: StandardizedRepository,
        pr_generator: Generator[Dict, None, None],
        limit: Optional[int] = None,
    ) -> Generator[Dict, None, None]:
        """
        This helper function is used after fetching prs if gql_skip_pr_closed_at is enabled via the compat config
        in the client.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pr_generator (Generator[Dict, None, None]): The generator to evaluate against
            limit (int, optional): When provided, limits returned prs. Passed from get_prs. Defaults to None.

        Returns:
            Generator[Dict, None, None]: A list of api prs.
        """
        evaluated_prs = {}
        # Evaluate the pr generator. Use limit to prevent pulling more than we want.
        for j, api_pr in enumerate(pr_generator, start=1):
            # IIDs are used for GitLab filtering here. They should always present and are always integers.
            evaluated_prs[int(api_pr['iid'])] = api_pr
            if limit and j >= limit:
                break

        # To fetch closed_at, use the api to fetch with batches of ids in query params
        project_id = standardized_repo.id
        project = self.client.client.projects.get(project_id)
        pr_keys = list(evaluated_prs.keys())

        # Fetch 25 pr iids at a time. This should prevent sending too many ids at a time via queryparams
        for pr_key_batch in batch_iterable(pr_keys, batch_size=25):
            for fetched_pr in project.mergerequests.list(iterator=True, iids=pr_key_batch):
                evaluated_prs[fetched_pr.iid]['closedAt'] = fetched_pr.closed_at

        for api_pr in evaluated_prs.values():
            yield api_pr

    def _backfill_pr_commits_committed_date(
        self,
        standardized_repo: StandardizedRepository,
        pr_generator: Generator[Dict, None, None],
        limit: Optional[int] = None,
    ) -> Generator[Dict, None, None]:
        """
        This helper function is used after fetching prs if gql_skip_commit_committed_date is enabled via the compat
        config in the client.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pr_generator (Generator[Dict, None, None]): The generator to evaluate against
            limit (int, optional): When provided, limits returned prs. Passed from get_prs. Defaults to None.

        Returns:
            Generator[Dict, None, None]: A list of api prs.
        """
        for j, api_pr in enumerate(pr_generator, start=1):
            pr_commits = self.client.get_pr_commits_rest_api(standardized_repo, api_pr)
            commit_mapping = {}
            for pr_commit in pr_commits:
                commit_mapping[pr_commit['id']] = pr_commit['committed_date']

            for gql_commit in api_pr['commits']['nodes']:
                gql_commit['committedDate'] = commit_mapping[gql_commit['sha']]

            yield api_pr

            if limit and j >= limit:
                break

    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: Optional[int] = None,
        start_cursor: Optional[Any] = None,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """Get the list of standardized Pull Requests for a Standardized Repository.
        This function makes use of the GraphQL interface provided by GitLab.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pull_files_for_pr (bool): When provided, we will pull file metadata for all PRs
            hash_files_for_prs (bool): When provided, all file metadata will be hashed for PRs
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        try:
            full_path: Optional[str] = standardized_repo.full_path
            if not full_path:
                logger.warning(
                    f':WARN: `full_path` not provided on standardized repo: {standardized_repo.name}. Skipping pulling pull requests...'
                )
                return

            pr_generator = self.client.get_prs(
                project_full_path=str(full_path),
                pull_files_for_pr=pull_files_for_pr,
                hash_files_for_pr=hash_files_for_prs,
                start_cursor=start_cursor,
                start_window=start_window,
                end_window=end_window,
            )

            if self.client.compatibility_config['gql_skip_pr_closed_at']:
                logger.info(
                    'Backfilling closed_at field for prs via api due to server GQL compatibility.'
                )
                pr_generator = self._backfill_pr_closed_at(standardized_repo, pr_generator, limit)

            if self.client.compatibility_config['gql_skip_commit_committed_date']:
                logger.info(
                    'Backfilling committed_date field for commits via api due to server GQL compatibility.'
                )
                pr_generator = self._backfill_pr_commits_committed_date(
                    standardized_repo, pr_generator, limit
                )

            for j, api_pr in enumerate(pr_generator, start=1):
                try:
                    standardized_pr = self._standardize_gitlab_pull_request_gql(
                        api_pr,
                        standardized_repo,
                    )
                    yield standardized_pr
                except (KeyError, TypeError) as e:
                    api_pr_key = None
                    if api_pr:
                        api_pr_key = api_pr.get('id')
                    logging_helper.send_to_agent_log_file(
                        f':WARN: Missing expected data for pull request key {api_pr_key}. Skipping. {e}'
                    )
                except Exception as e:
                    logging_helper.send_to_agent_log_file(
                        f'Exception encountered when attempting to standardize Pull Request. Exception: {e}',
                        level=logging.ERROR,
                    )

                if limit and j >= limit:
                    return
        except Exception as e:
            logger.warning(
                f':WARN: Unable to pull PRs for {standardized_repo.name}. Exception: {e}'
            )

    def get_users_gql(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        """
        NOTE: This function is not used in the current implementation due to issues with GraphQL
        authorization. It is here for future use.

        Get all users in a given Git Organization using GraphQL

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            Generator[StandardizedUser, None, None]: A generator of StandardizedUser objects
        """
        raise NotImplementedError(
            "This function is not currently supported due to GQL authorization issues."
        )

        for i, user in enumerate(
            self.client.get_users_gql(
                group_full_path=self.get_group_full_path_from_organization(
                    standardized_organization
                )
            )
        ):
            email: Optional[str] = None

            if public_email := user.get('publicEmail'):
                email = public_email
            elif email_conn_first := user.get('emails', {}).get('nodes'):
                email = email_conn_first[0].get('email')

            yield StandardizedUser(
                id=user['id'].split('gid://gitlab/User/')[1],
                name=user['name'],
                login=user['username'],
                email=email,
                url=user['webUrl'],
            )

            if limit and i >= limit:
                break
