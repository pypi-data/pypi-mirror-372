import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Dict
from unittest.mock import patch

import pytest
import pytz
from requests import Request
import requests_mock
from jira import JIRAError

from jf_ingest.constants import Constants
from jf_ingest.jf_jira.downloaders import (
    IssueMetadata,
    _download_issue_page,
    _expand_changelog,
    _filter_changelogs,
    _get_all_project_issue_counts,
    _get_batch_size_with_jql_enhanced_search,
    _get_exact_count_via_pagination,
    _get_issue_count_for_jql,
    _get_issue_count_with_jql_enhanced_search,
    _post_raw_result_jql_enhanced,
    is_jql_enhanced_search_available,
    fetch_id_to_key_for_all_existing,
    generate_jql_for_batch_of_ids,
    generate_project_pull_from_bulk_jql,
    generate_project_pull_from_jql,
    get_fields_spec,
    get_issues_with_post_enhanced,
    get_jira_results_looped,
    get_jira_search_batch_size,
    pull_all_jira_issues_by_date,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.jf_jira.utils import JiraFieldIdentifier
from jf_ingest.utils import batch_iterable
from tests.jf_jira.utils import (
    _register_jira_uri,
    _register_jira_uri_with_file,
    get_jira_mock_connection,
)

logger = logging.getLogger(__name__)


def _generate_mock_address_for_issue_jql(
    m: requests_mock.Mocker,
    jql_query: str,
    issue_count: int,
    start_at: int,
    max_results: int,
    issues: list[dict],
):
    _issues = [issue for issue in issues[start_at : min(start_at + max_results, len(issues))]]
    jira_return_val = f'{{"expand":"names,schema","startAt":{start_at},"maxResults":{max_results},"total":{issue_count},"issues":{json.dumps(_issues)}}}'

    endpoint = (
        f"search?jql={jql_query}&startAt={start_at}&validateQuery=True&maxResults={max_results}"
    )
    _register_jira_uri(
        m,
        endpoint=endpoint,
        return_value=jira_return_val,
    )


def _mock_jira_issue_by_date_endpoints(
    m: requests_mock.Mocker,
    project_keys_to_issue_counts: dict[str, int],
    pull_from: datetime,
    batch_size: int,
    issues_updated_value: datetime = pytz.utc.localize(datetime.min),
    expand_fields: list[str] = ["*all"],
):
    def generate_issues(project_key, count):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.strftime("%Y-%m-%dT%H:%M:%S.000-0000")
        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog",
                "id": f"{i}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"{project_key}-{i}",
                "fields": _fields,
            }
            for i in range(count)
        ]

    for project_key, count in project_keys_to_issue_counts.items():
        issues = generate_issues(project_key=project_key, count=count)
        jql_query = generate_project_pull_from_jql(project_key=project_key, pull_from=pull_from)
        # Generate one call for getting hte 'first' page (for issue counts)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=count,
            start_at=0,
            issues=issues,
            max_results=1,
        )
        for start_at in range(0, count, batch_size):
            _generate_mock_address_for_issue_jql(
                m=m,
                jql_query=jql_query,
                issue_count=count,
                start_at=start_at,
                max_results=batch_size,
                issues=issues,
            )


def test_get_issue_count_for_jql():
    pull_from = datetime.min
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 5123
    project_key_to_count = {PROJECT_KEY: PROJECT_ISSUE_COUNT}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_key_to_count,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=generate_project_pull_from_jql(project_key=PROJECT_KEY, pull_from=pull_from),
        )
        assert count_for_jql == project_key_to_count[PROJECT_KEY]


def test_get_issue_count_for_jql_400_level_error_handling():
    """Assert that when we raise 400 level errors, we always return 0"""
    for status_code in range(400, 500):
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_status",
            side_effect=JIRAError(status_code=status_code),
        ):
            logger.info(
                f"Attempting to test _get_issue_count_for_jql when a {status_code} error is thrown"
            )
            count_for_jql = _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")
            assert count_for_jql == 0


def test_get_issue_count_for_jql_500_level_error_handling():
    for status_code in range(500, 600):
        logger.info(f"Checking to see if we raise 500 level errors...")
        with patch(
            "jf_ingest.jf_jira.downloaders.retry_for_status",
            side_effect=JIRAError(status_code=status_code),
        ):
            with pytest.raises(JIRAError):
                _get_issue_count_for_jql(get_jira_mock_connection(), jql_query="")


def test_get_all_project_issue_counts():
    pull_from = datetime.min
    project_keys_to_counts = {"PROJ": 151, "COLLAGE": 512}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_keys_to_counts,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        project_keys_to_pull_from = {
            project_key: pull_from for project_key in project_keys_to_counts.keys()
        }
        project_issue_counts = _get_all_project_issue_counts(
            get_jira_mock_connection(mocker),
            project_key_to_pull_from=project_keys_to_pull_from,
            num_parallel_threads=1,
            jql_filter=None,
        )

        assert project_issue_counts == project_keys_to_counts


def _mock_jira_issue_by_ids(
    m: requests_mock.Mocker(),
    issue_ids: list[str],
    batch_size: int,
    issues_updated_value: datetime = datetime.min,
    expand_fields: list[str] = ["*all"],
):
    def _generate_issues(ids_batch):
        _fields = {}
        if "*all" in expand_fields:
            _fields["updated"] = issues_updated_value.isoformat()
            _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}
        else:
            if "updated" in expand_fields:
                _fields["updated"] = issues_updated_value.isoformat()
            if "parent" in expand_fields:
                _fields["parent"] = {"id": "PARENT", "key": f"PROJ-PARENT"}

        return [
            {
                "expand": "operations,versionedRepresentations,editmeta,changelog",
                "id": f"{id}",
                "self": "https://test-co.atlassian.net/rest/api/2/issue/63847",
                "key": f"PROJ-{i}",
                "fields": _fields,
            }
            for i, id in enumerate(ids_batch)
        ]

    for id_batch in batch_iterable(sorted(issue_ids, key=int), batch_size=batch_size):
        jql_query = generate_jql_for_batch_of_ids(id_batch)
        _generate_mock_address_for_issue_jql(
            m=m,
            jql_query=jql_query,
            issue_count=len(id_batch),
            start_at=0,
            issues=_generate_issues(id_batch),
            max_results=batch_size,
        )
        
def test_generate_jql_for_batch_ids():
    ids = ["1", "2", "3", "4", "5"]
    jql_query = generate_jql_for_batch_of_ids(ids)
    assert jql_query == 'id in (1,2,3,4,5) order by id asc'
        
def test_generate_jql_for_batch_ids_with_pull_from():
    ids = ["1", "2", "3", "4", "5"]
    pull_from = datetime(2024, 12, 29, 17, 20, 1)
    jql_query = generate_jql_for_batch_of_ids(ids, pull_from)
    assert jql_query == 'id in (1,2,3,4,5) AND updated > "2024-12-29" order by id asc'


def test_get_jira_batch_size():
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            # Check when fields is left out (it should default to [*all])
            jira_issues_batch_size = get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )

            assert jira_issues_batch_size == jira_batch_size_return


def test_get_jira_batch_size_with_variable_field_argument():
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            # Check when fields is left out (it should default to [*all])
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )

            def _get_request_body():
                return json.loads(mocker.request_history[-1]._request.body)

            print(json.loads(mocker.request_history[-1]._request.body)['fields'])
            assert _get_request_body()['fields'] == ['*all']

            # Check when fields is set to ['id', 'key']
            fields = ['key', 'id']
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
                fields=fields,
            )

            assert _get_request_body()['fields'] == fields

            # Check when fields is set to ['*all'] manually
            fields = ['*all']
            get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
                fields=fields,
            )
            assert _get_request_body()['fields'] == fields


