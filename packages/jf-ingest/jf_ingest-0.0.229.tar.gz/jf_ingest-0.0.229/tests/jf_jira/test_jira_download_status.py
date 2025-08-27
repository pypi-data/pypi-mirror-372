import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_statuses
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)


def test_download_statuses():
    """
    Resolutions is a simple function, so we just need a simple test
    """
    with requests_mock.Mocker() as m:
        status_data_str = get_fixture_file_data("api_responses/status.json")
        _register_jira_uri(m, endpoint="status", return_value=status_data_str)

        statuses = download_statuses(get_jira_mock_connection())

        assert type(statuses) == list
        assert [status["raw_json"] for status in statuses] == json.loads(status_data_str)
        for status_json in statuses:
            assert status_json["status_id"] == status_json["raw_json"]["id"]
