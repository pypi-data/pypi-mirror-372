from datetime import datetime
from typing import Dict, Generator, List, Optional, Tuple

import requests

from jf_ingest import logging_helper
from jf_ingest.config import AzureDevopsAuthConfig, GitAuthConfig
from jf_ingest.utils import retry_for_status, retry_session

ADO_DEFAULT_API_URL = 'https://dev.azure.com'


class AzureDevopsClient:
    '''
    Similar to GithubClient and BitbucketCloudClient in that this a requests-based
    client (i.e., we're not using a specialized library).

    Makes requests to the Azure DevOps API, handling that API's specific handling
    of authentication, pagination, retries, rate limiting, etc.
    '''

    def __init__(
        self,
        git_auth_config: GitAuthConfig,
        **kwargs,
    ):
        """Wrapper class for the DevOps API endpoint.

        Args:
            git_auth_config (GithubAuthConfig): A fully fleshed out GithubAuthConfig, with the api_version set
        """
        if type(git_auth_config) is not AzureDevopsAuthConfig:
            raise Exception(
                f'Provided Auth Config for AzureDevops Clients is {type(git_auth_config)}, but type AzureDevopsAuthConfig is required'
            )
        self.base_url = git_auth_config.base_url or ADO_DEFAULT_API_URL
        self.token = git_auth_config.token
        self.session = git_auth_config.session or retry_session(**kwargs)
        self.api_version = git_auth_config.api_version
        if self.api_version:
            self.api_version = git_auth_config.api_version
            self.common_request_params = {
                'api-version': self.api_version,
            }

        # Basic authentication, using no username and the PAT as the password
        self.session.auth = ('', self.token)
        self.session.verify = True
        self.session.headers.update({'Accept': 'application/json'})

    def _get_raw_result(
        self, url: str, params: Optional[Dict] = None, ignore404: Optional[bool] = False
    ) -> Tuple[Optional[requests.Response], Optional[str]]:
        """
        Returns a tuple: (the_raw_result, continuation_token_if_applicable)
        If there are more results to be fetched, some but not all API methods will return a continuation_token.

        This function WILL raise errors (like 429s) and should be called with the retry_for_status wrapper

        Args:
            url (str): A URL to hit with a GET request.
            params (Optional[Dict], optional): Params to hit the GET call with. Defaults to None.
            ignore404 (Optional[bool], optional): If provided, 404 errors will be ignored. Defaults to False.

        Returns:
            Tuple[requests.Response, str]: Returns the response and a str that represents the continuation token
        """
        if params is None:
            params = {}
        try:
            result = self.session.get(url=url, params=dict(self.common_request_params, **params))
            result.raise_for_status()
            continuation_token = result.headers.get('x-ms-continuationtoken')
            return result, continuation_token
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404 and ignore404:
                logging_helper.send_to_agent_log_file(f'Caught a 404 for {url} - ignoring')
                return None, None
            raise

    @staticmethod
    def format_datetime_to_ado_str(dt: datetime) -> str:
        # ADO is particular about their formatting. For simplicity, format
        # everything to base Date format
        return dt.strftime('%Y-%m-%d')

    def get_json(
        self, url: str, params: Optional[Dict] = None, ignore404: Optional[bool] = False
    ) -> Tuple[Dict, Optional[str]]:
        """
        Returns a tuple: (the_json_result, continuation_token_if_applicable)
        If there are more results to be fetched, some but not all API methods will return a continuation_token

        Args:
            url (str): URL to query
            params (Optional[Dict], optional): Params to query URL with. Defaults to None.
            ignore404 (Optional[bool], optional): Boolean to mark if we should ignore any raised 404s. Defaults to False.

        Returns:
            Tuple[Dict, str]: A tuple of the raw Dict result and the continuation token
        """
        if params is None:
            params = {}

        # Make request via the _get_raw_result function, wrapped in the retry_for_status util function
        # Save results initially as a tuple so we can unpack it later, giving us cleaner type hinting
        raw_result_tuple: Tuple[Optional[requests.Response], Optional[str]] = retry_for_status(
            self._get_raw_result, url=url, params=params, ignore404=ignore404
        )
        result, continuation_token = raw_result_tuple
        if result:
            return result.json(), continuation_token
        else:
            return {}, None

    def get_single_object(
        self, url: str, params: Optional[Dict] = None, ignore404: Optional[bool] = False
    ) -> Dict:
        """Get a single object from the ADO API

        Args:
            url (str): URL to query
            params (Optional[Dict], optional): Params to query URL with. Defaults to None.
            ignore404 (Optional[bool], optional): Boolean to mark if we should ignore any raised 404s. Defaults to False.

        Returns:
            Dict: a single JSON result returned from the API
        """
        if params is None:
            params = {}
        result, _ = self.get_json(url, params, ignore404)
        return result

    def get_single_page(
        self,
        url: str,
        params: Optional[Dict] = None,
        ignore404: bool = False,
        result_container: str = 'value',
    ) -> List[Dict]:
        """
        For API methods that do NOT implement pagination -- all results come back
        in a single page

        Args:
            url (str): URL to query
            params (Optional[Dict], optional): Params to query URL with. Defaults to None.
            ignore404 (Optional[bool], optional): Boolean to mark if we should ignore any raised 404s. Defaults to False.
            result_container (Optional[str], optional): A string indicating the key within the returned dictionary that holds the list of results. Defaults to 'value'.

        Returns:
            List[Dict]: A list of dictionary objects returned from the API
        """
        if params is None:
            params = {}
        page: Dict[str, List] = self.get_json(url, params, ignore404)[0]
        return page.get(result_container, [])

    def get_all_pages_using_skip_and_top(
        self,
        url: str,
        params: Optional[Dict] = None,
        ignore404: bool = False,
        result_container: str = 'value',
        skip: int = 0,
        top: int = 100,
    ) -> Generator[Dict, None, None]:
        """For API methods that implement resultset pagination using $skip and $top. To paginate,
        use $top=100 and $skip=0, then $skip=100, then $skip=200, etc.

        Args:
            url (str): URL to query
            params (Optional[Dict], optional): Params to query URL with. Defaults to None.
            ignore404 (Optional[bool], optional): Boolean to mark if we should ignore any raised 404s. Defaults to False.
            result_container (Optional[str], optional): A string indicating the key within the returned dictionary that holds the list of results. Defaults to 'value'.
            skip (Optional[int], optional): tells the API to skip this many matching entities. Defaults to 0.
            top (Optional[int], optional): tells the API to return at most this many matching entities. Defaults to 100.

        Yields:
            Generator[Dict, None, None]: Yields a dictionary for each result
        """
        if params is None:
            params = {}
        while True:
            params.update({'$skip': skip, '$top': top})
            page, continuation_token = self.get_json(url, params, ignore404)
            assert not continuation_token, (
                "Inside of get_all_pages_using_skip_and_top, but a continuation_token was included in the response; "
                "do you mean to use get_all_pages_using_pagination_token instead?"
            )
            if not page or result_container not in page:
                return
            for value in page[result_container]:
                yield value
            if 'count' in page and page['count'] == top:
                skip += top
            # NOTE: Fot the Diffs endpoint, the "count" is obscured as this
            # changeCounts values and we have to handle it differently
            elif 'changeCounts' in page:
                # Get TOTAL count of changed files (this can be bigger than page size (top))
                count_from_change_counts = sum(page['changeCounts'].values())
                # skip ahead a page
                skip += top
                # If we've skipped a page ahead and we're still below
                # the total, return
                #
                # If we've skipped a page ahead and we're equal to or greater than
                # the total files, return
                if count_from_change_counts > skip:
                    continue
                else:
                    return
            else:
                return

    def get_all_pages_using_pagination_token(
        self,
        url: str,
        params: Optional[Dict] = None,
        ignore404: Optional[bool] = False,
        result_container: Optional[str] = 'value',
    ) -> Generator[Dict, None, None]:
        """For API methods that implement resultset pagination using a continuation token
        To paginate, we issue subsequent requests using the continuation_token returned

        Args:
            url (str): URL to query
            params (Optional[Dict], optional): Params to query URL with. Defaults to None.
            ignore404 (Optional[bool], optional): Boolean to mark if we should ignore any raised 404s. Defaults to False.
            result_container (Optional[str], optional): A string indicating the key within the returned dictionary that ho

        Yields:
            Generator[Dict, None, None]: Yields a dictionary for each result
        """
        if params is None:
            params = {}
        while True:
            page, continuation_token = self.get_json(url, params, ignore404)
            if not page or result_container not in page:
                return
            for value in page[result_container]:
                yield value
            if continuation_token:
                params.update({'continuationToken': continuation_token})
            else:
                return

    def get_all_repos(self, org_name: str) -> List[Dict]:
        """Get all repositories from the ADO API
        Somehow, this API endpoint doesn't support paging? The only option is to get all the repositories all at once
        https://learn.microsoft.com/en-us/rest/api/azure/devops/git/repositories/list?view=azure-devops-rest-7.1&tabs=HTTP

        Args:
            org_name (str): The organization to query for

        Returns:
            List[Dict]: A list of repo dictionaries from ADO
        """
        url = f'{self.base_url}/{org_name}/_apis/git/repositories?api-version={self.api_version}'
        return self.get_single_page(url)

    def get_repos_count(self, org_name: str) -> int:
        """Get the count of repositories from the ADO API

        Args:
            org_name (str): The organization to query for

        Returns:
            int: The count of repositories
        """
        url = f'{self.base_url}/{org_name}/_apis/git/repositories?api-version={self.api_version}'
        count = self.get_single_object(url).get('count', 0)
        return int(count)

    def get_graph_users(self, org_name: str) -> Generator[Dict, None, None]:
        """A Generator for getting user data from the ADO API

        Args:
            org_name (str): The org to query for

        Yields:
            Generator[Dict, None, None]: A raw User dictionary object
        """
        url = f"{self.base_url}/{org_name}/_apis/graph/users"
        return self.get_all_pages_using_pagination_token(
            # XXX: This API is not yet GA? Hopefully down the road we'll be able to do away
            # with the URL and api-version overrides
            url.replace('dev.azure.com', 'vssps.dev.azure.com'),
            params={'api-version': '7.0-preview.1'} if self.api_version == '7.0' else None,
        )

    def get_teams(self, org_name: str) -> Generator[Dict, None, None]:
        """A Generator for getting team data from the ADO API

        Args:
            org_name (str): The org to query for

        Yields:
            Generator[Dict, None, None]: A raw Team dictionary object
        """
        url = f"{self.base_url}/{org_name}/_apis/graph/groups"
        return self.get_all_pages_using_pagination_token(
            # XXX: This API is not yet GA? Hopefully down the road we'll be able to do away
            # with the URL and api-version overrides
            url.replace('dev.azure.com', 'vssps.dev.azure.com'),
            params={'api-version': '7.0-preview.1'} if self.api_version == '7.0' else None,
        )

    def get_team_users(self, org_name: str, team_descriptor: str) -> List[Dict]:
        """Get a list of users for a given team

        Args:
            org_name (str): An organization name
            team_id (str): A team ID

        Returns:
            List[Dict]: A list of members for a team
        """
        url = f"{self.base_url}/{org_name}/_apis/Graph/Memberships/{team_descriptor}"
        params = {'direction': 'down'}
        if self.api_version == '7.0':
            params['api-version'] = '7.0-preview.1'
        team_memberships = self.get_single_page(
            # XXX: This API is not yet GA? Hopefully down the road we'll be able to do away
            # with the URL and api-version overrides
            url.replace('dev.azure.com', 'vssps.dev.azure.com'),
            params=params,
        )
        return [
            self.get_json(
                # XXX: This API is not yet GA? Hopefully down the road we'll be able to do away
                # with the api-version override
                team_membership['_links']['member']['href'],
                params={'api-version': '7.0-preview.1'} if self.api_version == '7.0' else None,
            )[0]
            for team_membership in team_memberships
        ]

    def get_commits(
        self,
        org_name: str,
        project_name: str,
        repo_id: str,
        branch_name: Optional[str],
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> Generator[Dict, None, None]:
        """Get commits for a branch (within a repo, within a project, and within an Org), with the ability to filter in between dates

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A Repo ID
            branch_name (str): A Branch Name
            from_date (Optional[datetime], optional): search will only return items created AFTER this date. Defaults to None.
            to_date (Optional[datetime], optional): search will only return items created BEFORE this date. Defaults to None.

        Yields:
            Generator[Dict, None, None]: A raw Commit Dictionary
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/commits?api-version={self.api_version}"
        params = {
            'searchCriteria.itemVersion.version': branch_name,
            'searchCriteria.itemVersion.versionType': 'branch',
        }
        if from_date:
            # These take hyper specific formatting, not general ADO format: https://learn.microsoft.com/en-us/rest/api/azure/devops/git/commits/get-commits?view=azure-devops-rest-7.1&tabs=HTTP
            params.update({'searchCriteria.fromDate': from_date.strftime('%m/%d/%Y %H:%M:%S %p')})
        if to_date:
            # These take hyper specific formatting, not general ADO format: https://learn.microsoft.com/en-us/rest/api/azure/devops/git/commits/get-commits?view=azure-devops-rest-7.1&tabs=HTTP
            params.update({'searchCriteria.toDate': to_date.strftime('%m/%d/%Y %H:%M:%S %p')})

        return self.get_all_pages_using_skip_and_top(url, params)

    def get_commit(self, org_name: str, project_name: str, repo_id: str, commit_id: str) -> Dict:
        """Get a single commit

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A Repo ID
            branch_name (str): A Branch Name
            commit_id (str): a commit ID to search for

        Returns:
            Dict: A raw Commit Dictionary
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/commits/{commit_id}?api-version={self.api_version}"
        return self.get_single_object(url)

    def get_branches(
        self,
        org_name: str,
        project_name: str,
        repo_id: str,
        filter_startswith: Optional[str] = None,
    ) -> Generator[Dict, None, None]:
        """Get a generator of branches

        Args:
            org_name (str): An org name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A repository ID
            filter_startswith (str, optional): A string to filter branches with. Defaults to None.

        Yields:
            Generator[Dict, None, None]: A raw branch in the form of a dictionary
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/refs?api-version={self.api_version}"
        if filter_startswith:
            return self.get_all_pages_using_pagination_token(
                url, params={'filter': f'heads/{filter_startswith}'}
            )
        else:
            return self.get_all_pages_using_pagination_token(url)

    def get_pull_request_iterations(
        self, org_name: str, project_name: str, repo_id: str, pr_id: int
    ) -> List[Dict]:
        url = f'{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/iterations?api-version={self.api_version}'
        return self.get_single_page(url)

    def get_pull_request_labels(
        self, org_name: str, project_name: str, repo_id: str, pr_id: int
    ) -> List[Dict]:
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/labels?api-version={self.api_version}"
        return self.get_single_page(url)

    def get_pull_request_changes_counts(
        self, org_name: str, repo_id: str, base_sha: str, target_sha: str
    ) -> Dict:
        url = f"{self.base_url}/{org_name}/_apis/git/repositories/{repo_id}/diffs/commits?api-version={self.api_version}"
        params = {
            'baseVersion': base_sha,
            'baseVersionType': 'commit',
            'targetVersion': target_sha,
            'targetVersionType': 'commit',
        }
        change_count_results: Dict[str, Dict] = self.get_json(url, params)[0]
        return change_count_results['changeCounts']

    def get_pull_request_diff(
        self, org_name: str, repo_id: str, base_sha: str, target_sha: str
    ) -> Generator[Dict, None, None]:
        url = f"{self.base_url}/{org_name}/_apis/git/repositories/{repo_id}/diffs/commits?api-version={self.api_version}"
        params = {
            'baseVersion': base_sha,
            'baseVersionType': 'commit',
            'targetVersion': target_sha,
            'targetVersionType': 'commit',
        }
        return self.get_all_pages_using_skip_and_top(url, params, result_container='changes')

    def get_pull_requests(
        self,
        org_name: str,
        project_name: str,
        repo_id: str,
        start_window: Optional[datetime],
        end_window: Optional[datetime],
        status: str = 'active',
        filter_by: str = 'created',
    ) -> Generator[Dict, None, None]:
        """Generate pull request dictionaries, pulled from the ADO API

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A repository ID
            start_cursor (int): The cursor of where in pagination we should start. Defaults to 0.

        Yields:
            Generator[Dict, None, None]: A raw pull request dictionary
        """

        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullrequests?api-version={self.api_version}&searchCriteria.status={status}"
        if start_window or end_window:
            url += f'&searchCriteria.queryTimeRangeType={filter_by}'
            if start_window:
                url += f'&searchCriteria.minTime={self.format_datetime_to_ado_str(start_window)}'
            if end_window:
                url += f'&searchCriteria.maxTime={self.format_datetime_to_ado_str(end_window)}'
        return self.get_all_pages_using_skip_and_top(url)

    def get_pr_comment_threads(
        self, org_name: str, project_name: str, repo_id: str, pr_id: int
    ) -> List[Dict]:
        """Gets a list of PR Comments for a Pull Request

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A repository ID
            pr_id (int): A pull request ID (pull request Number)

        Returns:
            List[Dict]: A list of comment objects for a PR
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/threads?api-version={self.api_version}"
        return self.get_single_page(url)

    def get_pr_commits(
        self, org_name: str, project_name: str, repo_id: str, pr_id: int
    ) -> Generator[Dict, None, None]:
        """Get a list of all commits associated with a Pull Request

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A repository ID
            pr_id (int): A pull request ID (pull request Number)

        Yields:
            Generator[Dict, None, None]: A commit object associated with the PR
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/commits?api-version={self.api_version}"
        return self.get_all_pages_using_pagination_token(url)

    def get_pr_labels(
        self, org_name: str, project_name: str, repo_id: str, pr_id: int
    ) -> List[Dict]:
        """Get a list of PR labels for a specific PR

        Args:
            org_name (str): An organization name
            project_name (str): A Project name. A project name is extracted from the repo URL. See _project_name_from_repo
            repo_id (str): A repository ID
            pr_id (int): A pull request ID (pull request Number)

        Returns:
            List[Dict]: A list of label objects for a PR
        """
        url = f"{self.base_url}/{org_name}/{project_name}/_apis/git/repositories/{repo_id}/pullRequests/{pr_id}/labels?api-version={self.api_version}"
        return self.get_single_page(url)

    def get_diffs_between_shas(
        self, org_name: str, repo_id: str, base_sha: str, target_sha: str
    ) -> List[Dict]:
        """Derive the additions, deletions, and changed_files between two shas (commits). It does so by
        using the "diffs" API endpoint:

        https://learn.microsoft.com/en-us/rest/api/azure/devops/git/diffs/get?view=azure-devops-rest-7.1&tabs=HTTP

        THIS FUNCTION IS USED TO RECONSTRUCT ADDITIONS/DELETIONS/CHANGED FOR A PULL REQUEST!

        Unfortunately the ADO API doesn't provide any way to get the LOC additions/deletions -- they're
        not returned as attributes of a PR, or of a commit, nor do they come back in the response from
        the "diffs" endpoint.

        So all we can get is the number of changed files. We get this by calling the "diffs" endpoint,
        comparing the tip of the PR's branch with the base branch.

        Args:
            org_name (str): An organization name
            repo_id (str): A repository that contains the base and target_shas
            base_sha (str): A base sha to compare with
            target_sha (str): A target sha to compare to

        Returns:
            List[Dict]: A list of differences, by file and action. See link to API documenation (in description) for more
        """
        url = f"{self.base_url}/{org_name}/_apis/git/repositories/{repo_id}/diffs/commits?api-version={self.api_version}"
        params = {
            'baseVersion': base_sha,
            'baseVersionType': 'commit',
            'targetVersion': target_sha,
            'targetVersionType': 'commit',
        }
        return self.get_single_page(url, params, result_container='changes')