def test_get_jira_batch_size_with_jql_enhanced_search():
    """Test get_jira_search_batch_size with JQL Enhanced Search API."""
    optimistic_batch_size = 1000
    
    # Test ID-only fields with JQL Enhanced Search
    batch_size = get_jira_search_batch_size(
        jira_connection=None,  # Not used when use_jql_enhanced_search=True
        optimistic_batch_size=optimistic_batch_size,
        fields=['id'],
        use_jql_enhanced_search=True,
    )
    assert batch_size == 5000  # ID-only queries use higher limit
    
    # Test ID and key fields with JQL Enhanced Search
    batch_size = get_jira_search_batch_size(
        jira_connection=None,  # Not used when use_jql_enhanced_search=True
        optimistic_batch_size=optimistic_batch_size,
        fields=['id', 'key'],
        use_jql_enhanced_search=True,
    )
    assert batch_size == 5000  # ID-only queries use higher limit
    
    # Test full fields with JQL Enhanced Search
    batch_size = get_jira_search_batch_size(
        jira_connection=None,  # Not used when use_jql_enhanced_search=True
        optimistic_batch_size=optimistic_batch_size,
        fields=['*all'],
        use_jql_enhanced_search=True,
    )
    assert batch_size == 100  # Full issue queries use lower limit
    
    # Test with optimistic batch size smaller than default
    batch_size = get_jira_search_batch_size(
        jira_connection=None,  # Not used when use_jql_enhanced_search=True
        optimistic_batch_size=50,
        fields=['*all'],
        use_jql_enhanced_search=True,
    )
    assert batch_size == 50  # Should use the smaller optimistic batch size


def test_get_jira_batch_size_legacy_api_unchanged():
    """Test that legacy API behavior is unchanged when use_jql_enhanced_search=False."""
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":{returned_batch_size},"total":0,"issues":[]}}'

            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield mocker

    optimistic_batch_size = 1000
    for jira_batch_size_return in [0, 10, Constants.MAX_ISSUE_API_BATCH_SIZE, 1000, 1235]:
        with _mocked_jira_return(
            requested_batch_size=optimistic_batch_size,
            returned_batch_size=jira_batch_size_return,
        ) as mocker:
            # Test with use_jql_enhanced_search=False (default)
            jira_issues_batch_size = get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
                use_jql_enhanced_search=False,
            )
            assert jira_issues_batch_size == jira_batch_size_return
            
            # Test with default parameter (should be False)
            jira_issues_batch_size_default = get_jira_search_batch_size(
                jira_connection=get_jira_mock_connection(mocker),
                optimistic_batch_size=optimistic_batch_size,
            )
            assert jira_issues_batch_size_default == jira_batch_size_return


def test_get_fields_spec():
    assert get_fields_spec(include_fields=[], exclude_fields=[]) == ["*all"]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=[]) == ["updated"]
    assert get_fields_spec(include_fields=["updated", "parent"], exclude_fields=[]) == [
        "updated",
        "parent",
    ]
    assert get_fields_spec(include_fields=["updated"], exclude_fields=["parent"]) == [
        "updated",
        "-parent",
    ]


def get_issues_through_test_fixture():
    issue_ids = sorted(["18447", "18404", "18031", "18018", "18016"], key=int)
    jql_query = generate_jql_for_batch_of_ids(issue_ids)
    with requests_mock.Mocker() as m:
        # Register one endpoint that this will hit
        uri = f"search?jql={jql_query}&startAt=0&validateQuery=True&fields=%2Aall&expand=changelog&maxResults=5"
        _register_jira_uri_with_file(m, endpoint=uri, fixture_path="api_responses/issues.json")

        return [
            i
            for i in pull_jira_issues_by_jira_ids(
                jira_connection=get_jira_mock_connection(),
                jira_ids=issue_ids,
                num_parallel_threads=10,
                batch_size=len(issue_ids),
                expand_fields=["changelog"],
                include_fields=[],
                exclude_fields=[],
            )
        ]

CUSTOM_FIELDS_FOR_FILTERING = tuple(["customfield_10051", "customfield_10057", "customfield_10009"])
JFI_FIELDS_FOR_FILTERING = tuple([
    JiraFieldIdentifier(jira_field_id=jira_id, jira_field_name=f'Name: {jira_id}')
    for jira_id in CUSTOM_FIELDS_FOR_FILTERING
])
def test_filter_changelogs_no_filtering():
    issues = get_issues_through_test_fixture()
    issues_without_filtering = _filter_changelogs(issues, [], [])

    for issue in issues_without_filtering:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) != 0
            for item in history["items"]:
                if "fieldId" in item:
                    assert item["fieldId"] in CUSTOM_FIELDS_FOR_FILTERING


def test_filter_changelogs_inclusion_filtering_for_madeup_field():
    issues = get_issues_through_test_fixture()
    issues_with_filtering_field_in = _filter_changelogs(issues, [JiraFieldIdentifier(jira_field_id="madeup_field", jira_field_name='Made up Field')], [])
    assert len(issues) == len(issues_with_filtering_field_in)
    for issue in issues_with_filtering_field_in:
        for history in issue["changelog"]["histories"]:
            assert len(history["items"]) == 0

def test_filter_changelogs_exclusion_filtering_for_madeup_field():
    issues = get_issues_through_test_fixture()
    issues_with_filtering_field_in = _filter_changelogs(issues, [], [JiraFieldIdentifier(jira_field_id="madeup_field", jira_field_name='Made up Field')])
    assert len(issues) == len(issues_with_filtering_field_in)
    for issue, filtered_issue in zip(issues, issues_with_filtering_field_in):
        assert len(issue['changelog']['histories']) == len(filtered_issue['changelog']['histories'])
        for history, filtered_history in zip(issue["changelog"]["histories"], filtered_issue['changelog']['histories']):
            assert len(history["items"]) == len(filtered_history['items'])

def test_filter_changelogs_inclusion_filtering_by_id():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'fieldId': field_id_1,
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    include_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_1, jira_field_name=field_name_1)
    ]
    filtered_issue = _filter_changelogs([issue], include_fields, [])[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['fieldId'] == field_id_1
        
def test_filter_changelogs_inclusion_filtering_by_name():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    include_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_1, jira_field_name=field_name_1)
    ]
    filtered_issue = _filter_changelogs([issue], include_fields, [])[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['field'] == field_name_1
        
def test_filter_changelogs_exclusion_filtering_by_id():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                                'fieldId': field_id_1
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    exclude_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_2, jira_field_name=field_name_2)
    ]
    filtered_issue = _filter_changelogs([issue], [], exclude_fields)[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['fieldId'] == field_id_1
        
def test_filter_changelogs_exclusion_filtering_by_name():
    field_id_1 = 'FIELD_ID_1'
    field_name_1 = 'FIELD NAME 1'
    field_id_2 = 'FIELD_ID_2'
    field_name_2 = 'FIELD NAME 2'
    issue = {
            'changelog': {
                'histories': [
                        {
                        'items': [
                            {
                                'field': field_name_1,
                            },
                            {
                                'fieldId': field_id_2,
                                'field': field_name_2,
                            }
                        ]
                    }
                ]
            }
        }
    exclude_fields = [
        JiraFieldIdentifier(jira_field_id=field_id_2, jira_field_name=field_name_2)
    ]
    filtered_issue = _filter_changelogs([issue], [], exclude_fields)[0]
    print(filtered_issue)
    for history in filtered_issue["changelog"]["histories"]:
        assert len(history["items"]) == 1
        assert history['items'][0]['field'] == field_name_1

@pytest.mark.skip(reason="need to mock serverInfo endpoint too")
def test_expand_changelog():
    total_changelog_histories = 5
    batch_size = 1

    def _mock_api_endpoint_for_changelog(m: requests_mock.Mocker, change_log_num: int):
        mock_return = {
            "self": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=1",
            "nextPage": "https://test-co.atlassian.net/rest/api/2/issue/TS-4/changelog?maxResults=1&startAt=2",
            "maxResults": batch_size,
            "startAt": change_log_num - 1,
            "total": total_changelog_histories,
            "isLast": False,
            "values": [
                {
                    "id": f"{change_log_num}",
                    "author": {},
                    "created": "2020-06-29T16:01:51.141-0400",
                    "items": [
                        {
                            "field": "Spelunking CustomField v2",
                            "fieldtype": "custom",
                            "fieldId": "customfield_10057",
                            "from": None,
                            "fromString": None,
                            "to": "10072",
                            "toString": "hello",
                        }
                    ],
                }
            ],
        }
        _register_jira_uri(
            m,
            endpoint=f"issue/1/changelog?startAt={change_log_num - 1}&maxResults={batch_size}",
            return_value=json.dumps(mock_return),
        )

    with requests_mock.Mocker() as m:
        for change_log_num in range(0, total_changelog_histories + 1):
            _mock_api_endpoint_for_changelog(m, change_log_num)
        spoofed_issue_raw: dict = {
            "id": "1",
            "key": "spoof-1",
            "changelog": {
                "total": total_changelog_histories,
                "maxResults": 0,
                "histories": [],
            },
        }

        spoofed_issue_no_more_results_raw: dict = {
            "id": "2",
            "key": "spoof-2",
            "changelog": {"total": 0, "maxResults": 0, "histories": []},
        }

        _expand_changelog(
            get_jira_mock_connection(),
            jira_issues=[spoofed_issue_raw, spoofed_issue_no_more_results_raw],
            batch_size=1,
        )

        assert len(spoofed_issue_raw["changelog"]["histories"]) == total_changelog_histories
        assert len(spoofed_issue_no_more_results_raw["changelog"]["histories"]) == 0


@contextmanager
def _mock_for_full_issue_test(
    jf_issue_metadata: list[IssueMetadata],
    project_key: str = "PROJ",
    pull_from: datetime = datetime.min,
    issues_updated_value: datetime = datetime(2020, 1, 1),
    batch_size: int = Constants.MAX_ISSUE_API_BATCH_SIZE,
):
    expand_fields = ["*all"]

    with requests_mock.Mocker() as mocker:
        # Register the 'Batch Size' query return
        _register_jira_uri(
            mocker,
            endpoint=f"search?jql=&startAt=0&validateQuery=True&fields=%2Aall&maxResults={Constants.MAX_ISSUE_API_BATCH_SIZE}",
            return_value=f'{{"expand":"schema,names","startAt":0,"maxResults":{batch_size},"total":{len(jf_issue_metadata)},"issues":[]}}',
        )

        # Register the 'pull from' dates
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts={project_key: len(jf_issue_metadata)},
            pull_from=pull_from,
            issues_updated_value=issues_updated_value,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )

        _mock_jira_issue_by_ids(
            m=mocker,
            issue_ids=[
                issue_metadata.id
                for issue_metadata in jf_issue_metadata
                if issues_updated_value > issue_metadata.updated
            ],
            batch_size=batch_size,
            issues_updated_value=issues_updated_value,
            expand_fields=expand_fields,
        )
        yield mocker


