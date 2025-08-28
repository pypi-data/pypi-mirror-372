import json
import logging
import textwrap
import time
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple, Union, cast

import jwt
import requests
from dateutil import parser
from requests.utils import default_user_agent

from jf_ingest.config import GitAuthConfig, GithubAuthConfig
from jf_ingest.constants import Constants
from jf_ingest.graphql_utils import (
    GQL_PAGE_INFO_BLOCK,
    GQLRateLimit,
    GqlRateLimitedExceptionInner,
    gql_format_to_datetime,
)
from jf_ingest.jf_git.exceptions import (
    GitAuthenticationException,
    GqlRateLimitExceededException,
)
from jf_ingest.utils import (
    DEFAULT_HTTP_CODES_TO_RETRY_ON,
    batch_iterable,
    hash_filename,
    retry_for_status,
    retry_session,
)

logger = logging.getLogger(__name__)

GIT_DEFAULT_API_ENDPOINT = 'https://api.github.com'

GQL_RATE_LIMIT_QUERY_BLOCK = "rateLimit {remaining, resetAt}"

GITHUB_STATUSES_TO_RETRY_ON = tuple(list(DEFAULT_HTTP_CODES_TO_RETRY_ON) + [403])


def parse_date(dt):
    if dt is None:
        return None
    return parser.parse(dt)


class GitHubGQLNotFoundError(Exception):
    def __init__(self, error_response: list[dict]):
        super().__init__(f'GitHub GraphQL not found error: {error_response}')
        self.error_response = error_response or []


