import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_priorities
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)


def test_download_priorities():
    """
    Resolutions is a simple function, so we just need a simple test
    """
    with requests_mock.Mocker() as m:
        priority_data_str = get_fixture_file_data("api_responses/priority.json")
        _register_jira_uri(m, endpoint="priority", return_value=priority_data_str)

        priorities = download_priorities(get_jira_mock_connection())

        assert type(priorities) == list
        assert priorities == json.loads(priority_data_str)