def test_download_issue_page_ensure_error_never_raised():
    """
    The _download_issue_page should NEVER raise an error.
    """
    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_status",
        side_effect=JIRAError(status_code=500),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0

    with patch(
        "jf_ingest.jf_jira.downloaders.retry_for_status",
        side_effect=Exception('random exception'),
    ):
        issues = _download_issue_page(
            jira_connection=get_jira_mock_connection(), jql_query='', start_at=0, batch_size=100
        )
        assert len(issues) == 0

def test_download_issue_page_ensure_fields_not_ignored():
    """
    The _download_issue_page should NEVER raise an error.
    """
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":0,"total":0,"issues":[]}}'
            jira_mock_connection = get_jira_mock_connection(mocker)
            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield jira_mock_connection, mocker
    
    with _mocked_jira_return(requested_batch_size=0, returned_batch_size=0) as (jira_conn, mocker):
        _download_issue_page(
            jira_connection=jira_conn, jql_query='', start_at=0, batch_size=0, expand_fields=[], include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='ID')
            ]
        )
        print(vars(mocker.request_history[0]))
        post_found = False
        for request in mocker.request_history:
            request: Request = request._request
            if request.method == 'POST':
                post_found = True
                request_body = json.loads(request.body)
                assert request_body['fields'] == ['id']
        assert post_found
        
def test_download_issue_page_ensure_fields_not_ignored_more():
    """
    The _download_issue_page should NEVER raise an error.
    """
    @contextmanager
    def _mocked_jira_return(requested_batch_size: int, returned_batch_size: int):
        with requests_mock.Mocker() as mocker:
            jira_return_val = f'{{"expand":"names,schema","startAt":0,"maxResults":0,"total":0,"issues":[]}}'
            jira_mock_connection = get_jira_mock_connection(mocker)
            _register_jira_uri(
                mocker,
                endpoint=f"search",
                return_value=jira_return_val,
                HTTP_ACTION='POST',
            )
            yield jira_mock_connection, mocker
    
    with _mocked_jira_return(requested_batch_size=0, returned_batch_size=0) as (jira_conn, mocker):
        _download_issue_page(
            jira_connection=jira_conn, jql_query='', start_at=0, batch_size=0, expand_fields=[], include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='ID'),
                JiraFieldIdentifier(jira_field_id='customfield_101234', jira_field_name='Sprint'),
                JiraFieldIdentifier(jira_field_id='customfield_201244', jira_field_name='Thing'),
            ]
        )
        print(vars(mocker.request_history[0]))
        post_found = False
        for request in mocker.request_history:
            request: Request = request._request
            if request.method == 'POST':
                post_found = True
                request_body = json.loads(request.body)
                assert request_body['fields'] == ['id', 'customfield_101234', 'customfield_201244']
        assert post_found

def test_generate_project_pull_from_bulk_jql_base():
    project_keys = ['A', 'B', 'C', 'D', 'E', 'F']
    project_key_to_pull_from = {
        'A': datetime(2024, 10, 1),
        'B': datetime(2024, 10, 2),
        'C': datetime(2024, 10, 3),
        'D': datetime(2024, 10, 4),
        'E': datetime(2024, 10, 5),
        'F': datetime(2024, 10, 6),
    }
    jql_filters = [
        generate_project_pull_from_bulk_jql(project_keys=project_key_batch, project_key_to_pull_from=project_key_to_pull_from)
        for project_key_batch in batch_iterable(project_keys, batch_size=3)
    ]
    
    assert len(jql_filters) == 2
    assert jql_filters[0] == '(project = A AND updated > "2024-10-01") OR (project = B AND updated > "2024-10-02") OR (project = C AND updated > "2024-10-03") order by id asc'
    assert jql_filters[1] == '(project = D AND updated > "2024-10-04") OR (project = E AND updated > "2024-10-05") OR (project = F AND updated > "2024-10-06") order by id asc'

def test_generate_project_pull_from_bulk_jql_with_issue_filter():
    project_keys = ['A', 'B', 'C', 'D', 'E', 'F']
    project_key_to_pull_from = {
        'A': datetime(2024, 10, 1),
        'B': datetime(2024, 10, 2),
        'C': datetime(2024, 10, 3),
        'D': datetime(2024, 10, 4),
        'E': datetime(2024, 10, 5),
        'F': datetime(2024, 10, 6),
    }
    jql_filter = generate_project_pull_from_bulk_jql(project_keys=project_keys, project_key_to_pull_from=project_key_to_pull_from, jql_filter='issuetype != "Secret Type"')
    assert jql_filter == (
        '(project = A AND updated > "2024-10-01") OR (project = B AND updated > "2024-10-02") OR (project = C AND updated > "2024-10-03") OR (project = D AND updated > "2024-10-04") OR (project = E AND updated > "2024-10-05") OR (project = F AND updated > "2024-10-06") AND (issuetype != "Secret Type") order by id asc'
    )


def test_is_jql_enhanced_search_available_success():
    """Test that is_jql_enhanced_search_available returns True when /search/jql endpoint returns 200"""
    with requests_mock.Mocker() as mocker:
        # Mock successful response from /search/jql endpoint
        jira_return_val = '{"maxResults": 1, "nextPageToken": "eyJzdGFydEF0IjoxfQ==", "issues": []}'
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=jira_return_val,
            HTTP_ACTION='POST',
            status_code=200,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = is_jql_enhanced_search_available(jira_connection)
        assert result is True


def test_is_jql_enhanced_search_available_not_found():
    """Test that is_jql_enhanced_search_available returns False when /search/jql endpoint returns 404"""
    with requests_mock.Mocker() as mocker:
        # Mock 404 response from /search/jql endpoint
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value='{"errorMessages":["Not Found"]}',
            HTTP_ACTION='POST',
            status_code=404,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = is_jql_enhanced_search_available(jira_connection)
        assert result is False


