import json
import os
import queue
from copy import deepcopy
from unittest.mock import patch

import pytest
import requests
import requests_mock

from jf_ingest.config import IngestionConfig, IngestionType, JiraDownloadConfig
from jf_ingest.jf_jira.custom_fields import (
    JELLYFISH_CUSTOM_FIELDS_API_LIMIT,
    _annotate_results_from_jellyfish,
    _retrieve_custom_fields_from_jellyfish,
)
from jf_ingest.utils import RetryLimitExceeded
from tests.jf_jira.utils import get_fixture_file_data

ATLASSIAN_BASE_URL = 'mock://test-co.atlassian.net/'
JELLYFISH_BASE_URL = 'mock://jellyfish.jellyfish'
JELLYFISH_CUSTOM_FIELDS_ENDPOINT = 'endpoints/jira/issues/custom-fields'


def _get_ingestion_config():
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


def _get_jellyfish_custom_fields_default_response() -> dict:
    return json.loads(get_fixture_file_data(fixture_path='jellyfish_custom_fields.json'))


def _get_jellyfish_custom_fields_empty_response() -> dict:
    return json.loads(
        get_fixture_file_data(fixture_path='jellyfish_custom_fields_empty_response.json')
    )


def test_custom_fields_base_case():
    config = _get_ingestion_config()
    jf_response = _get_jellyfish_custom_fields_default_response()
    empty_response = _get_jellyfish_custom_fields_empty_response()

    with requests_mock.Mocker() as mocker:
        base_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit={JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
            json=jf_response,
            status_code=200,
        )

        addl_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=101&limit={JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
            json=empty_response,
            status_code=200,
        )

        q = queue.Queue()
        _retrieve_custom_fields_from_jellyfish(config, q)
        assert q.qsize() == 1
        output = q.get()

        assert output == _annotate_results_from_jellyfish(jf_response)
        assert addl_mock.call_count == 0
        assert base_mock.call_count == 1
        assert base_mock.last_request.qs == {
            'cursor': ['0'],
            'limit': [str(JELLYFISH_CUSTOM_FIELDS_API_LIMIT)],
        }


def test_custom_fields_api_adjusted_limit():
    config = _get_ingestion_config()
    jf_response = _get_jellyfish_custom_fields_default_response()
    empty_response = _get_jellyfish_custom_fields_empty_response()

    jf_response['max_records'] = 1
    jf_response['total_records'] = 1

    jf_response_1 = deepcopy(jf_response)
    jf_response_1['issues'] = jf_response_1['issues'][:1]
    expected_cursor = jf_response_1['issues'][0]['issue_jira_id']
    jf_response_1['next_cursor'] = expected_cursor

    jf_response_2 = deepcopy(jf_response)
    jf_response_2['issues'] = jf_response_2['issues'][1:]

    with requests_mock.Mocker() as mocker:
        general_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}",
            json=empty_response,
            status_code=200,
        )

        mock0 = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit={JELLYFISH_CUSTOM_FIELDS_API_LIMIT}",
            json=jf_response_1,
            status_code=200,
        )

        mock1 = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor={expected_cursor}&limit=1",
            json=jf_response_2,
            status_code=200,
        )

        q = queue.Queue()
        _retrieve_custom_fields_from_jellyfish(config, q)
        assert q.qsize() == 2
        output0 = q.get()
        output1 = q.get()

        assert output0 == _annotate_results_from_jellyfish(jf_response_1)
        assert output1 == _annotate_results_from_jellyfish(jf_response_2)
        assert mock0.call_count == 1
        assert mock1.call_count == 1
        assert general_mock.call_count == 0


def test_custom_fields_caller_adjusted_limit():
    config = _get_ingestion_config()
    jf_response = _get_jellyfish_custom_fields_default_response()
    empty_response = _get_jellyfish_custom_fields_empty_response()
    limit = 3

    with requests_mock.Mocker() as mocker:
        general_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}",
            json=empty_response,
            status_code=200,
        )

        mock0 = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit={limit}",
            json=jf_response,
            status_code=200,
        )

        q = queue.Queue()
        _retrieve_custom_fields_from_jellyfish(config, q, limit=limit)
        assert q.qsize() == 1
        output0 = q.get()

        assert output0 == _annotate_results_from_jellyfish(jf_response)
        assert mock0.call_count == 1
        assert general_mock.call_count == 0


def test_custom_fields_max_issues_to_process():
    config = _get_ingestion_config()
    jf_response = _get_jellyfish_custom_fields_default_response()
    empty_response = _get_jellyfish_custom_fields_empty_response()

    jf_response['max_records'] = 1
    jf_response['total_records'] = 1
    jf_response['issues'] = jf_response['issues'][:1]

    with requests_mock.Mocker() as mocker:
        general_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}",
            json=empty_response,
            status_code=200,
        )

        mock0 = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor=0&limit=1",
            json=jf_response,
            status_code=200,
        )

        q = queue.Queue()
        _retrieve_custom_fields_from_jellyfish(config, q, max_issues_to_process=1)
        assert q.qsize() == 1
        output0 = q.get()

        assert output0 == _annotate_results_from_jellyfish(jf_response)
        assert mock0.call_count == 1
        assert general_mock.call_count == 0


def test_custom_fields_non_handled_status_code():
    config = _get_ingestion_config()

    with requests_mock.Mocker() as mocker:
        general_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}",
            json={},
            status_code=418,
        )

        q = queue.Queue()
        with pytest.raises(requests.exceptions.HTTPError):
            _retrieve_custom_fields_from_jellyfish(config, q, max_issues_to_process=1)


def test_custom_fields_retry_for_status():
    config = _get_ingestion_config()

    with requests_mock.Mocker() as mocker:
        general_mock = mocker.register_uri(
            'GET',
            f"{config.jellyfish_api_base}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}",
            json={},
            status_code=504,
        )

        q = queue.Queue()
        with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
            with pytest.raises(RetryLimitExceeded):
                _retrieve_custom_fields_from_jellyfish(config, q, max_issues_to_process=1)
