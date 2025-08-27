import logging
from typing import Optional, Union

import requests
from jira import JIRA, JIRAError
from jira.resources import GreenHopperResource
from requests.auth import AuthBase

from jf_ingest.config import JiraAuthConfig, JiraAuthMethod, JiraDownloadConfig
from jf_ingest.utils import retry_for_status

logger = logging.getLogger(__name__)


class JiraAuthenticationException(Exception):
    def __init__(self, *args, original_exception: Optional[Exception] = None):
        self.original_exception = original_exception
        super().__init__(*args)


# HACK(asm,2024-05-10): We are seeing questionable HTTP 401 responses from Jira that seem to be
# related to cookie-based authentication validation. Specifically, we believe that requests made
# using a bearer token are creating an expiring session on the server side, and it is causing Jira
# to (incorrectly) challenge us to re-authenticate based on this expired session. To avoid this, we
# are customizing the authentication method so that we never send cookies when we are using bearer
# token authentication. If this works, this should be upstreamed.
class TokenAuth(AuthBase):
    def __init__(self, token: str):
        self._token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        # never send cookies for token auth
        r.headers["Cookie"] = ''
        r.headers["authorization"] = f"Bearer {self._token}"
        return r


def get_jira_connection(
    config: Union[JiraAuthConfig, JiraDownloadConfig],
    auth_method: JiraAuthMethod = JiraAuthMethod.BasicAuth,
    max_retries=3,
    use_jql_enhanced_search: bool = False,
) -> JIRA:
    """Get a JIRA connection object

    Args:
        config (JiraAuthConfig | JiraDownloadConfig): A JIRA Configuration Object that contains authentication information
        auth_method (JiraAuthMethod, optional): The Authentication method used. BasicAuth and AtlassianConnect are currently supported. Defaults to JiraAuthMethod.BasicAuth.
        max_retries (int, optional): The retry limit used by the JiraConnection.ResilientSession object. Defaults to 3.
        use_jql_enhanced_search (bool, optional): Whether to configure connection for JQL Enhanced Search API. When True, uses REST API v3 for /search/jql endpoints. When False, uses REST API v2 for backward compatibility. Defaults to False.

    Raises:
        Several Errors can be raised by this class. Please ensure your config is properly set up

    Returns:
        JIRA: A JIRA connection object
    """
    should_ssl_verify = not config.bypass_ssl_verification

    # This is the base Jira Connection KWARGs. For different
    # authentication methods, we will need to add specific fields
    jira_conn_kwargs = {
        "timeout": 600,
        "server": config.url,
        "max_retries": max_retries,
        "options": {
            "agile_rest_path": GreenHopperResource.AGILE_BASE_REST_PATH,
            "verify": should_ssl_verify,
            "headers": {
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "Accept": "application/json,*/*;q=0.9",
                "X-Atlassian-Token": "no-check",
            },
        },
    }

    # Determine REST API version based on intended usage
    if use_jql_enhanced_search:
        jira_conn_kwargs['options']['rest_api_version'] = '3'

    using_token_auth = False

    if auth_method.value == JiraAuthMethod.AtlassianConnect.value:
        if not config.connect_app_active:
            raise RuntimeError(
                f'Atlassian connect integration for {config.company_slug} is disabled. Check "connect_app_active" flag state.'
            )

        # The customer has installed our Atlassian Connect app; we authenticate to the Jira
        # API using the JWT attributes
        shared_secret = config.jwt_attributes.get("sharedSecret")
        client_key = config.jwt_attributes.get("clientKey")
        key = config.jwt_attributes.get("key")

        if not (shared_secret and client_key and key):
            raise RuntimeError(
                f"Atlassian connect integration for {config.company_slug} is misconfigured"
            )

        logger.info(f"Authenticating to Jira API at {config.url} using JWT attributes")
        jira_conn_kwargs['jwt'] = {
            "secret": shared_secret,
            "payload": {"iss": key, "aud": client_key},
        }
        jira_conn: JIRA = retry_for_status(
            JIRA, max_retries_for_retry_for_status=3, **jira_conn_kwargs
        )

    elif auth_method.value == JiraAuthMethod.BasicAuth.value:
        # Attempt to log a helpful warning if a customer has a Jira User provided but NOT a jira password provided
        if config.user and not config.password:
            optional_bearer_token_message = (
                f'A Jira Bearer token was being detected as being provided, so we will attempt to authenticate with that instead. '
                'If you would like to authenticate with only the Bear token please remove the Jira User field provided, as it is not necessary.'
            )
            logger.warning(
                f'Jira Authentication has detected that a Jira User value has been provided, '
                'but that Jira Password value was left blank. '
                'If you would like to authenticate using a User/Password scheme, please provide the username and password. '
                f'{optional_bearer_token_message if config.personal_access_token else ""}'
            )

        # Attempt user/password auth only if we have both a user and a password
        if config.user and config.password:
            logger.info(
                f"Authenticating to Jira API at {config.url} "
                f"using the username and password secrets for {config.user} of company {config.company_slug}"
            )
            # Add in basic auth info
            jira_conn_kwargs['basic_auth'] = (config.user, config.password)
        elif config.personal_access_token:
            logger.info(
                f"Authenticating to Jira API at {config.url} "
                f"using the personal_access_token secret for {config.company_slug}"
            )
            # Add in personal access token
            jira_conn_kwargs['token_auth'] = config.personal_access_token

            using_token_auth = True
        else:
            raise RuntimeError(
                f"No valid basic authentication mechanism for {config.url} - need a username/password combo or a personal access token"
            )

        while True:
            try:
                jira_conn = retry_for_status(
                    JIRA, max_retries_for_retry_for_status=3, **jira_conn_kwargs
                )
                break
            except JIRAError as e:  # catch generic error raised from JIRA
                if hasattr(e, "status_code") and e.status_code in (401, 403):
                    raise JiraAuthenticationException(
                        f"Jira authentication (HTTP ERROR CODE {e.status_code}) failed for {config.url} using {config.user} and the jira_password secret for {config.company_slug}",
                        original_exception=e,
                    )
                else:
                    raise
    else:
        raise RuntimeError(
            f"No valid authentication mechanism for {config.url} (Auth Method: {auth_method})."
        )

    # set user-agent
    jira_conn._session.headers["User-Agent"] = (
        f'{config.user_agent} ({jira_conn._session.headers["User-Agent"]})'
    )

    # HACK(asm,2024-05-10): See comment above `TokenAuth` class definition - overriding
    # authentication here to force no cookies.
    if using_token_auth and config.personal_access_token:
        jira_conn._session.auth = TokenAuth(config.personal_access_token)

    return jira_conn