def test_is_jql_enhanced_search_available_server_error():
    """Test that is_jql_enhanced_search_available returns False when /search/jql endpoint returns 500 (conservative fallback)"""
    with requests_mock.Mocker() as mocker:
        # Mock 500 response from /search/jql endpoint
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value='{"errorMessages":["Internal Server Error"]}',
            HTTP_ACTION='POST',
            status_code=500,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = is_jql_enhanced_search_available(jira_connection)
        assert result is False


def test_is_jql_enhanced_search_available_auth_error():
    """Test that is_jql_enhanced_search_available returns False when /search/jql endpoint returns 401 (conservative fallback)"""
    with requests_mock.Mocker() as mocker:
        # Mock 401 response from /search/jql endpoint
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value='{"errorMessages":["Unauthorized"]}',
            HTTP_ACTION='POST',
            status_code=401,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = is_jql_enhanced_search_available(jira_connection)
        assert result is False


def test_is_jql_enhanced_search_available_network_exception():
    """Test that is_jql_enhanced_search_available returns False when network exception occurs"""
    import requests
    with requests_mock.Mocker() as mocker:
        # Mock network exception
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            exc=requests.exceptions.ConnectTimeout
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = is_jql_enhanced_search_available(jira_connection)
        assert result is False



    

def test_post_raw_result_jql_enhanced_success():
    """Test that _post_raw_result_jql_enhanced successfully calls the /search/jql endpoint"""
    with requests_mock.Mocker() as mocker:
        # Mock successful response from /search/jql endpoint
        mock_response = {
            "maxResults": 5000,
            "nextPageToken": "eyJzdGFydEF0IjoxMDAwfQ==",
            "issues": [{"id": "1", "key": "TEST-1"}, {"id": "2", "key": "TEST-2"}]
        }
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=json.dumps(mock_response),
            HTTP_ACTION='POST',
            status_code=200,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _post_raw_result_jql_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id", "key"],
            expand=[],
            max_results=5000,
            next_page_token=None
        )
        
        assert result == mock_response
        assert result["maxResults"] == 5000
        assert result["nextPageToken"] == "eyJzdGFydEF0IjoxMDAwfQ=="
        assert len(result["issues"]) == 2


def test_post_raw_result_jql_enhanced_with_next_page_token():
    """Test that _post_raw_result_jql_enhanced correctly includes nextPageToken in request"""
    with requests_mock.Mocker() as mocker:
        # Mock successful response from /search/jql endpoint
        mock_response = {
            "maxResults": 5000,
            "issues": [{"id": "3", "key": "TEST-3"}]
        }
        
        def request_callback(request, context):
            # Verify that nextPageToken is included in the request
            request_data = json.loads(request.text)
            assert request_data["nextPageToken"] == "eyJzdGFydEF0IjoxMDAwfQ=="
            assert request_data["jql"] == "project = TEST"
            assert request_data["maxResults"] == 2500
            context.status_code = 200
            return json.dumps(mock_response)
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=request_callback
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _post_raw_result_jql_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id"],
            expand=[],
            max_results=2500,
            next_page_token="eyJzdGFydEF0IjoxMDAwfQ=="
        )
        
        assert result == mock_response


def test_post_raw_result_jql_enhanced_retry_on_error():
    """Test that _post_raw_result_jql_enhanced retries on server errors"""
    with requests_mock.Mocker() as mocker:
        # First call returns 500, second call succeeds
        mock_response = {"maxResults": 5000, "issues": []}
        
        call_count = 0
        def request_callback(request, context):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                context.status_code = 500
                return '{"errorMessages":["Internal Server Error"]}'
            else:
                context.status_code = 200
                return json.dumps(mock_response)
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=request_callback
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _post_raw_result_jql_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id"],
            expand=[],
            max_results=5000,
            next_page_token=None
        )
        
        assert result == mock_response
        assert call_count == 2  # Verify retry occurred


def test_get_issue_count_with_jql_enhanced_search_approximate_success():
    """Test that _get_issue_count_with_jql_enhanced_search uses approximate count when available"""
    with requests_mock.Mocker() as mocker:
        # Mock successful approximate count response (now uses POST)
        _register_jira_uri(
            mocker,
            endpoint="search/approximate-count",
            return_value='{"approximateCount": 1247}',
            HTTP_ACTION='POST',
            status_code=200,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_issue_count_with_jql_enhanced_search(jira_connection, "project = TEST")
        
        assert result == 1247


def test_get_issue_count_with_jql_enhanced_search_fallback_to_pagination():
    """Test that _get_issue_count_with_jql_enhanced_search falls back to pagination when approximate count fails"""
    with requests_mock.Mocker() as mocker:
        # Mock failed approximate count response
        _register_jira_uri(
            mocker,
            endpoint="search/approximate-count",
            return_value='{"errorMessages":["Not supported"]}',
            HTTP_ACTION='GET',
            status_code=404,
        )
        
        # Mock pagination responses for exact counting
        # First page: 5000 issues with nextPageToken
        first_page_response = {
            "maxResults": 5000,
            "nextPageToken": "eyJzdGFydEF0Ijo1MDAwfQ==",
            "issues": [{"id": str(i)} for i in range(1, 5001)]  # 5000 issues
        }
        
        # Second page: 2500 issues, no nextPageToken (end of results)
        second_page_response = {
            "maxResults": 5000,
            "issues": [{"id": str(i)} for i in range(5001, 7501)]  # 2500 issues
        }
        
        call_count = 0
        def jql_request_callback(request, context):
            nonlocal call_count
            call_count += 1
            request_data = json.loads(request.text)
            
            if call_count == 1:
                # First call should have no nextPageToken
                assert "nextPageToken" not in request_data
                context.status_code = 200
                return json.dumps(first_page_response)
            else:
                # Second call should have nextPageToken
                assert request_data["nextPageToken"] == "eyJzdGFydEF0Ijo1MDAwfQ=="
                context.status_code = 200
                return json.dumps(second_page_response)
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=jql_request_callback
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_issue_count_with_jql_enhanced_search(jira_connection, "project = TEST")
        
        assert result == 7500  # 5000 + 2500
        assert call_count == 2  # Verify both pagination calls occurred


def test_get_issue_count_with_jql_enhanced_search_single_page():
    """Test that _get_issue_count_with_jql_enhanced_search handles single page results correctly"""
    with requests_mock.Mocker() as mocker:
        # Mock failed approximate count response
        _register_jira_uri(
            mocker,
            endpoint="search/approximate-count",
            return_value='{"errorMessages":["Not supported"]}',
            HTTP_ACTION='GET',
            status_code=404,
        )
        
        # Mock single page response (no nextPageToken)
        single_page_response = {
            "maxResults": 5000,
            "issues": [{"id": str(i)} for i in range(1, 101)]  # 100 issues
        }
        
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=json.dumps(single_page_response),
            HTTP_ACTION='POST',
            status_code=200,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_issue_count_with_jql_enhanced_search(jira_connection, "project = TEST")
        
        assert result == 100


def test_get_batch_size_with_jql_enhanced_search_id_only():
    """Test that _get_batch_size_with_jql_enhanced_search returns 5000 for ID-only queries"""
    result = _get_batch_size_with_jql_enhanced_search(['id'], 10000)
    assert result == 5000
    
    result = _get_batch_size_with_jql_enhanced_search(['id', 'key'], 10000)
    assert result == 5000


def test_get_batch_size_with_jql_enhanced_search_full_issue_queries():
    """Test that _get_batch_size_with_jql_enhanced_search returns min(optimistic_batch_size, 100) for full issue queries"""
    # Test with many fields - should return min(optimistic_batch_size, 100)
    many_fields = ['id', 'key', 'summary', 'status', 'assignee', 'reporter']
    result = _get_batch_size_with_jql_enhanced_search(many_fields, 10000)
    assert result == 100
    
    # Test with few fields - should still return min(optimistic_batch_size, 100)
    few_fields = ['summary', 'status']
    result = _get_batch_size_with_jql_enhanced_search(few_fields, 10000)
    assert result == 100


def test_get_batch_size_with_jql_enhanced_search_respects_optimistic_limit():
    """Test that _get_batch_size_with_jql_enhanced_search behavior matches design specification"""
    # For ID queries, design shows hard-coded 5000 (doesn't respect optimistic_batch_size)
    result = _get_batch_size_with_jql_enhanced_search(['id'], 1000)
    assert result == 5000  # Design shows hard-coded 5000 for ID queries
    
    # For full issue queries, should return min(optimistic_batch_size, 100)
    result = _get_batch_size_with_jql_enhanced_search(['summary', 'status'], 50)
    assert result == 50  # Should respect the lower optimistic limit


def test_get_batch_size_with_jql_enhanced_search_with_iterable():
    """Test that _get_batch_size_with_jql_enhanced_search works with different iterable types"""
    # Test with tuple for ID queries
    result = _get_batch_size_with_jql_enhanced_search(('id', 'key'), 10000)
    assert result == 5000
    
    # Test with set for ID queries
    result = _get_batch_size_with_jql_enhanced_search({'id'}, 10000)
    assert result == 5000
    
    # Test with tuple for full issue queries
    result = _get_batch_size_with_jql_enhanced_search(('summary', 'status'), 10000)
    assert result == 100


def test_get_exact_count_via_pagination_single_page():
    """Test that _get_exact_count_via_pagination handles single page results correctly"""
    with requests_mock.Mocker() as mocker:
        # Mock single page response (no nextPageToken)
        single_page_response = {
            "maxResults": 5000,
            "issues": [{"id": str(i)} for i in range(1, 101)]  # 100 issues
        }
        
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=json.dumps(single_page_response),
            HTTP_ACTION='POST',
            status_code=200,
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_exact_count_via_pagination(jira_connection, "project = TEST")
        
        assert result == 100


def test_get_exact_count_via_pagination_multiple_pages():
    """Test that _get_exact_count_via_pagination handles multiple pages correctly"""
    with requests_mock.Mocker() as mocker:
        # Mock pagination responses
        # First page: 5000 issues with nextPageToken
        first_page_response = {
            "maxResults": 5000,
            "nextPageToken": "eyJzdGFydEF0Ijo1MDAwfQ==",
            "issues": [{"id": str(i)} for i in range(1, 5001)]  # 5000 issues
        }
        
        # Second page: 2500 issues, no nextPageToken (end of results)
        second_page_response = {
            "maxResults": 5000,
            "issues": [{"id": str(i)} for i in range(5001, 7501)]  # 2500 issues
        }
        
        call_count = 0
        def jql_request_callback(request, context):
            nonlocal call_count
            call_count += 1
            request_data = json.loads(request.text)
            
            if call_count == 1:
                # First call should have no nextPageToken
                assert "nextPageToken" not in request_data
                context.status_code = 200
                return json.dumps(first_page_response)
            else:
                # Second call should have nextPageToken
                assert request_data["nextPageToken"] == "eyJzdGFydEF0Ijo1MDAwfQ=="
                context.status_code = 200
                return json.dumps(second_page_response)
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=jql_request_callback
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_exact_count_via_pagination(jira_connection, "project = TEST")
        
        assert result == 7500  # 5000 + 2500
        assert call_count == 2  # Verify both pagination calls occurred


def test_get_exact_count_via_pagination_uses_batch_size_function():
    """Test that _get_exact_count_via_pagination uses _get_batch_size_with_jql_enhanced_search"""
    with requests_mock.Mocker() as mocker:
        # Mock response
        mock_response = {
            "maxResults": 5000,
            "issues": [{"id": "1"}]
        }
        
        def jql_request_callback(request, context):
            request_data = json.loads(request.text)
            # Verify that maxResults matches what _get_batch_size_with_jql_enhanced_search returns for ['id']
            # According to our implementation, it should return 5000 for ID-only queries
            assert request_data["maxResults"] == 5000
            assert request_data["fields"] == ["id"]
            context.status_code = 200
            return json.dumps(mock_response)
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=jql_request_callback
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = _get_exact_count_via_pagination(jira_connection, "project = TEST")
        
        assert result == 1


def test_get_issue_count_for_jql_with_legacy_api():
    """Test that _get_issue_count_for_jql works correctly with legacy API (use_jql_enhanced_search=False)"""
    pull_from = datetime.min
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 5123
    project_key_to_count = {PROJECT_KEY: PROJECT_ISSUE_COUNT}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_key_to_count,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=generate_project_pull_from_jql(project_key=PROJECT_KEY, pull_from=pull_from),
            use_jql_enhanced_search=False,  # Explicitly test legacy API
        )
        assert count_for_jql == project_key_to_count[PROJECT_KEY]


