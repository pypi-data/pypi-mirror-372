import json
from contextlib import contextmanager
from datetime import datetime

import requests_mock

from jf_ingest.jf_jira.downloaders import (
    _convert_datetime_to_worklog_timestamp,
    download_worklogs,
)
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)

DELETED_WORKLOG_IDS = [10007, 10008]


@contextmanager
def worklogs_context_manager(existing_ids: list[int] = []):
    with requests_mock.Mocker() as m:
        # Get specific updated since data
        worklog_updated_data_str = get_fixture_file_data("api_responses/worklog_updated.json")
        _register_jira_uri(
            m, endpoint="worklog/updated?since=0", return_value=worklog_updated_data_str
        )
        # List Updated Since Data
        worklog_list_data_str = get_fixture_file_data("api_responses/worklog_list.json")
        worklog_filtered = [
            wl for wl in json.loads(worklog_list_data_str) if int(wl["issueId"]) in existing_ids
        ]
        _register_jira_uri(
            m,
            endpoint="worklog/list",
            return_value=json.dumps(worklog_filtered),
            HTTP_ACTION="POST",
        )
        # Get deleted
        worklog_deleted_data_str = get_fixture_file_data("api_responses/worklog_deleted.json")
        _register_jira_uri(
            m, endpoint="worklog/deleted?since=0", return_value=worklog_deleted_data_str
        )
        yield


def test_download_worklogs_schema():
    """
    worklogs is a simple function, so we just need a simple test
    """
    with worklogs_context_manager():
        worklog_dict = download_worklogs(get_jira_mock_connection(), [], datetime.min)

        # Assert schema of worklog dict object
        assert type(worklog_dict) == dict
        # Check existing
        assert "existing" in worklog_dict
        assert type(worklog_dict["existing"]) == list
        # Check deleted
        assert "deleted" in worklog_dict
        assert type(worklog_dict["deleted"]) == list


def test_download_worklogs_no_issues_to_search():
    """
    worklogs is a simple function, so we just need a simple test
    """
    with worklogs_context_manager():
        worklog_dict = download_worklogs(get_jira_mock_connection(), [], datetime.min)

        assert len(worklog_dict["existing"]) == 0
        assert worklog_dict["deleted"] == DELETED_WORKLOG_IDS


def test_download_worklogs_no_issues_to_search():
    """
    worklogs is a simple function, so we just need a simple test
    """
    ids = [11143, 11201]
    with worklogs_context_manager(ids):
        worklog_dict = download_worklogs(get_jira_mock_connection(), ids, datetime.min)

        assert len(worklog_dict["existing"]) == 4
        assert worklog_dict["deleted"] == DELETED_WORKLOG_IDS


def test_convert_datetime_to_worklog_timestamp():
    since_timestamp = _convert_datetime_to_worklog_timestamp(datetime.min)
    assert since_timestamp == 0

    a_day = datetime(1995, 12, 29)
    a_day_since_timestamp = _convert_datetime_to_worklog_timestamp(a_day)
    assert a_day.timestamp() * 1000 == a_day_since_timestamp

    b_day = datetime(1995, 12, 29, 3)
    b_day_since_timestamp = _convert_datetime_to_worklog_timestamp(b_day)
    assert b_day.timestamp() * 1000 == b_day_since_timestamp
