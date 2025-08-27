import json
import os

import requests_mock
from jira import JIRA

from jf_ingest.config import JiraAuthConfig
from jf_ingest.jf_jira.auth import get_jira_connection
from jf_ingest.jf_jira.downloaders import IssueMetadata

_MOCK_REST_BASE_URL = "https://test-co.atlassian.net/rest/api/2"
_MOCK_AGILE_BASE_URL = "https://test-co.atlassian.net/rest/agile/1.0"


def get_jira_mock_connection(mocker=None) -> JIRA:
    """Helper function for getting a spoofed JIRA connection

    Returns:
        JIRA: A Mocked JIRA connection object
    """

    _MOCK_SERVER_INFO_RESP = (
        '{"baseUrl":"https://test-co.atlassian.net","version":"1001.0.0-SNAPSHOT",'
        '"versionNumbers":[1001,0,0],"deploymentType":"Cloud","buildNumber":100218,'
        '"buildDate":"2023-03-16T08:21:48.000-0400","serverTime":"2023-03-17T16:32:45.255-0400",'
        '"scmInfo":"9999999999999999999999999999999999999999","serverTitle":"JIRA",'
        '"defaultLocale":{"locale":"en_US"}} '
    )

    auth_config = JiraAuthConfig(
        url="https://test-co.atlassian.net/",
        personal_access_token="asdf",
        company_slug="test_co",
        gdpr_active=True,
    )

    if not mocker:
        with requests_mock.Mocker() as m:
            _register_jira_uri(m, "serverInfo", f"{_MOCK_SERVER_INFO_RESP}")
            _register_jira_uri_with_file(m, "field", "api_responses/fields.json")
            jira_conn = get_jira_connection(config=auth_config, max_retries=1)
    else:
        _register_jira_uri(mocker, "serverInfo", f"{_MOCK_SERVER_INFO_RESP}")
        _register_jira_uri_with_file(mocker, "field", "api_responses/fields.json")
        jira_conn = get_jira_connection(config=auth_config, max_retries=1)

    return jira_conn


def get_fixture_file_data(fixture_path: str) -> str:
    """Helper function to get file data from a fixture

    Usage (if calling from tests/jf_jira/test_jira_resolutions.py):
    fixture_path='api_response/resolutions.json'

    Args:
        fixture_path (str): A path to a fixture file. It prepends the current relative path.

    Returns:
        str: The file data as a string
    """
    with open(f"{os.path.dirname(__file__)}/fixtures/{fixture_path}", "r") as f:
        return f.read()


def get_jellyfish_issue_metadata() -> dict[str, IssueMetadata]:
    """Gets some hardcoded jellyfish metadata

    Returns:
        dict[str, dict]: Hardcoded jellyfish issue data from tests/jf_jira/fixtures/jellyfish_issue_metadata.json
    """
    with open(f"{os.path.dirname(__file__)}/fixtures/jellyfish_issue_metadata.json", "r") as f:
        return [IssueMetadata(**metadata_dict) for metadata_dict in json.loads(f.read())]


def _register_jira_uri_with_file(
    mock: requests_mock.Mocker, endpoint: str, fixture_path: str
) -> None:
    """Registers a Jira API endpoint to respond with the data from a fixture file

    Args:
        mock (requests_mock.Mocker): A requests_mock.Mocker() object
        endpoint (str): The endpoint we want to spoof
        fixture_path (str): The file of data we want it to return
    """
    _register_jira_uri(mock, endpoint, get_fixture_file_data(fixture_path=fixture_path))


def _register_jira_uri(
    mock: requests_mock.Mocker,
    endpoint: str,
    return_value: str,
    HTTP_ACTION: str = "GET",
    use_agile_endpoint: bool = False,
    status_code: int = 200,
) -> None:
    """Helper function used to registering mock results for testing against our mock JIRA API. Works by providing
    a request_mock.Mocker instance, what endpoint you want to spoof, and the string that you want that spoofed endpoint
    to return

    Args:
        mock (requests_mock.Mocker): Mocker object
        endpoint (str): Endpoint to append to the end of the base URL ("https://test-co.atlassian.net/rest/api/2", unless use_agile_endpoint is True)
        return_value (str): The raw str to return from the API endpoint
        use_agile_endpoint (bool, optional): IF TRUE, switch the default base URL from the /rest/api/2 endpoint to the agile endpoint. MUST BE TRUE FOR SPRINT AND BOARD API ENDPOINTS. Defaults to False.
        HTTP_ACTION (str, optional): If we are mocking a GET or POST or PUT HTTP command. Defaults to "GET".
    """

    _MOCK_REST_BASE_URL = "https://test-co.atlassian.net/rest/api/2"

    mock_base_url = _MOCK_REST_BASE_URL if not use_agile_endpoint else _MOCK_AGILE_BASE_URL
    mock.register_uri(
        HTTP_ACTION,
        f"{mock_base_url}/{endpoint}",
        text=return_value,
        status_code=status_code,
    )
