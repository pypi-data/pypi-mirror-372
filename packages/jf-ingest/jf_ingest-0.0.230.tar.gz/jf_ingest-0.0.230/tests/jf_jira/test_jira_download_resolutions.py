import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_resolutions
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)


def test_download_resolutions():
    """
    Resolutions is a simple function, so we just need a simple test
    """
    with requests_mock.Mocker() as m:
        resolution_data_str = get_fixture_file_data("api_responses/resolution.json")
        _register_jira_uri(m, endpoint="resolution", return_value=resolution_data_str)

        resolutions = download_resolutions(get_jira_mock_connection())

        assert type(resolutions) == list
        assert resolutions == json.loads(resolution_data_str)
