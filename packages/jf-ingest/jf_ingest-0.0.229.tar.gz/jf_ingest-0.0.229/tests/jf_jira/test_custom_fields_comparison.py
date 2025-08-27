import json
import os
import requests_mock
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from jf_ingest.config import IngestionConfig, IngestionType, JiraDownloadConfig
from jf_ingest.jf_jira import custom_fields as custom_fields
from jf_ingest.jf_jira.custom_fields import (
    JELLYFISH_CUSTOM_FIELDS_ENDPOINT,
    JELLYFISH_MARK_FOR_REDOWNLOAD_ENDPOINT,
    JCFVUpdate
)
from tests.jf_jira.utils import get_fixture_file_data

ATLASSIAN_BASE_URL = 'mock://test-co.atlassian.net/'
JELLYFISH_BASE_URL = 'mock://jellyfish.jellyfish'


class TestCustomFieldsComparison(TestCase):
    def setUp(self):
        self.missing_from_jira_jcfv = JCFVUpdate(
            field_id='201',
            field_key='customfield_301',
            field_type='team',
            jira_issue_id='101',
            value_new=None,
            value_old={"name": "T2"}
        )
        self.missing_from_db_jcfv = JCFVUpdate(
            field_id='201',
            field_key='customfield_301',
            field_type='team',
            jira_issue_id='100',
            value_new={
                'self': 'https://test-co.atlassian.net/rest/api/2/customFieldOption/12347',
                'value': 'NEW TEAM 10',
                'id': '12347',
            },
            value_old=None
        )
        self.out_of_sync_jcfv = JCFVUpdate(
            field_id='200',
            field_key='customfield_300',
            field_type='team',
            jira_issue_id='100',
            value_new={
                'self': 'https://test-co.atlassian.net/rest/api/2/customFieldOption/12345',
                'value': 'NEW TEAM 1',
                'id': '12345',
            },
            value_old={"name": "T1"}
        )

    def _get_ingestion_config(self):
        company_slug = "test_company"
        url = ATLASSIAN_BASE_URL
        return IngestionConfig(
            company_slug=company_slug,
            jira_config=JiraDownloadConfig(
                company_slug=company_slug,
                url=url,
                personal_access_token='pat',
                gdpr_active=True,
            ),
            git_configs=[],
            jellyfish_api_token='some_token',
            jellyfish_api_base=JELLYFISH_BASE_URL,
            ingest_type=IngestionType.DIRECT_CONNECT,
        )


    def _get_jellyfish_custom_fields_default_response(self) -> dict:
        return json.loads(get_fixture_file_data(fixture_path='jellyfish_custom_fields.json'))


    def _get_jellyfish_custom_fields_empty_response(self) -> dict:
        return json.loads(
            get_fixture_file_data(fixture_path='jellyfish_custom_fields_empty_response.json')
        )


    def _mock_synchronous_thread(self):
        # Mock out ThreadPoolExecutor to get a synchronous run
        def _synchronous_run(f, *args, **kwargs):
            f(*args, **kwargs)
            thread_obj = MagicMock()
            thread_obj.running = MagicMock()
            thread_obj.running.return_value = False
            return thread_obj

        synchronous_run_mock = MagicMock()
        custom_fields.ThreadPoolExecutor = MagicMock()
        custom_fields.ThreadPoolExecutor.return_value = synchronous_run_mock
        synchronous_run_mock.submit = _synchronous_run

        return synchronous_run_mock


    def _mock_custom_field_responses(self, issues_fixture_path: Optional[str] = 'issues_for_custom_fields.json'):
        # Mock out Jira response
        issues = get_fixture_file_data(
            fixture_path=os.path.join('api_responses', issues_fixture_path)
        )
        issues_resp = json.loads(issues)['issues']
        custom_fields.pull_jira_issues_by_jira_ids = MagicMock()
        custom_fields.pull_jira_issues_by_jira_ids.return_value = issues_resp

        # Mock out Jira connection and batch size request
        custom_fields.get_jira_connection = MagicMock()
        custom_fields.get_jira_search_batch_size = MagicMock()
        custom_fields.get_jira_search_batch_size.return_value = 100


    def test_custom_fields_comparison_base_case(self):
        config = self._get_ingestion_config()
        jf_response = self._get_jellyfish_custom_fields_default_response()

        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                'GET',
                f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit={custom_fields.JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
                json=jf_response,
                status_code=200,
            )

            mocker.register_uri(
                'GET',
                f"{config.jellyfish_api_base}/endpoints/jira/issues/count",
                json={
                    'total_issues_in_jellyfish': 0
                },  # This is just for TQDM UX, and not really important for testing
                status_code=200,
            )

            redownload_mock = mocker.register_uri(
                'POST',
                f"{config.jellyfish_api_base}/{JELLYFISH_MARK_FOR_REDOWNLOAD_ENDPOINT}",
                json={},
                status_code=200,
            )

            self._mock_synchronous_thread()
            self._mock_custom_field_responses()

            # Generate update payload
            update_payload = custom_fields.identify_custom_field_mismatches(config, nthreads=1)

            self.assertEqual(len(update_payload.missing_from_jira_jcfv), 1)
            self.assertEqual(len(update_payload.missing_from_db_jcfv), 1)
            self.assertEqual(len(update_payload.out_of_sync_jcfv), 1)

            # Missing from Jira (DELETE)
            self.assertEqual(update_payload.missing_from_jira_jcfv[0],self.missing_from_jira_jcfv)

            # Missing from DB (INSERT)
            self.assertEqual(update_payload.missing_from_db_jcfv[0], self.missing_from_db_jcfv)

            # Out-of-sync (UPDATE)
            self.assertEqual(update_payload.out_of_sync_jcfv[0], self.out_of_sync_jcfv)

            self.assertFalse(redownload_mock.called)


    def test_custom_fields_mark_for_redownload(self):
        config = self._get_ingestion_config()
        jf_response = self._get_jellyfish_custom_fields_default_response()

        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                'GET',
                f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit={custom_fields.JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
                json=jf_response,
                status_code=200,
            )

            mocker.register_uri(
                'GET',
                f"{config.jellyfish_api_base}/endpoints/jira/issues/count",
                json={
                    'total_issues_in_jellyfish': 0
                },  # This is just for TQDM UX, and not really important for testing
                status_code=200,
            )

            redownload_mock = mocker.register_uri(
                'POST',
                f"{config.jellyfish_api_base}/{JELLYFISH_MARK_FOR_REDOWNLOAD_ENDPOINT}",
                [
                    {'json': {}, 'status_code': 504},
                    {'json': {}, 'status_code': 200},
                ]
            )

            self._mock_synchronous_thread()
            self._mock_custom_field_responses()

            # Generate update payload
            update_payload = custom_fields.identify_custom_field_mismatches(config, nthreads=1, mark_for_redownload=True)

            self.assertEqual(len(update_payload.missing_from_jira_jcfv), 1)
            self.assertEqual(len(update_payload.missing_from_db_jcfv), 1)
            self.assertEqual(len(update_payload.out_of_sync_jcfv), 1)
            self.assertEqual(update_payload.missing_from_jira_jcfv[0], self.missing_from_jira_jcfv)
            self.assertEqual(update_payload.missing_from_db_jcfv[0], self.missing_from_db_jcfv)
            self.assertEqual(update_payload.out_of_sync_jcfv[0], self.out_of_sync_jcfv)

            # We should attempt twice with the same payload. A 504 triggers retry. Issue id order does not matter.
            self.assertEqual(redownload_mock.call_count, 2)
            self.assertCountEqual(redownload_mock.request_history[0].json()['issue_ids'], ['100', '101'])
            self.assertCountEqual(redownload_mock.request_history[1].json()['issue_ids'], ['101', '100'])
