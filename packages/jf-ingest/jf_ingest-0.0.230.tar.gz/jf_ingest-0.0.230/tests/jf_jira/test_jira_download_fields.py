from contextlib import contextmanager

import requests_mock

from jf_ingest.jf_jira.downloaders import download_fields
from tests.jf_jira.utils import _register_jira_uri_with_file, get_jira_mock_connection


@contextmanager
def _field_context_manager():
    with requests_mock.Mocker() as m:
        _register_jira_uri_with_file(m, "field", f"api_responses/fields.json")
        yield


def test_get_fields_once():
    expected_field = {
        "id": "statuscategorychangedate",
        "key": "statuscategorychangedate",
        "name": "Status Category Changed",
        "custom": False,
        "orderable": False,
        "navigable": True,
        "searchable": True,
        "clauseNames": ["statusCategoryChangedDate"],
        "schema": {"type": "datetime", "system": "statuscategorychangedate"},
    }

    with _field_context_manager():
        fields = download_fields(
            jira_connection=get_jira_mock_connection(),
        )

    assert len(fields) == 4
    assert fields[0] == expected_field
    for field in fields:
        assert "id" in field.keys()
        assert "key" in field.keys()
        assert "name" in field.keys()