class GithubClient:
    # This uses GQL to hit the Github API!

    GITHUB_GQL_USER_FRAGMENT = "... on User {login, id: databaseId, email, name, url}"

    # NOTE: On the author block here, we have a type GitActor
    # We cannot always get the email from the nested user object,
    # so pull whatever email we can from the gitActor top level object.
    # (we can't get the email from the user object bc of variable privacy configuration)
    GITHUB_GQL_COMMIT_FRAGMENT = f"""
        ... on Commit {{
            sha: oid
            url
            author {{
                ... on GitActor {{
                    email
                    name
                    user {{ id: databaseId, login }}
                }}
            }}
            message
            committedDate
            authoredDate
            parents {{totalCount}}
        }}
    """
    GITHUB_GQL_SHORT_REPO_FRAGMENT = "... on Repository {name, id:databaseId, url}"

    # The PR query is HUGE, we shouldn't query more than about 25 at a time
    MAX_PAGE_SIZE_FOR_PR_QUERY = 25

    def __init__(
        self,
        github_auth_config: GitAuthConfig,
        **kwargs,
    ):
        """This is a wrapper class for interacting with the Github GQL endpoint. It supports
        both cloud and enterprise. It works by either accepting a provided token or by using
        the other args to set up JWT authentication (see: https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/)

        Args:
            token (str, optional): An optional authentication token. If not provided we will use the other args to get a JWT token. See GithubClient._get_app_access_token. Defaults to None.
            installation_id (str, optional): A client provided installation ID, used for JWT authentication. Defaults to None.
            app_id (str, optional): A client provided App Id, used for JWT authentication. Defaults to None.
            private_key (str, optional): A user provided private key, used for JWT authentication. Defaults to None.
            base_url (str, optional): An optional base url, used by Github Enterprise customers. Defaults to None.
            verify (bool, optional): Session arg. Defaults to True.
            session (requests.Session, optional): An optional session to pass this client, if you've already set up an authenticated session. Defaults to None.
            company_slug (str, optional): An optional str giving this class context what company this client is for. Defaults to None.
        """

        self.company_slug = github_auth_config.company_slug
        self.gql_base_url = self.get_github_gql_base_url(base_url=github_auth_config.base_url)
        # We need to hit the REST API for some API calls, see get_organization_by_name and _get_app_access_token
        self.rest_api_url = github_auth_config.base_url or GIT_DEFAULT_API_ENDPOINT

        # Create the user fragment based on the provider being GHE or GHC
        if (
            isinstance(github_auth_config.base_url, str)
            and GIT_DEFAULT_API_ENDPOINT not in github_auth_config.base_url
        ):
            provider_is_ghe = True
        else:
            provider_is_ghe = False

        self.github_gql_actor_fragment = self.get_github_gql_actor_fragment(provider_is_ghe)

        if github_token := github_auth_config.token:
            self.token = github_token
            self.token_expiration: Optional[datetime] = None
            self.uses_jwt = False
        else:
            if type(github_auth_config) == GithubAuthConfig:
                self.installation_id = github_auth_config.installation_id
                self.app_id = github_auth_config.app_id
                self.private_key = github_auth_config.private_key
                self.token, self.token_expiration = self._get_app_access_token()
                self.uses_jwt = True
            else:
                raise Exception(
                    f'Unknown Auth Config provided to GithubClient. GitAuthConfig type is expected to be a GithubAuthConfig type'
                )

        self.session = github_auth_config.session or retry_session(**kwargs)
        self.session.verify = True
        self.session.headers.update(
            {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github+json',
                'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
            }
        )

    @staticmethod
    def datetime_to_gql_str_format(_datetime: datetime) -> str:
        return _datetime.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def get_github_gql_base_url(base_url: Optional[str]) -> str:
        # the URL for GQL things is different from what we need to get a token
        if base_url and 'api/v3' in base_url:
            # Github server clients provide an API with a trailing '/api/v3'
            # replace this with the graphql endpoint
            return base_url.replace('api/v3', 'api/graphql')
        else:
            return f'{base_url or GIT_DEFAULT_API_ENDPOINT}/graphql'

    @staticmethod
    def get_github_gql_actor_fragment(is_ghe: bool) -> str:
        # Need to make a second, special actor fragment to make sure we grab
        # the proper ID from either a bot, User or (for GHC) Mannequin
        # NOTE: This could be done in a more elegant way, but using a conditional
        # within the GQL query f-string will cause formatting issues
        if is_ghe:
            return """
                ... on Actor
                    {
                        login
                        ... on User { id: databaseId, email, name }
                        ... on Bot { id: databaseId}
                    }
            """
        else:
            return """
                ... on Actor
                    {
                        login
                        ... on User { id: databaseId, email, name }
                        ... on Bot { id: databaseId}
                        ... on Mannequin { id: databaseId, email, name}
                    }
            """

    @staticmethod
    def create_jwt_token(app_id, private_key):
        now = int(time.time()) - 60
        payload = {"iat": now, "exp": now + 600, "iss": app_id}
        jwt_token = jwt.encode(payload, key=private_key, algorithm="RS256")
        return jwt_token

    def get_gql_rate_limit(self) -> GQLRateLimit:
        """Attempt to pull the current rate limit information from GQL
        NOTE: Getting the rate limit info is never affected by the current rate limit

        Args:
            session (Session): A valid session connecting us to the GQL API
            base_url (str): The base URL we are hitting

        Returns:
            dict: A dictionary object containing rate limit information (remaing and resetAt)
        """
        query_body = f"{{{GQL_RATE_LIMIT_QUERY_BLOCK}}}"
        # NOTE: DO NOT CALL get_raw_gql_result TO GET THE RESULTS HERE! IT'S A RECURSIVE TRAP
        response: requests.Response = retry_for_status(
            self.session.post, url=self.gql_base_url, json={'query': query_body}
        )
        response.raise_for_status()
        json_str = response.content.decode()
        raw_data: dict = json.loads(json_str)['data']['rateLimit']
        reset_at = cast(
            datetime, gql_format_to_datetime(raw_data['resetAt'])
        )  # resetAt is always going to be present
        logger.info('GQL rate limit info', extra=raw_data)
        return GQLRateLimit(remaining=int(raw_data['remaining']), reset_at=reset_at)

    def get_raw_result(self, query_body: str, max_attempts: int = 7) -> Dict:
        """Gets the raw results from a Graphql Query.

        Args:
            query_body (str): A query body to hit GQL with
            max_attempts (int, optional): The number of retries we should make when we specifically run into GQL Rate limiting. This value is important if the GQL endpoint doesn't give us (or gives us a malformed) rate limit header. Defaults to 7.

        Raises:
            GqlRateLimitExceededException: A custom exception if we run into GQL rate limiting and we run out of attempts (based on max_attempts)
            Exception: Any other random exception we encounter, although the big rate limiting use cases are generally covered

        Returns:
            dict: A raw dictionary result from GQL
        """
        attempt_number = 1
        while True:
            try:
                # 2024-11-08, jcr: Retry logic is handled by this loop; retry_for_status
                # should NOT be used here, otherwise it can cause excessive retries and
                # improper handling of rate limiting.
                response: requests.Response = self.session.post(
                    url=self.gql_base_url, json={'query': query_body}
                )
                response.raise_for_status()
                json_str = response.content.decode()
                json_data: Dict = json.loads(json_str)
                if 'errors' in json_data:
                    error_list: List[Dict] = json_data['errors']
                    if len(error_list) == 1:
                        error_dict = error_list[0]
                        error_type = error_dict.get('type', '')
                        if error_type == 'RATE_LIMITED':
                            logger.info(
                                'Rate limit hit in GQL, dumping headers',
                                extra={
                                    'x-ratelimit-limit': response.headers.get('x-ratelimit-limit'),
                                    'x-ratelimit-remaining': response.headers.get(
                                        'x-ratelimit-remaining'
                                    ),
                                    'x-ratelimit-reset': response.headers.get('x-ratelimit-reset'),
                                    'x-ratelimit-used': response.headers.get('x-ratelimit-used'),
                                    'x-ratelimit-resource': response.headers.get(
                                        'x-ratelimit-resource'
                                    ),
                                },
                            )
                            raise GqlRateLimitedExceptionInner(
                                error_dict.get('message', 'Rate Limit hit in GQL')
                            )
                        elif error_type == 'NOT_FOUND':
                            raise GitHubGQLNotFoundError(error_response=error_list)
                    elif len(error_list) > 1:
                        all_not_found = all(
                            error.get('type', '') == 'NOT_FOUND' for error in error_list
                        )

                        if all_not_found:
                            raise GitHubGQLNotFoundError(error_response=error_list)
                    raise Exception(
                        f'Exception encountered when trying to query: {query_body}. Error: {json_data["errors"]}'
                    )
                return json_data
            except requests.exceptions.HTTPError as e:
                # Our GQL connection times out after 60 minutes, if we encounter a 401
                # attempt to re-establish a connection
                if e.response.status_code == 401:
                    self._update_token()
                    continue
                # We can get transient errors that have to do with rate limiting,
                # but aren't directly related to the above GqlRateLimitedExceptionInner logic.
                # Do a simple retry loop here
                elif e.response.status_code in GITHUB_STATUSES_TO_RETRY_ON:
                    pass
                else:
                    raise

                # Raise if we've passed our limit
                if attempt_number > max_attempts:
                    raise

                sleep_time = attempt_number**2
                # Overwrite sleep time if github gives us a specific wait time
                if (
                    retry_after_str := e.response.headers.get('retry-after')
                ) and attempt_number == 1:
                    retry_after = int(retry_after_str)
                    if retry_after > (60 * 5):
                        # if the given wait time is more than 5 minutes, call their bluff
                        # and try the experimental backoff approach
                        pass
                    elif retry_after <= 0:
                        # if the given wait time is negative ignore their suggestion
                        pass
                    else:
                        # Add three seconds for gracetime
                        sleep_time = retry_after + 3

                logger.warning(
                    f'A secondary rate limit was hit. Sleeping for {sleep_time} seconds. (attempt {attempt_number}/{max_attempts})',
                )
                time.sleep(sleep_time)
            except GqlRateLimitedExceptionInner:
                if attempt_number > max_attempts:
                    raise GqlRateLimitExceededException(
                        f'Exceeded maximum retry limit ({max_attempts})'
                    )

                rate_limit_info: GQLRateLimit = self.get_gql_rate_limit()
                reset_at_timestamp = rate_limit_info.reset_at.timestamp()
                curr_timestamp = datetime.now(tz=timezone.utc).timestamp()

                # Sometimes there is a race condition where we get here and our rate limiter has already reset.
                # if that's the case, don't sleep. If, however, our remaining budget is 0 then we're going to
                # have to sleep until it resets
                if rate_limit_info.remaining == 0:
                    # Convert float values to int, add one second as a grace period
                    sleep_time = int(reset_at_timestamp - curr_timestamp) + 1

                    # Sometimes github gives a reset time way in the
                    # future. But rate limits reset each hour, so don't
                    # wait longer than that
                    sleep_time = min(sleep_time, 3600)

                    # Sometimes github gives a reset time in the
                    # past. In that case, wait for 5 mins just in case.
                    if sleep_time <= 0:
                        sleep_time = 300
                    logger.warning(
                        f'GQL Rate Limit hit. Sleeping for {sleep_time} seconds',
                        extra=dict(
                            rate_limit_info=rate_limit_info.__dict__,
                            reset_at_timestamp=str(reset_at_timestamp),
                            curr_timestamp=curr_timestamp,
                            attempt=attempt_number,
                            max_attempts=max_attempts,
                        ),
                    )
                    time.sleep(sleep_time)
            except requests.exceptions.ConnectionError as e:
                if attempt_number > max_attempts:
                    raise

                sleep_time = attempt_number**2
                logger.warning(
                    f'Encountered a ConnectionError ({e})- attempting to sleep for {sleep_time} seconds. Attempt {attempt_number} of {max_attempts}'
                )
                time.sleep(sleep_time)
            except GitHubGQLNotFoundError as not_found_err:
                logger.error(not_found_err)
                raise not_found_err
            except Exception as e:
                if attempt_number > max_attempts:
                    raise

                sleep_time = attempt_number**2
                logger.warning(
                    f'Encountered generic error ({e}) when fetching GQL results. This could be transient so we will retry after {sleep_time} seconds. Attempt {attempt_number} of {max_attempts}'
                )
                time.sleep(sleep_time)
            finally:
                attempt_number += 1

    def page_results_gql(
        self, query_body: str, path_to_page_info: str, cursor: Optional[str] = 'null'
    ) -> Generator[dict, None, None]:
        """This is a helper function for paging results from GraphQL. It expects
        a query body to hit Graphql with that has a %s marker after the "after:"
        key word, so that we can inject a cursor into the query. This will allow
        us to page results in GraphQL.
        To use this function properly, the section you are trying to page MUST
        INCLUDE VALID PAGE INFO (including the hasNext and endCursor attributes)

        Args:
            query_body (str): The query body to hit GraphQL with
            path_to_page_info (str): A string of period separated words that lead
            to the part of the query that we are trying to page. Example: data.organization.userQuery
            cursor (str, optional): LEAVE AS NULL - this argument is use recursively to page. The cursor
            will continuously go up, based on the endCursor attribute in the GQL call. Defaults to 'null'.

        Yields:
            Generator[dict, None, None]: This function yields each item from all the pages paged, item by item
        """
        if not cursor:
            cursor = 'null'
        hasNextPage = True
        while hasNextPage:
            # Fetch results
            result = self.get_raw_result(query_body=(query_body % cursor))

            yield result

            # Get relevant data and yield it
            path_tokens = path_to_page_info.split('.')
            for token in path_tokens:
                result = result[token]

            page_info = result['pageInfo']
            # Need to grab the cursor and wrap it in quotes
            _cursor = page_info['endCursor']
            # If endCursor returns null (None), break out of loop
            hasNextPage = page_info['hasNextPage'] and _cursor
            cursor = f'"{_cursor}"'

    def _get_app_access_token(self) -> Tuple[str, Optional[datetime]]:
        """
        Authenticating a github app requires encoding the installation id, and private key
        into a JWT token in order to request a access_token from the server.
        See: https://developer.github.com/apps/building-github-apps/authenticating-with-github-apps/
        """

        base_url = self.rest_api_url

        # create the jwt_token to authenticate request
        jwt_token = GithubClient.create_jwt_token(app_id=self.app_id, private_key=self.private_key)

        # fetch token from the server
        response = requests.post(
            url=f'{base_url}/app/installations/{self.installation_id}/access_tokens',
            headers={
                'Accept': 'application/vnd.github.machine-man-preview+json',
                'Authorization': f'Bearer {jwt_token}',
                'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
            },
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if e.response.status_code in (403, 404):
                msg = (
                    f"Got HTTP {e.response.status_code} when attempting to create a GithubClient the this address: {base_url}. "
                    "This means our app does not have permission to access the customer's github instance. "
                    "This usually happens when either permissions have intentionally revoked or if an access token expires. "
                    "Set the JFGithubInstance to enabled=False to skip this GitHub instance but allow pulling from any other instances to complete successfully. "
                )
                logger.error(msg)
                raise GitAuthenticationException(msg, original_exception=e)

            raise

        response_data = response.json()
        token: str = response_data['token']
        token_expiration = parse_date(response_data['expires_at'])
        logger.info(
            f'Obtained token successfully - new token will expire in 60m at {token_expiration}'
        )
        return token, token_expiration

    def _update_token(self):
        # refresh token
        self.token, self.token_expiration = self._get_app_access_token()
        self.session.headers.update(
            {
                'Accept': 'application/json',
                'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({default_user_agent()})',
                'Authorization': f'token {self.token}',
            }
        )

    def _check_token_expiration(self):
        if self.token_expiration:
            mins_until_expiration = (
                self.token_expiration - datetime.now(timezone.utc)
            ).total_seconds() / 60
            if mins_until_expiration < 10:
                logger.info(
                    f'Token is going to expire in {mins_until_expiration:.1f} minutes -- obtaining a new token.'
                )
                self._update_token()

    # This is for commits, specifically the 'author' block within them.
    # On the GQL side of things, these are specifically a distinct type of object,
    # GitActor. It has a nested user object, but the quality of data within it
    # is variable due to a users privacy settings. Email, for example, is often
    # not present in the child user block, so we always grab it from the top level.
    @staticmethod
    def _process_git_actor_gql_object(author: Dict) -> dict:
        user: Dict = author.get('user') or {}
        return {
            'id': user.get('id'),
            'login': user.get('login'),
            'email': author['email'],
            'name': author['name'],
        }

    def get_scopes_of_api_token(self):
        # Make an empty call against the orgs API to be quick
        # and get the OAuth scopes
        url = f'{self.rest_api_url}/orgs/'
        result = self.session.get(url)
        return result.headers.get('X-OAuth-Scopes')

    # HACK: This call will actually use the REST endpoint
    # Agent clients are supposed to have the [org:read] scope,
    # but many of them don't. This wasn't a problem before
    # because the REST org API doesn't actually hide behind any perms...
    # TODO: Once we straighten out everybody's permissions we can sunset
    # this function
    def get_organization_by_login(self, login: str):
        # NOTE: We are hitting a different base url here!
        url = f'{self.rest_api_url}/orgs/{login}'

        # HACK: A 403 appears to happen after we have been
        # rate-limited when hitting certain URLs. Add 403s
        # to HTTP Codes to retry
        statuses_to_retry = GITHUB_STATUSES_TO_RETRY_ON
        result = retry_for_status(self.session.get, url, statuses_to_retry=statuses_to_retry)
        result.raise_for_status()
        return result.json()

    # This function is generally only going to be used by Github Enterprise.
    # Github Cloud only has one organization, and as part of onboarding this
    # is entered manually. Github Enterprise, however, can have multiple orgs
    # and entering those all by hand can be hard. Instead, we can discover them.
    # NOTE: Uses the REST API endpoint
    def get_all_organizations(self) -> Generator[Dict, None, None]:
        per_page = 100
        page_number = 1
        while True:
            url = f'{self.rest_api_url}/user/orgs?per_page={per_page}&page={page_number}'

            # HACK: A 403 appears to happen after we have been
            # rate-limited when hitting certain URLs. Add 403s
            # to HTTP Codes to retry
            statuses_to_retry = GITHUB_STATUSES_TO_RETRY_ON
            result: requests.Response = retry_for_status(
                self.session.get, url, statuses_to_retry=statuses_to_retry
            )

            orgs = result.json()
            for org in orgs:
                yield org

            if len(orgs) < per_page:
                return

            page_number += 1

    # HACK: This call will actually use the REST endpoint
    def get_labels_for_repository(self, org_login: str, repo_name: str):
        # NOTE: We are hitting a different base url here!
        labels = []
        page_number = 1
        page_size = 100

        # HACK: A 403 appears to happen after we have been
        # rate-limited when hitting certain URLs. Add 403s
        # to HTTP Codes to retry
        statuses_to_retry = GITHUB_STATUSES_TO_RETRY_ON
        while True:
            url = f'{self.rest_api_url}/repos/{org_login}/{repo_name}/labels?per_page={page_size}&page={page_number}'
            result = retry_for_status(self.session.get, url, statuses_to_retry=statuses_to_retry)
            result.raise_for_status()
            result_json = result.json()
            labels.extend(result_json)
            page_number += 1
            if not result_json:
                break

        return labels

    def get_users(self, login: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                userQuery: membersWithRole(first: 100, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    users: nodes {{
                        {self.GITHUB_GQL_USER_FRAGMENT}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.userQuery'
        ):
            for user in page['data']['organization']['userQuery']['users']:
                yield user

    def get_team_members(self, login: str, team_slug: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                team(slug: \"{team_slug}\") {{
                    membersQuery: members(first: 100, after: %s) {{
                        {GQL_PAGE_INFO_BLOCK}
                        members: nodes {{
                            {self.GITHUB_GQL_USER_FRAGMENT}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.team.membersQuery'
        ):
            for member in page['data']['organization']['team']['membersQuery']['members']:
                yield member

    def get_teams(self, login: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: \"{login}\") {{
                teamsQuery: teams(first: 100, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    teams: nodes {{
                        id
                        slug
                        name
                        description
                        membersQuery: members(first: 100) {{
                            {GQL_PAGE_INFO_BLOCK}
                            members: nodes {{
                                {self.GITHUB_GQL_USER_FRAGMENT}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.teamsQuery'
        ):
            for team in page['data']['organization']['teamsQuery']['teams']:
                if team['membersQuery']['pageInfo']['hasNextPage']:
                    logger.debug(
                        f'Team {team["name"]} was detected as having more than {len(team["membersQuery"]["members"])} members, we need to page for additional members'
                    )
                    team['members'] = [
                        member
                        for member in self.get_team_members(login=login, team_slug=team['slug'])
                    ]
                else:
                    team['members'] = team['membersQuery']['members']

                yield team

    def get_repos(
        self, login: str, only_private: Optional[bool] = False
    ) -> Generator[dict, None, None]:
        priv_filter = 'privacy: PRIVATE, ' if only_private else ''

        query_body = f"""{{
            organization(login: "{login}") {{
                repoQuery: repositories({priv_filter}first: 50, after: %s) {{
                    {GQL_PAGE_INFO_BLOCK}
                    repos: nodes {{
                        ... on Repository {{
                            id: databaseId
                            name
                            fullName: nameWithOwner
                            url
                            isFork
                            defaultBranch: defaultBranchRef {{ name, target {{ sha: oid }} }}
                        }}

                        # Get metadata related to repositories, for more efficient querying later
                        branches: refs(refPrefix:"refs/heads/", first: 0) {{ totalCount }}
                        defaultBranch: defaultBranchRef {{
                            commitsQuery: target {{
                                ... on Commit {{commitHistory: history(first: 1){{ commits: nodes {{ committedDate }} }} }}
                            }}
                        }}
                        prQuery: pullRequests(first: 1, orderBy: {{ direction: DESC, field:UPDATED_AT }}) {{prs: nodes {{updatedAt}} }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repoQuery'
        ):
            for api_repo in page['data']['organization']['repoQuery']['repos']:
                yield api_repo

    def get_branches(self, login: str, repo_name: str) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branchQuery: refs(refPrefix:"refs/heads/", first: 100, after: %s) {{
                            {GQL_PAGE_INFO_BLOCK}
                            branches: nodes {{
                                ... on Ref {{
                                    name
                                    target {{sha: oid}}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repository.branchQuery'
        ):
            for api_branch in page['data']['organization']['repository']['branchQuery']['branches']:
                yield api_branch

    def get_commits_count(
        self, login: str, repo_name: str, branch_name: str, since: datetime
    ) -> int:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branch: ref(qualifiedName: "{branch_name}") {{
                            target {{
                                ... on Commit {{
                                    history(first: 0, since: "{self.datetime_to_gql_str_format(since)}") {{
                                        totalCount
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        return int(
            self.get_raw_result(query_body)['data']['organization']['repo']['branch']['target'][
                'history'
            ]['totalCount']
        )

    def get_commits(
        self,
        login: str,
        repo_name: str,
        branch_name: str,
        since: datetime,
        until: Optional[datetime] = None,
    ) -> Generator[dict, None, None]:
        optional_until_clause = (
            f' until: "{self.datetime_to_gql_str_format(until)}",' if until else ""
        )
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    ... on Repository {{
                        branch: ref(qualifiedName: "{branch_name}") {{
                            target {{
                                ... on Commit {{
                                    history(first: 100, since: "{self.datetime_to_gql_str_format(since)}", {optional_until_clause} after: %s) {{
                                        {GQL_PAGE_INFO_BLOCK}
                                        commits: nodes {{
                                            {self.GITHUB_GQL_COMMIT_FRAGMENT}
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.branch.target.history'
        ):
            for api_commit in page['data']['organization']['repo']['branch']['target']['history'][
                'commits'
            ]:
                # Overwrite Author block for backwards compatibility
                api_commit['author'] = self._process_git_actor_gql_object(api_commit['author'])
                yield api_commit

    #
    # PR Queries are HUGE, so pull out reusable blocks (comments, reviews, commits, etc)
    #
    def _get_pr_comments_query_block(self, enable_paging: bool = False):
        return f"""
            commentsQuery: comments(first: 100{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}

                comments: nodes {{
                    author {{
                        {self.github_gql_actor_fragment}
                    }}
                    body
                    createdAt
                }}
            }}
        """

    # NOTE: There are comments associated with reviews that we need to fetch as well
    def _get_pr_reviews_query_block(self, enable_paging: bool = False):
        return f"""
            reviewsQuery: reviews(first: 25{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}

                reviews: nodes {{
                    ... on PullRequestReview {{
                        author {{
                            {self.github_gql_actor_fragment}
                        }}
                        id: databaseId
                        state
                        # NOTE! We are paging for comments here as well!
                        {self._get_pr_comments_query_block()}
                    }}
                }}
            }}
        """

    def _get_labels_query_block(self, enable_paging: bool = False):
        return f"""
            labelsQuery: labels(first: 50{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}
                labels: nodes {{
                    ... on Label {{
                        node_id: id
                        name
                        default: isDefault
                        description
                    }}
                }}
            }}
        """

    def _get_pr_files_query_block(self, enable_paging: bool = False):
        return f"""
            filesQuery: files(first: 50{', after: %s' if enable_paging else ''}) {{
                {GQL_PAGE_INFO_BLOCK}
                files: nodes {{
                    ... on PullRequestChangedFile {{
                        additions
                        deletions
                        path
                        status: changeType
                    }}
                }}
            }}
        """

    def _get_pr_commits_query_block(
        self, enable_paging: bool = False, include_force_push_commits: bool = False
    ):
        # Force push commits use a different gql element
        if include_force_push_commits:
            return f"""
                commitsQuery: timelineItems(first: 50{', after: %s' if enable_paging else ''}) {{
                    {GQL_PAGE_INFO_BLOCK}

                    commits: nodes {{
                        ... on PullRequestCommit {{
                            commit {{
                                {self.GITHUB_GQL_COMMIT_FRAGMENT}
                            }}
                        }}
                        ... on HeadRefForcePushedEvent {{
                            beforeCommit {{
                                {self.GITHUB_GQL_COMMIT_FRAGMENT}
                            }}
                        }}
                    }}
                }}
            """
        else:
            return f"""
                commitsQuery: commits(first: 50{', after: %s' if enable_paging else ''}) {{
                    {GQL_PAGE_INFO_BLOCK}

                    commits: nodes {{
                        ... on PullRequestCommit {{
                            commit {{
                                {self.GITHUB_GQL_COMMIT_FRAGMENT}
                            }}
                        }}
                    }}
                }}
            """

    def get_prs_count(self, login: str, repo_name: str) -> int:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    prQuery: pullRequests(first: 1, orderBy: {{direction: DESC, field: UPDATED_AT}}) {{
                        totalCount
                    }}
                }}
            }}
        }}
        """
        return int(
            self.get_raw_result(query_body=query_body)['data']['organization']['repo']['prQuery'][
                'totalCount'
            ]
        )

    def get_prs_metadata(self, login: str, repo_name: str) -> Generator[dict, None, None]:
        """
        Helper function, intended to be SUPER lightweight query against PRs. It returns PR Id (number) and the last updated date,
        as well as the current GQL cursor of the returned PR.

        Returned Format:
        {
            'cursor': 'gql_cursor_value',
            'pr': {
                'number': 1,
                'updatedAt': 'gql_formatted_date'
            }
        }
        """
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    prQuery: pullRequests(first: 100, orderBy: {{direction: DESC, field: UPDATED_AT}}, after: %s) {{
                        {GQL_PAGE_INFO_BLOCK}
                        prs: edges {{ cursor, pr: node {{number, updatedAt}} }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.prQuery'
        ):
            for api_pr in page['data']['organization']['repo']['prQuery']['prs']:
                yield api_pr

    def get_pr_authors(
        self, login: str, repo_name: str, pr_ids: list[int]
    ) -> dict[int, dict[str, Union[str, None]]]:
        """
        Get each author for a list of PRs.

        Returned Format:
        {
            pr_number (int): {
                    'id': (Optional[str]) gql_id,
                    'login': (Optional[str]) login,
                    'name': (Optional[str]) name,
                    'email': (Optional[str]) email
                }
        }
        """

        def _get_pr_author_query_block(pr_number_list: list[int]) -> str:
            pr_blocks = "\n".join(
                f"""
                        pr_{n}: pullRequest(number: {n}) {{
                            number
                            author {{
                                { textwrap.indent(self.github_gql_actor_fragment, " " * 16) }
                            }}
                        }}
                """
                for n in pr_number_list
            )

            return textwrap.dedent(
                f"""{{
                organization(login: "{login}") {{
                    repo: repository(name: "{repo_name}") {{
                        {pr_blocks}
                    }}
                }}
            }}
            """
            ).strip()

        pr_authors: dict[int, dict[str, Union[str, None]]] = {}

        for number_batch in batch_iterable(pr_ids, 100):
            continue_search = True
            process_authors = True
            current_pr_numbers = number_batch.copy()
            attempt_count = 0
            result: Optional[dict] = None

            while continue_search and attempt_count < 3:
                attempt_count += 1

                try:
                    result = self.get_raw_result(_get_pr_author_query_block(current_pr_numbers))
                    continue_search = False
                except GitHubGQLNotFoundError as e:
                    logger.warning('Not all PRs found, removing missing PRs from query')

                    for err in e.error_response:
                        # Expected format: 'path': ['organization', 'repo', 'pr_1234']
                        try:
                            pr_num_str = err.get('path', [])[-1]
                            pr_num = int(pr_num_str.split('_')[-1])

                            logger.info(f'Removing PR {pr_num} from query')
                            current_pr_numbers.remove(pr_num)
                        except Exception as e:
                            logger.warning(f'Error removing PR {err} from query: {e}')

                    if not current_pr_numbers:
                        logger.info('No PRs left to query, stopping')
                        continue_search = False
                        process_authors = False
                except Exception as e:
                    logger.error(f'GQL error querying PR authors: {e}')
                    continue_search = False
                    process_authors = False

            if not process_authors or not result:
                logger.error('Unable to process PR authors for PR number batch, skipping')
                continue

            for _, pr_data in result['data']['organization']['repo'].items():
                pr_number = pr_data['number']
                pr_actor = pr_data.get('author')

                if pr_actor:
                    a_id = pr_actor.get('id')
                    a_id = str(a_id) if a_id else None

                    pr_authors[pr_number] = {
                        'id': a_id,
                        'login': pr_actor.get('login'),
                        'name': pr_actor.get('name'),
                        'email': pr_actor.get('email'),
                    }

        return pr_authors

    # PR query is HUGE, see above GITHUB_GQL_PR_* blocks for reused code
    # page_size is optimally variable. Most repos only have a 0 to a few PRs day to day,
    # so sometimes the optimal page_size is 0. Generally, we should never go over 25
    def get_prs(
        self,
        login: str,
        repo_name: str,
        include_top_level_comments: bool = False,
        include_force_push_commits: bool = False,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        repository_label_node_ids_to_id: Dict[str, int] = {},
        page_size: int = MAX_PAGE_SIZE_FOR_PR_QUERY,
        start_cursor: Optional[Any] = None,
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    prQuery: pullRequests(first: {page_size}, orderBy: {{direction: DESC, field: UPDATED_AT}}, after: %s) {{
                        {GQL_PAGE_INFO_BLOCK}
                        prs: nodes {{
                            ... on PullRequest {{
                                id: number
                                number
                                additions
                                deletions
                                changedFiles
                                state
                                merged
                                createdAt
                                updatedAt
                                mergedAt
                                closedAt
                                title
                                body
                                url
                                baseRefName
                                headRefName
                                baseRepository {{ {self.GITHUB_GQL_SHORT_REPO_FRAGMENT} }}
                                headRepository {{ {self.GITHUB_GQL_SHORT_REPO_FRAGMENT} }}
                                author {{
                                    {self.github_gql_actor_fragment}
                                }}
                                mergedBy {{
                                    {self.github_gql_actor_fragment}
                                }}
                                mergeCommit {{
                                    {self.GITHUB_GQL_COMMIT_FRAGMENT}
                                }}
                                {self._get_pr_comments_query_block(enable_paging=False) if include_top_level_comments else ''}
                                {self._get_pr_reviews_query_block(enable_paging=False)}
                                {self._get_pr_commits_query_block(enable_paging=False, include_force_push_commits=include_force_push_commits)}
                                {self._get_pr_files_query_block(enable_paging=False) if pull_files_for_pr else ''}
                                {self._get_labels_query_block(enable_paging=False)}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """
        transformed_start_cursor = f'"{start_cursor}"' if start_cursor else None
        for page in self.page_results_gql(
            query_body=query_body,
            path_to_page_info='data.organization.repo.prQuery',
            cursor=transformed_start_cursor,
        ):
            for api_pr in page['data']['organization']['repo']['prQuery']['prs']:
                # Process and add related PR data (comments, reviews, commits)
                # This may require additional API calls
                pr_number = api_pr['number']

                # Load reviews first because we use them in both reviews and comments
                reviews = (
                    [r for r in self.get_pr_reviews(login, repo_name, pr_number=pr_number)]
                    if api_pr['reviewsQuery']['pageInfo']['hasNextPage']
                    else api_pr['reviewsQuery']['reviews']
                )

                # NOTE: COMMENTS ARE WEIRD! They exist in there own API endpoint (these
                # are typically top level comments in a PR, considered an IssueComment)
                # but there are also comments associated with each review (typically only one)
                # The baseline for what we care about is the Review Level comment, pulled from
                # the reviews endpoint. Grabbing Top Level Comments is an optional feature flag

                # Grab the comments pulled from reviews. We ALWAYS want these!
                api_pr['comments'] = [
                    comment for review in reviews for comment in review['commentsQuery']['comments']
                ]

                # Grab the potentially optional top level comments
                if include_top_level_comments:
                    top_level_comments = (
                        [
                            comment
                            for comment in self.get_pr_top_level_comments(
                                login, repo_name, pr_number=pr_number
                            )
                        ]
                        if api_pr['commentsQuery']['pageInfo']['hasNextPage']
                        else api_pr['commentsQuery']['comments']
                    )
                    api_pr['comments'].extend(top_level_comments)

                api_pr['reviews'] = reviews

                api_pr['commits'] = (
                    [
                        commit
                        for commit in self.get_pr_commits(
                            login,
                            repo_name,
                            pr_number=pr_number,
                            include_force_push_commits=include_force_push_commits,
                        )
                    ]
                    if api_pr['commitsQuery']['pageInfo']['hasNextPage']
                    else [
                        commit['commit'] if 'commit' in commit else commit['beforeCommit']
                        for commit in api_pr['commitsQuery']['commits']
                        if 'commit' in commit or 'beforeCommit' in commit
                    ]
                )

                # Do some extra processing on commits to clean up their weird author block
                for commit in api_pr['commits']:
                    commit['author'] = self._process_git_actor_gql_object(commit['author'])

                if api_pr['mergeCommit'] and api_pr['mergeCommit']['author']:
                    api_pr['mergeCommit']['author'] = self._process_git_actor_gql_object(
                        api_pr['mergeCommit']['author']
                    )

                labels = (
                    [label for label in self.get_pr_labels(login, repo_name, pr_number=pr_number)]
                    if api_pr['labelsQuery']['pageInfo']['hasNextPage']
                    else [label for label in api_pr['labelsQuery']['labels']]
                )
                api_pr['labels'] = []
                # Only add to labels if we have the proper label ID
                for label in labels:
                    if repository_label_node_ids_to_id.get(label['node_id']):
                        label['id'] = repository_label_node_ids_to_id.get(label['node_id'])
                        api_pr['labels'].append(label)

                # NOTE: Processing files requires quite a bit of in place transformation
                if pull_files_for_pr:
                    files = api_pr['filesQuery']['files']
                    api_pr['files'] = {}
                    # If there are more files to fetch, fetch them
                    if api_pr['filesQuery']['pageInfo']['hasNextPage']:
                        files = self.get_pr_files(login, repo_name, pr_number=pr_number)

                    for file_dict in files:
                        # File path is the dictionary key, and should not be included in the dictionary body
                        file_path = (
                            hash_filename(file_dict.pop('path'))
                            if hash_files_for_prs
                            else file_dict.pop('path')
                        )
                        # The legacy REST API includes a 'changed' field, which is the total of additions and deletions.
                        # To match legacy logic, perform that operations here
                        file_dict['changes'] = file_dict['additions'] + file_dict['deletions']
                        # The legacy REST API has the status enums all lowercase
                        file_dict['status'] = file_dict['status'].lower()
                        api_pr['files'][file_path] = file_dict

                yield api_pr

    def get_pr_top_level_comments(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_comments_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.commentsQuery'
        ):
            for api_pr_comment in page['data']['organization']['repo']['pr']['commentsQuery'][
                'comments'
            ]:
                yield api_pr_comment

    def get_pr_reviews(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_reviews_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.reviewsQuery'
        ):
            for api_pr_review in page['data']['organization']['repo']['pr']['reviewsQuery'][
                'reviews'
            ]:
                yield api_pr_review

    def get_pr_commits(
        self, login: str, repo_name: str, pr_number: int, include_force_push_commits: bool = False
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_commits_query_block(enable_paging=True, include_force_push_commits=include_force_push_commits)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.commitsQuery'
        ):
            for api_pr_commit in page['data']['organization']['repo']['pr']['commitsQuery'][
                'commits'
            ]:
                # When we are pulling commits with force pushes, we can get empty elements in this
                # query that are PR timeline events that are not force-pushes or commits. In that
                # case, just skip them.
                if include_force_push_commits and not api_pr_commit:
                    continue

                # Commit blocks are nested within the 'commits' block
                commit = (
                    api_pr_commit['beforeCommit']
                    if 'beforeCommit' in api_pr_commit
                    else api_pr_commit['commit']
                )
                commit['author'] = self._process_git_actor_gql_object(commit['author'])
                yield commit

    def get_pr_files(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_pr_files_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.filesQuery'
        ):
            for api_pr_file in page['data']['organization']['repo']['pr']['filesQuery']['files']:
                yield api_pr_file

    def get_pr_labels(
        self, login: str, repo_name: str, pr_number: int
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                repo: repository(name: "{repo_name}") {{
                    pr: pullRequest(number: {pr_number}) {{
                        ... on PullRequest {{
                            {self._get_labels_query_block(enable_paging=True)}
                        }}
                    }}
                }}
            }}
        }}
        """
        for page in self.page_results_gql(
            query_body=query_body, path_to_page_info='data.organization.repo.pr.labelsQuery'
        ):
            for api_pr_label in page['data']['organization']['repo']['pr']['labelsQuery']['labels']:
                yield api_pr_label

    def get_users_count(self, login: str) -> int:
        query_body = f"""{{
            organization(login: "{login}"){{
                    users: membersWithRole {{
                        totalCount
                    }}
                }}
            }}
        """
        # TODO: Maybe serialize the return results so that we don't have to do this crazy nested grabbing?
        return int(
            self.get_raw_result(query_body=query_body)['data']['organization']['users'][
                'totalCount'
            ]
        )

    def get_repos_count(self, login: str, only_private: bool = False) -> int:
        priv_filter = '(privacy: PRIVATE)' if only_private else ''

        query_body = f"""{{
            organization(login: "{login}"){{
                    repos: repositories{priv_filter} {{
                        totalCount
                    }}
                }}
            }}
        """
        # TODO: Maybe serialize the return results so that we don't have to do this crazy nested grabbing?
        return int(
            self.get_raw_result(query_body=query_body)['data']['organization']['repos'][
                'totalCount'
            ]
        )

    def get_repo_manifest_data(
        self, login: str, page_size: int = 10
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
            organization(login: "{login}") {{
                    repositories(first: {page_size}, after: %s) {{
                        pageInfo {{
                            endCursor
                            hasNextPage

                        }}
                        repos: nodes {{
                            id: databaseId
                            name
                            url
                            defaultBranch: defaultBranchRef {{
                                name
                                target {{
                                    ... on Commit {{
                                        history {{
                                            totalCount
                                        }}
                                    }}
                                }}
                            }}
                            users: assignableUsers{{
                                totalCount
                            }}
                            prs: pullRequests {{
                                totalCount
                            }}
                            branches: refs(refPrefix:"refs/heads/") {{
                                totalCount
                            }}
                        }}
                    }}
                }}
            }}
        """
        path_to_page_info = 'data.organization.repositories'
        for result in self.page_results_gql(
            query_body=query_body, path_to_page_info=path_to_page_info
        ):
            for repo in result['data']['organization']['repositories']['repos']:
                yield repo

    def get_pr_manifest_data(
        self, login: str, repo_name: str, page_size=100
    ) -> Generator[dict, None, None]:
        query_body = f"""{{
                organization(login: "{login}") {{
                        repository(name: "{repo_name}") {{
                            name
                            id: databaseId
                            prs_query: pullRequests(first: {page_size}, after: %s) {{
                                pageInfo {{
                                    endCursor
                                    hasNextPage
                                }}
                                totalCount
                                prs: nodes {{
                                    updatedAt
                                    id: databaseId
                                    title
                                    number
                                    repository {{id: databaseId, name}}
                                }}
                            }}
                        }}
                    }}
                }}
        """

        path_to_page_info = 'data.organization.repository.prs_query'
        for result in self.page_results_gql(
            query_body=query_body, path_to_page_info=path_to_page_info
        ):
            for pr in result['data']['organization']['repository']['prs_query']['prs']:
                yield pr
