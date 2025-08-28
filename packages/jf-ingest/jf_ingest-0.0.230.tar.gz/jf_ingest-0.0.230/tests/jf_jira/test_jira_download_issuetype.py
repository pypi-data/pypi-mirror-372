import json

import requests_mock

from jf_ingest.jf_jira.downloaders import download_issuetypes
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)

ISSUE_TYPE_SORT_KEY = lambda x: x["id"]


def test_download_issuetypes_no_projects():
    with requests_mock.Mocker() as m:
        issuetype_data_str = get_fixture_file_data("api_responses/issuetype.json")
        _register_jira_uri(m, endpoint="issuetype", return_value=issuetype_data_str)

        issuetypes = download_issuetypes(get_jira_mock_connection(), project_ids=[])

        issuetype_data = json.loads(issuetype_data_str)
        issuetypes_with_no_project_scope = [
            issuetype for issuetype in issuetype_data if "scope" not in issuetype
        ]

        assert type(issuetypes) == list
        assert len(issuetypes) > 0
        assert issuetypes.sort(key=ISSUE_TYPE_SORT_KEY) == issuetypes_with_no_project_scope.sort(
            key=ISSUE_TYPE_SORT_KEY
        )


def test_download_issuetypes_with_projects():
    with requests_mock.Mocker() as m:
        issuetype_data_str = get_fixture_file_data("api_responses/issuetype.json")
        _register_jira_uri(m, endpoint="issuetype", return_value=issuetype_data_str)

        projects_to_include = ["10022", "10009"]

        issuetype_data = json.loads(issuetype_data_str)

        # Issue types we want
        issuetypes_with_no_project_scope = [
            issuetype for issuetype in issuetype_data if "scope" not in issuetype
        ]
        issue_types_with_included_projects = [
            issuetype
            for issuetype in issuetype_data
            if "scope" in issuetype
            and issuetype["scope"]["type"] == "PROJECT"
            and issuetype["scope"]["project"]["id"] in projects_to_include
        ]
        issuetypes_we_want = [
            *issue_types_with_included_projects,
            *issuetypes_with_no_project_scope,
        ]

        # Issue types we don't want
        issuetypes_we_do_not_want = [
            issuetype
            for issuetype in issuetype_data
            if "scope" in issuetype
            and issuetype["scope"]["type"] == "PROJECT"
            and issuetype["scope"]["project"]["id"] not in projects_to_include
        ]

        issuetypes = download_issuetypes(
            get_jira_mock_connection(), project_ids=projects_to_include
        )
        assert len(issuetypes) > 0
        assert issuetypes.sort(key=ISSUE_TYPE_SORT_KEY) == issuetypes_we_want.sort(
            key=ISSUE_TYPE_SORT_KEY
        )
        for issuetype in issuetypes:
            assert issuetype not in issuetypes_we_do_not_want
