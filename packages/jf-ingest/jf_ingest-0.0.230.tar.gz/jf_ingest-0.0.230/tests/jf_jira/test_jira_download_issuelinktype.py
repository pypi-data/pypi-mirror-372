import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_issuelinktypes
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)


def test_download_issuelinktypes():
    """
    Resolutions is a simple function, so we just need a simple test
    """
    with requests_mock.Mocker() as m:
        issuelinktype_data_str = get_fixture_file_data("api_responses/issueLinkType.json")
        _register_jira_uri(m, endpoint="issueLinkType", return_value=issuelinktype_data_str)

        issuelinktypes = download_issuelinktypes(get_jira_mock_connection())

        assert type(issuelinktypes) == list
        assert issuelinktypes == json.loads(issuelinktype_data_str)["issueLinkTypes"]