def test_get_issue_count_for_jql_with_jql_enhanced_search():
    """Test that _get_issue_count_for_jql works correctly with JQL Enhanced Search API (use_jql_enhanced_search=True)"""
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 2500
    jql_query = f"project = {PROJECT_KEY}"

    with requests_mock.Mocker() as mocker:
        # Mock the approximate count endpoint (now uses POST)
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/approximate-count',
            json={'approximateCount': PROJECT_ISSUE_COUNT}
        )
        
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=jql_query,
            use_jql_enhanced_search=True,  # Test JQL Enhanced Search API
        )
        assert count_for_jql == PROJECT_ISSUE_COUNT


def test_get_issue_count_for_jql_jql_enhanced_search_fallback_to_pagination():
    """Test that _get_issue_count_for_jql falls back to pagination when approximate count fails"""
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 1500
    jql_query = f"project = {PROJECT_KEY}"

    with requests_mock.Mocker() as mocker:
        # Mock approximate count endpoint to fail
        mocker.register_uri(
            'GET',
            'https://test-co.atlassian.net/rest/api/2/search/approximate-count',
            status_code=404
        )
        
        # Mock JQL Enhanced Search endpoint for pagination fallback
        def jql_request_callback(request, context):
            request_data = json.loads(request.text)
            max_results = request_data.get('maxResults', 5000)
            
            # Return first page with issues
            return json.dumps({
                'issues': [{'id': str(i)} for i in range(1, min(max_results + 1, PROJECT_ISSUE_COUNT + 1))],
                'maxResults': max_results
                # No nextPageToken means this is the only page
            })
        
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            text=jql_request_callback
        )
        
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=jql_query,
            use_jql_enhanced_search=True,  # Test JQL Enhanced Search API with fallback
        )
        assert count_for_jql == PROJECT_ISSUE_COUNT


def test_get_issue_count_for_jql_backward_compatibility():
    """Test that _get_issue_count_for_jql maintains backward compatibility when called without use_jql_enhanced_search parameter"""
    pull_from = datetime.min
    PROJECT_KEY = "PROJ"
    PROJECT_ISSUE_COUNT = 3456
    project_key_to_count = {PROJECT_KEY: PROJECT_ISSUE_COUNT}

    with requests_mock.Mocker() as mocker:
        _mock_jira_issue_by_date_endpoints(
            m=mocker,
            project_keys_to_issue_counts=project_key_to_count,
            pull_from=pull_from,
            batch_size=Constants.MAX_ISSUE_API_BATCH_SIZE,
        )
        # Call without use_jql_enhanced_search parameter - should default to False (legacy API)
        count_for_jql = _get_issue_count_for_jql(
            get_jira_mock_connection(mocker),
            jql_query=generate_project_pull_from_jql(project_key=PROJECT_KEY, pull_from=pull_from),
        )
        assert count_for_jql == project_key_to_count[PROJECT_KEY]


def test_get_issue_count_for_jql_error_handling_with_jql_enhanced_search():
    """Test that _get_issue_count_for_jql properly handles errors when using JQL Enhanced Search API"""
    jql_query = "project = TEST"
    
    # Test that JIRAError from helper function is properly propagated
    with patch(
        "jf_ingest.jf_jira.downloaders._get_issue_count_with_jql_enhanced_search",
        side_effect=JIRAError(status_code=500),
    ):
        with pytest.raises(JIRAError):
            _get_issue_count_for_jql(
                get_jira_mock_connection(), 
                jql_query=jql_query,
                use_jql_enhanced_search=True
            )


def test_get_issues_with_post_enhanced_success():
    """Test that get_issues_with_post_enhanced successfully calls the JQL Enhanced Search API"""
    with requests_mock.Mocker() as mocker:
        # Mock successful response from /search/jql endpoint
        mock_response = {
            "issues": [
                {"id": "1", "key": "TEST-1"},
                {"id": "2", "key": "TEST-2"}
            ],
            "nextPageToken": "eyJzdGFydEF0IjoyMDB9"
        }
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            json=mock_response,
            status_code=200
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        issues, total, next_token = get_issues_with_post_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id", "key"],
            expand=[],
            max_results=100
        )
        
        assert len(issues) == 2
        assert total == 2  # Should be len(issues)
        assert next_token == "eyJzdGFydEF0IjoyMDB9"
        assert issues[0]["id"] == "1"
        assert issues[1]["key"] == "TEST-2"


