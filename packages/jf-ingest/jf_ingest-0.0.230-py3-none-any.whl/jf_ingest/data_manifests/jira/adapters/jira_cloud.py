import json
import logging
import time
import traceback
import zoneinfo
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Optional, Union

from jira import JIRAError

from jf_ingest.config import JiraDownloadConfig
from jf_ingest.data_manifests.jira.adapters.manifest_adapter import ManifestAdapter
from jf_ingest.data_manifests.manifest_base import ManifestSource
from jf_ingest.jf_jira import get_jira_connection
from jf_ingest.jf_jira.downloaders import search_users
from jf_ingest.utils import get_wait_time, retry_for_status

logger = logging.getLogger(__name__)


@dataclass
class JiraCloudManifestAdapter(ManifestAdapter):
    '''
    Adapter for retrieving information from all remote Jira sources
    '''

    def __init__(
        self,
        config: JiraDownloadConfig,
        project_keys_to_classification_type: Union[
            dict[str, str], MappingProxyType
        ] = MappingProxyType({}),
    ):
        # Super class fields
        super().__init__(
            config=config,
            manifest_source=ManifestSource.remote,
            project_keys_to_classification_type=project_keys_to_classification_type,
        )
        self.jira_connection = get_jira_connection(config=config)

        # Rip off trailing slash since all urls depend on that
        self.jira_endpoint = (
            str(self.config.url)[:-1] if str(self.config.url).endswith('/') else self.config.url
        )

        self._boards_cache: list = []
        self._projects_cache: list = []

        # Set up caches
        self._get_all_boards()
        self._get_all_projects()

    def get_users_count(self) -> int:
        # Users are a special case where their page results aren't formatted the same as
        # other API page results. Special, internal function to handle this
        def _get_user_count_from_pages(url_path: str, page_size: int = 50) -> int:
            curr = 0
            user_count = 0
            while True:
                page = retry_for_status(
                    self.jira_connection._get_json,
                    url_path,
                    {**{'startAt': curr, "maxResults": page_size}},
                )
                page_count = len(page)
                user_count += page_count
                curr += page_size

                if page_count == 0:
                    break
            return user_count

        # Jira Cloud
        if self.config.gdpr_active:
            return _get_user_count_from_pages(url_path='users/search')
        # Jira Server
        else:
            return len(
                search_users(
                    jira_connection=self.jira_connection,
                    gdpr_active=bool(self.config.gdpr_active),
                    search_users_by_letter_email_domain=self.config.search_users_by_letter_email_domain,
                )
            )

    def get_fields_count(self) -> int:
        # Lazy loading paranoia, we might not need to do this for loop
        return len(retry_for_status(self.jira_connection.fields))

    def get_resolutions_count(self) -> int:
        # Lazy loading paranoia, we might not need to do this for loops
        try:
            return len(retry_for_status(self.jira_connection.resolutions))
        except Exception as e:
            logger.error(f"Could not get resolutions count for {self.config}, got {e}")
            return 0

    def get_issue_types_count(self) -> int:
        # Lazy loading paranoia, we might not need to do this for loop
        return len(retry_for_status(self.jira_connection.issue_types))

    def get_issue_link_types_count(self) -> int:
        return len(retry_for_status(self.jira_connection.issue_link_types))

    def get_priorities_count(self) -> int:
        return len(retry_for_status(self.jira_connection.priorities))

    def get_boards_count(self) -> int:
        return len(retry_for_status(self._get_all_boards))

    def get_project_versions_count(self) -> int:
        total_project_versions = 0
        retries = 0
        max_retries = 5
        constant_sleep = 5
        for project in self._get_all_projects():
            done = False
            while not done:
                try:
                    total_project_versions += self._get_raw_result(
                        url=f'{self.jira_endpoint}/rest/api/latest/project/{project["id"]}/version?startAt=0&maxResults=0&state=future,active,closed'
                    )['total']
                    retries = 0
                    done = True
                except Exception as e:
                    if (
                        hasattr(e, 'status_code')
                        and e.status_code == 429
                        and retries <= max_retries
                    ):
                        sleep_secs = get_wait_time(e, retries)
                        logger.info(
                            f'Caught JIRAError with a {e.status_code} return code during get_project_versions_count. '
                            f'Hopefully transient; sleeping for {sleep_secs} secs then may retry ({retries} of {max_retries}).'
                        )
                        time.sleep(sleep_secs + (constant_sleep * retries))
                        retries += 1
                    else:
                        logger.error(
                            f"Could not recover from error getting jira projects for manifests, got {e}"
                        )
                        raise

        return total_project_versions

    def _get_all_projects(self) -> list[dict]:
        if not self._projects_cache:
            if self.config.gdpr_active:
                self._projects_cache = [
                    project
                    for project in self._page_get_results(
                        url=f'{self.jira_endpoint}/rest/api/latest/project/search?startAt=%s&maxResults=500&status=live'
                    )
                    if not project.get('archived', False) and not project['isPrivate']
                ]
            else:
                self._projects_cache = [
                    project
                    for project in self._get_raw_result(
                        url=f'{self.jira_endpoint}/rest/api/latest/project?includedArchived=True'
                    )
                ]

        return self._projects_cache

    def get_project_data_dicts(self) -> list[dict]:
        return [
            {"key": project['key'], "id": project['id']} for project in self._get_all_projects()
        ]

    def get_project_versions_count_for_project(self, project_id: int) -> int:
        return (
            self._get_raw_result(
                url=f'{self.jira_endpoint}/rest/api/latest/project/{project_id}/version?startAt=0&maxResults=0&state=future,active,closed'
            )['total']
            or 0
        )

    def get_issues_count(self) -> int:
        # JCR 072123 Since we're using JiraIssueData, we need to check `download_all_json`, since this
        # determines whether we get _all_ issue data or just data from the pull_from date.
        #
        # See: `download_all_issue_metadata`
        pull_from = (
            '0' if self.config.full_redownload else self.config.pull_from.strftime('%Y-%m-%d')
        )

        # Query for all issues via JQL, but ask for 0 results.
        # Meta data is returned that will give us the total number of
        # (unpulled) results
        result = self._get_jql_search(jql_search=f"updatedDate > {pull_from}", max_results=0)
        return result['total'] or 0

    def get_board_ids(self, project_id: int):
        result = self._get_raw_result(
            url=f'{self.jira_endpoint}/rest/agile/1.0/board?projectKeyOrId={project_id}&startAt=0&maxResults=100'
        )
        return [value['id'] for value in result['values']]

    def _get_all_boards(self):
        if not self._boards_cache:
            self._boards_cache = [
                board
                for board in self._page_get_results(
                    url=f'{self.jira_endpoint}/rest/agile/1.0/board?startAt=%s&maxResults=100'
                )
            ]

        return self._boards_cache

    def test_basic_auth_for_project(self, project_id: int) -> bool:
        # Doing a basic query for issues is the best way to test auth.
        # Catch and error, if it happens, and bubble up more specific error
        try:
            self.get_issues_count_for_project(project_id=project_id)
            return True
        except JIRAError:
            return False
        except Exception:
            # This is unexpected behavior and it should never happen, log the error
            # before returning
            logger.error(
                'Unusual exception encountered when testing auth. '
                f'JIRAError was expected but the following error was raised: {traceback.format_exc()}'
            )
            return False

    def get_issues_count_for_project(self, project_id: int) -> int:
        # JCR 072123 Since we're using JiraIssueData, we need to check `download_all_json`, since this
        # determines whether we get _all_ issue data or just data from the pull_from date.
        #
        # See: `download_all_issue_metadata`
        pull_from = (
            '0' if self.config.full_redownload else self.config.pull_from.strftime('%Y-%m-%d')
        )

        # Query for all issues via JQL, but ask for 0 results.
        # Meta data is returned that will give us the total number of
        # (unpulled) results
        return (
            self._get_jql_search(
                jql_search=f"project = {project_id} AND updatedDate > {pull_from}",
                max_results=0,
            )['total']
            or 0
        )

    # I believe that there should be a one to one relationship with
    # Jira Issues and Jira Issue Data...
    def get_issues_data_count_for_project(self, project_id: int) -> int:
        return self.get_issues_count_for_project(project_id=project_id)

    def _get_jql_search(self, jql_search: str, max_results: int = 0):
        retries = 0
        max_retries = 5
        constant_sleep = 5
        while True:
            try:
                return retry_for_status(
                    self.jira_connection._get_json,
                    'search',
                    {'jql': jql_search, "maxResults": max_results},
                )
            except Exception as e:
                if hasattr(e, 'status_code') and e.status_code == 429 and retries <= max_retries:
                    sleep_secs = get_wait_time(e, retries)
                    logger.info(
                        f'Caught JIRAError with a {e.status_code} return code during jira_connection._get_json. '
                        f'Hopefully transient; sleeping for {sleep_secs} secs then may retry ({retries} of {max_retries}).'
                    )
                    time.sleep(sleep_secs + (constant_sleep * retries))
                    retries += 1
                else:
                    logger.error(
                        f"Could not recover from error getting jira projects for manifests, got {e}"
                    )
                    raise

    def _page_get_results(self, url: str):
        start_at = 0
        while True:
            page_result = self._get_raw_result(url % start_at)
            for value in page_result['values']:
                yield value

            if page_result['isLast']:
                break
            else:
                start_at += len(page_result['values'])

    def _get_raw_result(self, url) -> dict:
        response = retry_for_status(self.jira_connection._session.get, url)
        response.raise_for_status()
        json_str = response.content.decode()
        return json.loads(json_str) or {}

    def get_last_updated_for_project(self, project_id: int) -> Optional[datetime]:
        try:
            most_recent_issue_from_api: dict = self._get_jql_search(
                jql_search=f"project = {project_id} ORDER BY updated",
                max_results=1,
            )['issues'][0]
            # Example returned str: '2023-05-15T14:04:19.376-0400'
            most_recent_updated_date_str = most_recent_issue_from_api['fields']['updated']
            last_updated_datetime = datetime.strptime(
                most_recent_updated_date_str, '%Y-%m-%dT%H:%M:%S.%f%z'
            )
            # Normalize to utc
            return last_updated_datetime.astimezone(tz=zoneinfo.ZoneInfo('UTC'))
        except Exception as e:
            logger.error(
                f"Could not fetch latest issue updated date in project {project_id}, got: {e}"
            )
            return None

    """
    NOTE: DEPRECATED FUNCTION
    This function takes a long time to process and we currently do not use sprint counts for anything.
    I have made the decision to deprecate it, but there is no standard decorator for deprecated functions in python.
    Instead, I have removed this function from the parent abstract class and commented it out.
    I have opted to comment it out because it's a non trivial function, and if we want sprint counts back
    sometime in the future, it'd be nice to have this to work off of
    -Gavin
    
    NOTE: If we do bring this back, we must add retry logic with exponential back off logic to get around 429 errors!
    
    def get_sprints_count(self) -> int:
        # Leverage the jira_connections _session field to get an authenticated session
        # Get all boards with above query, get all sprints with this query: https://docs.atlassian.com/jira-software/REST/7.3.1/?#agile/1.0/board/{boardId}/sprin

        def _get_sprints_for_board(board_id: int):
            total_sprints_for_board = 0
            try:
                total_sprints_for_board += len(
                    [
                        sprint
                        for sprint in self._page_get_results(
                            url=f'{self.jira_endpoint}/rest/agile/1.0/board/{board_id}/sprint?startAt=%s&maxResults=100'
                        )
                    ]
                )
            except JIRAError as e:
                # JIRA returns 500 errors for various reasons: board is
                # misconfigured; "failed to execute search"; etc.  Just
                # skip and move on
                if e.status_code == 500:
                    logger.debug(f"Couldn't get sprints for {self.instance} board {board_id}")
                elif e.status_code == 400:
                    logger.debug(
                        f"For {self.instance}, board {board_id} doesn't support sprints -- skipping"
                    )
                else:
                    raise

            return total_sprints_for_board

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(_get_sprints_for_board, board["id"])
                for board in self._get_all_boards()
            ]

            return sum([future.result() for future in futures if future])
    """