def test_get_issues_with_post_enhanced_with_next_page_token():
    """Test that get_issues_with_post_enhanced correctly passes nextPageToken to the API"""
    with requests_mock.Mocker() as mocker:
        # Mock successful response from /search/jql endpoint
        mock_response = {
            "issues": [
                {"id": "3", "key": "TEST-3"}
            ]
            # No nextPageToken - indicates last page
        }
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            json=mock_response,
            status_code=200
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        issues, total, next_token = get_issues_with_post_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id", "key"],
            expand=[],
            max_results=100,
            next_page_token="eyJzdGFydEF0IjoyMDB9"
        )
        
        # Verify the request included the nextPageToken
        request_data = json.loads(mocker.last_request.text)
        assert request_data["nextPageToken"] == "eyJzdGFydEF0IjoyMDB9"
        
        assert len(issues) == 1
        assert total == 1
        assert next_token is None  # No more pages
        assert issues[0]["id"] == "3"


def test_get_issues_with_post_enhanced_empty_response():
    """Test that get_issues_with_post_enhanced handles empty responses correctly"""
    with requests_mock.Mocker() as mocker:
        # Mock empty response from /search/jql endpoint
        mock_response = {
            "issues": []
            # No nextPageToken - indicates no more results
        }
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            json=mock_response,
            status_code=200
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        issues, total, next_token = get_issues_with_post_enhanced(
            jira_connection=jira_connection,
            jql_query="project = EMPTY",
            fields=["id"],
            expand=[],
            max_results=100
        )
        
        assert len(issues) == 0
        assert total == 0
        assert next_token is None


def test_get_issues_with_post_enhanced_consistent_return_signature():
    """Test that get_issues_with_post_enhanced always returns exactly 3 values"""
    with requests_mock.Mocker() as mocker:
        # Mock response with various scenarios
        mock_response = {
            "issues": [{"id": "1", "key": "TEST-1"}],
            "nextPageToken": "token123"
        }
        mocker.register_uri(
            'POST',
            'https://test-co.atlassian.net/rest/api/2/search/jql',
            json=mock_response,
            status_code=200
        )
        
        jira_connection = get_jira_mock_connection(mocker)
        result = get_issues_with_post_enhanced(
            jira_connection=jira_connection,
            jql_query="project = TEST",
            fields=["id", "key"],
            expand=[],
            max_results=100
        )
        
        # Verify it always returns exactly 3 values
        assert isinstance(result, tuple)
        assert len(result) == 3
        issues, total, next_token = result
        assert isinstance(issues, list)
        assert isinstance(total, int)
        assert (next_token is None) or isinstance(next_token, str)


def test_download_issue_page_with_legacy_api():
    """Test that _download_issue_page works correctly with legacy API (use_jql_enhanced_search=False)"""
    with requests_mock.Mocker() as mocker:
        # Mock legacy API response
        mock_response = {
            "expand": "names,schema",
            "startAt": 0,
            "maxResults": 100,
            "total": 1,
            "issues": [{"id": "1", "key": "TEST-1"}]
        }
        jira_mock_connection = get_jira_mock_connection(mocker)
        _register_jira_uri(
            mocker,
            endpoint="search",
            return_value=json.dumps(mock_response),
            HTTP_ACTION='POST',
        )
        
        # Test with use_jql_enhanced_search=False (default)
        result = _download_issue_page(
            jira_connection=jira_mock_connection,
            jql_query="project = TEST",
            start_at=0,
            batch_size=100,
            return_total=True,
            use_jql_enhanced_search=False
        )
        
        # Should return 2 values for legacy API
        assert isinstance(result, tuple)
        assert len(result) == 2
        issues, total = result
        assert len(issues) == 1
        assert total == 1
        assert issues[0]["key"] == "TEST-1"


def test_download_issue_page_with_jql_enhanced_search():
    """Test that _download_issue_page works correctly with JQL Enhanced Search API (use_jql_enhanced_search=True)"""
    with requests_mock.Mocker() as mocker:
        # Mock JQL Enhanced Search API response
        mock_response = {
            "issues": [{"id": "1", "key": "TEST-1"}],
            "nextPageToken": "token123"
        }
        jira_mock_connection = get_jira_mock_connection(mocker)
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=json.dumps(mock_response),
            HTTP_ACTION='POST',
        )
        
        # Test with use_jql_enhanced_search=True
        result = _download_issue_page(
            jira_connection=jira_mock_connection,
            jql_query="project = TEST",
            start_at=0,
            batch_size=100,
            return_total=True,
            use_jql_enhanced_search=True,
            next_page_token=None
        )
        
        # Should return (issues, total) tuple when return_total=True
        assert isinstance(result, tuple)
        assert len(result) == 2
        issues, total = result
        assert len(issues) == 1
        assert total == 1  # len(issues) for JQL Enhanced Search
        assert issues[0]["key"] == "TEST-1"


def test_download_issue_page_with_jql_enhanced_search_no_return_total():
    """Test that _download_issue_page returns correct signature when return_total=False with JQL Enhanced Search"""
    with requests_mock.Mocker() as mocker:
        # Mock JQL Enhanced Search API response
        mock_response = {
            "issues": [{"id": "1", "key": "TEST-1"}],
            "nextPageToken": "token123"
        }
        jira_mock_connection = get_jira_mock_connection(mocker)
        _register_jira_uri(
            mocker,
            endpoint="search/jql",
            return_value=json.dumps(mock_response),
            HTTP_ACTION='POST',
        )
        
        # Test with use_jql_enhanced_search=True and return_total=False
        result = _download_issue_page(
            jira_connection=jira_mock_connection,
            jql_query="project = TEST",
            start_at=0,
            batch_size=100,
            return_total=False,
            use_jql_enhanced_search=True,
            next_page_token=None
        )
        
        # Should return just issues list when return_total=False
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "TEST-1"


def test_download_issue_page_backward_compatibility():
    """Test that _download_issue_page maintains backward compatibility when called without new parameters"""
    with requests_mock.Mocker() as mocker:
        # Mock legacy API response
        mock_response = {
            "expand": "names,schema",
            "startAt": 0,
            "maxResults": 100,
            "total": 1,
            "issues": [{"id": "1", "key": "TEST-1"}]
        }
        jira_mock_connection = get_jira_mock_connection(mocker)
        _register_jira_uri(
            mocker,
            endpoint="search",
            return_value=json.dumps(mock_response),
            HTTP_ACTION='POST',
        )
        
        # Test calling without new parameters (should use legacy API)
        result = _download_issue_page(
            jira_connection=jira_mock_connection,
            jql_query="project = TEST",
            start_at=0,
            batch_size=100
        )
        
        # Should return just issues list (no total) for backward compatibility
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "TEST-1"


def test_download_issue_page_error_handling_with_jql_enhanced_search():
    """Test that _download_issue_page handles errors correctly with JQL Enhanced Search API"""
    with patch("jf_ingest.jf_jira.downloaders.get_issues_with_post_enhanced", side_effect=Exception("API Error")):
        # Test error handling with JQL Enhanced Search
        result = _download_issue_page(
            jira_connection=get_jira_mock_connection(),
            jql_query="project = TEST",
            start_at=1000,  # Set start_at > end_at to trigger error return
            batch_size=100,
            return_total=True,
            use_jql_enhanced_search=True
        )
        
        # Should return empty results with correct signature (issues, total) when return_total=True
        assert isinstance(result, tuple)
        assert len(result) == 2
        issues, total = result
        assert issues == []
        assert total == 0


def test_get_jira_results_looped_with_legacy_api():
    """Test that get_jira_results_looped works correctly with legacy API (default behavior)"""
    with patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        jira_connection = get_jira_mock_connection()
        jql_query = "project = TEST"
        
        # Mock two calls to _download_issue_page with 2-value returns (legacy API)
        mock_download.side_effect = [
            # First call - returns issues with total
            ([{"id": "1", "key": "TEST-1"}, {"id": "2", "key": "TEST-2"}], 3),
            # Second call - returns final issue with total
            ([{"id": "3", "key": "TEST-3"}], 3)
        ]
        
        results = get_jira_results_looped(
            jira_connection=jira_connection,
            jql_query=jql_query,
            batch_size=2,
            issue_count=3,
            include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='id'),
                JiraFieldIdentifier(jira_field_id='key', jira_field_name='key'),
            ]
        )
        
        assert len(results) == 3
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        assert results[2]["id"] == "3"
        
        # Verify _download_issue_page was called correctly for legacy API
        assert mock_download.call_count == 2
        
        # First call should have start_at=0
        first_call = mock_download.call_args_list[0]
        assert first_call[1]["start_at"] == 0
        assert "use_jql_enhanced_search" not in first_call[1] or first_call[1]["use_jql_enhanced_search"] is False
        
        # Second call should have start_at=2 (after processing 2 results)
        second_call = mock_download.call_args_list[1]
        assert second_call[1]["start_at"] == 2
        assert "use_jql_enhanced_search" not in second_call[1] or second_call[1]["use_jql_enhanced_search"] is False


def test_get_jira_results_looped_with_jql_enhanced_search():
    """Test that get_jira_results_looped works correctly with JQL Enhanced Search API"""
    with patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        jira_connection = get_jira_mock_connection()
        jql_query = "project = TEST"
        
        # For this test, let's use a simple single-page scenario to avoid the complexity
        # Mock single call that returns all results with no next_page_token
        mock_download.return_value = ([{"id": "1", "key": "TEST-1"}, {"id": "2", "key": "TEST-2"}, {"id": "3", "key": "TEST-3"}], 3, None)
        
        results = get_jira_results_looped(
            jira_connection=jira_connection,
            jql_query=jql_query,
            batch_size=10,
            issue_count=3,
            include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='id'),
                JiraFieldIdentifier(jira_field_id='key', jira_field_name='key'),
            ],
            use_jql_enhanced_search=True
        )
        
        assert len(results) == 3
        assert results[0]["id"] == "1"
        assert results[1]["id"] == "2"
        assert results[2]["id"] == "3"
        
        # Verify _download_issue_page was called correctly
        assert mock_download.call_count == 1
        
        # Call should have use_jql_enhanced_search=True and next_page_token=None (first call)
        call_args = mock_download.call_args_list[0]
        assert call_args[1]["use_jql_enhanced_search"] is True
        assert call_args[1]["next_page_token"] is None


def test_get_jira_results_looped_backward_compatibility():
    """Test that get_jira_results_looped maintains backward compatibility when use_jql_enhanced_search is not provided"""
    with patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        jira_connection = get_jira_mock_connection()
        jql_query = "project = TEST"
        
        # Mock single call to _download_issue_page
        mock_download.return_value = ([{"id": "1", "key": "TEST-1"}], 1)
        
        # Call without use_jql_enhanced_search parameter (should default to False)
        results = get_jira_results_looped(
            jira_connection=jira_connection,
            jql_query=jql_query,
            batch_size=10,
            issue_count=1
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "1"
        
        # Verify _download_issue_page was called with legacy API behavior
        assert mock_download.call_count == 1
        call_args = mock_download.call_args_list[0]
        assert "use_jql_enhanced_search" not in call_args[1] or call_args[1]["use_jql_enhanced_search"] is False


def test_pull_jira_issues_by_jira_ids_with_use_jql_enhanced_search_parameter():
    """Test that pull_jira_issues_by_jira_ids passes use_jql_enhanced_search parameter correctly"""
    with patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        jira_connection = get_jira_mock_connection()
        jira_ids = ["1", "2"]
        
        # Mock _download_issue_page to return issues
        mock_download.return_value = [
            {"id": "1", "key": "TEST-1"},
            {"id": "2", "key": "TEST-2"}
        ]
        
        # Test with use_jql_enhanced_search=True
        list(pull_jira_issues_by_jira_ids(
            jira_connection=jira_connection,
            jira_ids=jira_ids,
            num_parallel_threads=1,
            batch_size=10,
            use_jql_enhanced_search=True
        ))
        
        # Verify _download_issue_page was called with use_jql_enhanced_search=True
        assert mock_download.call_count == 1
        call_args = mock_download.call_args_list[0]
        assert call_args[1]["use_jql_enhanced_search"] is True


def test_pull_jira_issues_by_jira_ids_backward_compatibility():
    """Test that pull_jira_issues_by_jira_ids maintains backward compatibility when use_jql_enhanced_search is not provided"""
    with patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        jira_connection = get_jira_mock_connection()
        jira_ids = ["1"]
        
        # Mock _download_issue_page to return issues
        mock_download.return_value = [{"id": "1", "key": "TEST-1"}]
        
        # Test without use_jql_enhanced_search parameter (should default to False)
        list(pull_jira_issues_by_jira_ids(
            jira_connection=jira_connection,
            jira_ids=jira_ids,
            num_parallel_threads=1,
            batch_size=10
        ))
        
        # Verify _download_issue_page was called with use_jql_enhanced_search=False (default)
        assert mock_download.call_count == 1
        call_args = mock_download.call_args_list[0]
        # The parameter should not be present in the call (using default)
        assert "use_jql_enhanced_search" not in call_args[1] or call_args[1]["use_jql_enhanced_search"] is False


def test_pull_all_jira_issues_by_date_with_use_jql_enhanced_search_parameter():
    """Test that pull_all_jira_issues_by_date passes use_jql_enhanced_search parameter correctly"""
    from datetime import datetime
    
    with patch("jf_ingest.jf_jira.downloaders._get_all_project_issue_counts") as mock_count, \
         patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download, \
         patch("jf_ingest.jf_jira.downloaders._pull_all_jira_issues_by_date_enhanced") as mock_enhanced:
        
        jira_connection = get_jira_mock_connection()
        project_key_to_pull_from = {"TEST": datetime.min}
        
        # Mock _get_all_project_issue_counts to return project counts
        mock_count.return_value = {"TEST": 2}
        
        # Mock _pull_all_jira_issues_by_date_enhanced to return issues
        mock_enhanced.return_value = iter([
            {"id": "1", "key": "TEST-1"},
            {"id": "2", "key": "TEST-2"}
        ])
        
        # Mock _download_issue_page to return issues in the correct format for JQL Enhanced Search
        # Format: (issues_list, total_count, next_page_token)
        mock_download.return_value = (
            [{"id": "1", "key": "TEST-1"}, {"id": "2", "key": "TEST-2"}],  # issues
            2,  # total
            None  # next_page_token (no more pages)
        )
        
        # Test with use_jql_enhanced_search=True
        list(pull_all_jira_issues_by_date(
            jira_connection=jira_connection,
            project_key_to_pull_from=project_key_to_pull_from,
            num_parallel_threads=1,
            batch_size=10,
            jql_project_batch_size=1,
            use_jql_enhanced_search=True
        ))
        
        # Verify _get_all_project_issue_counts was called with use_jql_enhanced_search=True
        assert mock_count.call_count == 1
        count_call_args = mock_count.call_args_list[0]
        assert count_call_args[1]["use_jql_enhanced_search"] is True
        
        # Verify _pull_all_jira_issues_by_date_enhanced was called (JQL Enhanced Search path)
        assert mock_enhanced.call_count == 1
        enhanced_call_args = mock_enhanced.call_args_list[0]
        # Verify the enhanced function was called with the correct parameters
        assert enhanced_call_args[1]["jira_connection"] == jira_connection
        assert enhanced_call_args[1]["project_key_to_pull_from"] == project_key_to_pull_from


def test_pull_all_jira_issues_by_date_backward_compatibility():
    """Test that pull_all_jira_issues_by_date maintains backward compatibility when use_jql_enhanced_search is not provided"""
    from datetime import datetime
    
    with patch("jf_ingest.jf_jira.downloaders._get_all_project_issue_counts") as mock_count, \
         patch("jf_ingest.jf_jira.downloaders._download_issue_page") as mock_download:
        
        jira_connection = get_jira_mock_connection()
        project_key_to_pull_from = {"TEST": datetime.min}
        
        # Mock _get_all_project_issue_counts to return project counts
        mock_count.return_value = {"TEST": 1}
        
        # Mock _download_issue_page to return issues
        mock_download.return_value = [{"id": "1", "key": "TEST-1"}]
        
        # Test without use_jql_enhanced_search parameter (should default to False)
        list(pull_all_jira_issues_by_date(
            jira_connection=jira_connection,
            project_key_to_pull_from=project_key_to_pull_from,
            num_parallel_threads=1,
            batch_size=10,
            jql_project_batch_size=1
        ))
        
        # Verify _get_all_project_issue_counts was called with use_jql_enhanced_search=False (default)
        assert mock_count.call_count == 1
        count_call_args = mock_count.call_args_list[0]
        assert "use_jql_enhanced_search" not in count_call_args[1] or count_call_args[1]["use_jql_enhanced_search"] is False
        
        # Verify _download_issue_page was called with use_jql_enhanced_search=False (default)
        assert mock_download.call_count >= 1
        download_call_args = mock_download.call_args_list[0]
        assert "use_jql_enhanced_search" not in download_call_args[1] or download_call_args[1]["use_jql_enhanced_search"] is False


def test_get_all_project_issue_counts_with_use_jql_enhanced_search_parameter():
    """Test that _get_all_project_issue_counts passes use_jql_enhanced_search parameter correctly"""
    from datetime import datetime
    
    with patch("jf_ingest.jf_jira.downloaders._get_issue_count_for_jql") as mock_count:
        jira_connection = get_jira_mock_connection()
        project_key_to_pull_from = {"TEST": datetime.min}
        
        # Mock _get_issue_count_for_jql to return a count
        mock_count.return_value = 5
        
        # Test with use_jql_enhanced_search=True
        _get_all_project_issue_counts(
            jira_connection=jira_connection,
            project_key_to_pull_from=project_key_to_pull_from,
            num_parallel_threads=1,
            use_jql_enhanced_search=True
        )
        
        # Verify _get_issue_count_for_jql was called with use_jql_enhanced_search=True
        assert mock_count.call_count == 1
        call_args = mock_count.call_args_list[0]
        assert call_args[1]["use_jql_enhanced_search"] is True


def test_get_all_project_issue_counts_backward_compatibility():
    """Test that _get_all_project_issue_counts maintains backward compatibility when use_jql_enhanced_search is not provided"""
    from datetime import datetime
    
    with patch("jf_ingest.jf_jira.downloaders._get_issue_count_for_jql") as mock_count:
        jira_connection = get_jira_mock_connection()
        project_key_to_pull_from = {"TEST": datetime.min}
        
        # Mock _get_issue_count_for_jql to return a count
        mock_count.return_value = 3
        
        # Test without use_jql_enhanced_search parameter (should default to False)
        _get_all_project_issue_counts(
            jira_connection=jira_connection,
            project_key_to_pull_from=project_key_to_pull_from,
            num_parallel_threads=1
        )
        
        # Verify _get_issue_count_for_jql was called with use_jql_enhanced_search=False (default)
        assert mock_count.call_count == 1
        call_args = mock_count.call_args_list[0]
        assert "use_jql_enhanced_search" not in call_args[1] or call_args[1]["use_jql_enhanced_search"] is False



def test_fetch_id_to_key_for_all_existing_parameter_passing():
    """Test that fetch_id_to_key_for_all_existing passes use_jql_enhanced_search parameter through to called functions."""
    from unittest.mock import patch, MagicMock
    
    # Mock the functions that fetch_id_to_key_for_all_existing calls
    with patch('jf_ingest.jf_jira.downloaders._get_all_project_issue_counts') as mock_get_counts, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_search_batch_size') as mock_batch_size, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_results_looped') as mock_results_looped, \
         patch('jf_ingest.jf_jira.downloaders.generate_project_pull_from_jql') as mock_jql:
        
        # Set up mock return values
        mock_get_counts.return_value = {'PROJ': 100}
        mock_batch_size.return_value = 1000
        mock_results_looped.return_value = [{'id': '1', 'key': 'PROJ-1'}]
        mock_jql.return_value = 'project = PROJ'
        
        # Test with use_jql_enhanced_search=True
        result = fetch_id_to_key_for_all_existing(
            jira_connection=MagicMock(),
            project_ids=['PROJ'],
            pull_from=datetime.min,
            jql_filter=None,
            use_jql_enhanced_search=True
        )
        
        # Verify the parameter was passed to _get_all_project_issue_counts
        mock_get_counts.assert_called_once()
        call_args = mock_get_counts.call_args
        assert call_args[1]['use_jql_enhanced_search'] is True
        
        # Verify the parameter was passed to get_jira_results_looped
        mock_results_looped.assert_called_once()
        call_args = mock_results_looped.call_args
        assert call_args[1]['use_jql_enhanced_search'] is True
        
        # Verify return value
        assert result == {'1': 'PROJ-1'}


def test_fetch_id_to_key_for_all_existing_backward_compatibility():
    """Test that fetch_id_to_key_for_all_existing maintains backward compatibility when use_jql_enhanced_search is not provided."""
    from unittest.mock import patch, MagicMock
    
    # Mock the functions that fetch_id_to_key_for_all_existing calls
    with patch('jf_ingest.jf_jira.downloaders._get_all_project_issue_counts') as mock_get_counts, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_search_batch_size') as mock_batch_size, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_results_looped') as mock_results_looped, \
         patch('jf_ingest.jf_jira.downloaders.generate_project_pull_from_jql') as mock_jql:
        
        # Set up mock return values
        mock_get_counts.return_value = {'PROJ': 100}
        mock_batch_size.return_value = 1000
        mock_results_looped.return_value = [{'id': '1', 'key': 'PROJ-1'}]
        mock_jql.return_value = 'project = PROJ'
        
        # Test without use_jql_enhanced_search parameter (should default to False)
        result = fetch_id_to_key_for_all_existing(
            jira_connection=MagicMock(),
            project_ids=['PROJ'],
            pull_from=datetime.min,
            jql_filter=None
        )
        
        # Verify the parameter was passed as False to _get_all_project_issue_counts
        mock_get_counts.assert_called_once()
        call_args = mock_get_counts.call_args
        assert call_args[1]['use_jql_enhanced_search'] is False
        
        # Verify the parameter was passed as False to get_jira_results_looped
        mock_results_looped.assert_called_once()
        call_args = mock_results_looped.call_args
        assert call_args[1]['use_jql_enhanced_search'] is False
        
        # Verify return value
        assert result == {'1': 'PROJ-1'}


def test_fetch_id_to_key_for_all_existing_api_selection_integration():
    """Integration test to verify API selection works through the entire call chain."""
    from unittest.mock import patch, MagicMock
    
    # Mock the lower-level functions to verify they receive the correct parameter
    with patch('jf_ingest.jf_jira.downloaders._get_issue_count_for_jql') as mock_count_jql, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_search_batch_size') as mock_batch_size, \
         patch('jf_ingest.jf_jira.downloaders.get_jira_results_looped') as mock_results_looped, \
         patch('jf_ingest.jf_jira.downloaders.generate_project_pull_from_jql') as mock_jql:
        
        # Set up mock return values
        mock_count_jql.return_value = 100
        mock_batch_size.return_value = 5000  # JQL Enhanced Search batch size
        mock_results_looped.return_value = [{'id': '1', 'key': 'PROJ-1'}]
        mock_jql.return_value = 'project = PROJ'
        
        # Test with use_jql_enhanced_search=True
        result = fetch_id_to_key_for_all_existing(
            jira_connection=MagicMock(),
            project_ids=['PROJ'],
            pull_from=datetime.min,
            jql_filter=None,
            use_jql_enhanced_search=True
        )
        
        # Verify _get_issue_count_for_jql was called with use_jql_enhanced_search=True
        # This happens through _get_all_project_issue_counts
        mock_count_jql.assert_called()
        count_call_args = mock_count_jql.call_args
        assert count_call_args[1]['use_jql_enhanced_search'] is True
        
        # Verify get_jira_results_looped was called with use_jql_enhanced_search=True
        mock_results_looped.assert_called_once()
        results_call_args = mock_results_looped.call_args
        assert results_call_args[1]['use_jql_enhanced_search'] is True
        
        # Verify return value
        assert result == {'1': 'PROJ-1'}