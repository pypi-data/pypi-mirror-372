from datetime import datetime
from unittest.mock import patch

import pytest
import pytz
import requests
import requests_mock

from jf_ingest.config import GithubAuthConfig
from jf_ingest.graphql_utils import (
    GQL_PAGE_INFO_BLOCK,
    GQLRateLimit,
    gql_format_to_datetime,
)
from jf_ingest.jf_git.clients.github import GQL_RATE_LIMIT_QUERY_BLOCK, GithubClient
from jf_ingest.jf_git.exceptions import GqlRateLimitExceededException

TEST_BASE_URL = 'https://gav.com/gql'

# Shared test data
GQL_DATETIME_STR = "2024-12-29T12:00:58Z"


@pytest.fixture()
def client() -> GithubClient:
    # Mock out a Github GQL Client
    github_auth_config = GithubAuthConfig(company_slug='a company', base_url=TEST_BASE_URL, token='test')
    return GithubClient(github_auth_config)


def test_gql_page_results_block():
    """This is a sanity check that the GQL_PAGE_INFO_BLOCK and GQL_RATE_LIMIT_QUERY_BLOCK
    are valid. This are pretty vague smoke tests... it's unlikely anybody would mess with
    these, but if they do it will cause a lot of problems!
    """

    assert 'pageInfo' in GQL_PAGE_INFO_BLOCK
    assert 'hasNextPage' in GQL_PAGE_INFO_BLOCK
    assert 'endCursor' in GQL_PAGE_INFO_BLOCK

    assert 'rateLimit' in GQL_RATE_LIMIT_QUERY_BLOCK
    assert 'remaining' in GQL_RATE_LIMIT_QUERY_BLOCK
    assert 'resetAt' in GQL_RATE_LIMIT_QUERY_BLOCK


def test_gql_format_to_datetime():
    """Assert we get valid date time back (and that it's timezone aware)"""
    gql_datetime: datetime = gql_format_to_datetime(datetime_str=GQL_DATETIME_STR)
    assert type(gql_datetime) is datetime
    assert gql_datetime.tzinfo is not None
    assert gql_datetime == datetime(2024, 12, 29, 12, 00, 58, tzinfo=pytz.utc)

def test_git_auth_config_base_url():
    github_api_url = 'https://api.github.com'
    github_auth_config = GithubAuthConfig(company_slug='a company', token='test')
    assert github_auth_config.base_url == GithubAuthConfig.base_url
    assert github_auth_config.base_url == None

    client = GithubClient(github_auth_config)
    assert client.rest_api_url == github_api_url
    assert client.gql_base_url == f'{github_api_url}/graphql'

def test_get_rate_limit(requests_mock: requests_mock.Mocker, client: GithubClient):
    # Mock classes/data
    session = requests.Session()
    client.session = session
    
    def _test_get_rate_limit_inner(remaining_rate_limit: int, reset_at_rate_limit_str: str):
        print(
            f'Testing get_rate_limit with remaining={remaining_rate_limit} and resetAt={reset_at_rate_limit_str}'
        )
        # Mock classes/data
        session_mock_return_data = {
            'data': {
                'rateLimit': {'remaining': remaining_rate_limit, 'resetAt': reset_at_rate_limit_str}
            }
        }
        requests_mock.post(url=f'{TEST_BASE_URL}/graphql', json=session_mock_return_data)

        # Call function
        rate_limit_info = client.get_gql_rate_limit()

        # Test results
        assert type(rate_limit_info) is GQLRateLimit
        assert rate_limit_info.reset_at == gql_format_to_datetime(datetime_str=GQL_DATETIME_STR)
        assert rate_limit_info.remaining == int(remaining_rate_limit)

    # Test data
    _test_get_rate_limit_inner(25, GQL_DATETIME_STR)
    _test_get_rate_limit_inner(-1, GQL_DATETIME_STR)
    _test_get_rate_limit_inner("124", GQL_DATETIME_STR)
    with pytest.raises(Exception):
        _test_get_rate_limit_inner('cat', GQL_DATETIME_STR)


def test_get_raw_gql_result_simple(requests_mock: requests_mock.Mocker, client: GithubClient):
    # Test Data
    test_query_body = "test_query_body"
    # Mock classes/data
    session = requests.Session()
    session_mock_caller_data = {'query': test_query_body}
    session_mock_return_data = {'data': {'test': {'remaining': 'test', 'resetAt': 'test'}}}
    requests_mock.post(url=f'{TEST_BASE_URL}/graphql', json=session_mock_return_data)
    client.session = session

    # call function
    returned_data = client.get_raw_result(query_body=test_query_body)

    assert returned_data == session_mock_return_data
    assert requests_mock.last_request.json() == session_mock_caller_data


def test_get_raw_gql_result_force_error_raise(mocker, requests_mock: requests_mock.Mocker, client: GithubClient):
    mocker.patch('time.sleep', return_value=None)
    # Mock classes/data
    session = requests.Session()
    client.session = session

    requests_mock.post(
        url=f'{TEST_BASE_URL}/graphql', response_list=[{'json': '', 'status_code': 403}]
    )

    print('Testing raising a 403 error intentionally')
    with pytest.raises(Exception):
        print('Max attempts is 0...')
        client.get_raw_result(query_body='', max_attempts=0)
        print('Max attempts is 100... (if time.sleep is NOT mocked here, this will hang forever!)')
        client.get_raw_result(query_body='', max_attempts=100)

    print('Testing raising a 500 error intentionally')
    requests_mock.post(url=TEST_BASE_URL, response_list=[{'json': '', 'status_code': 500}])
    with pytest.raises(Exception):
        client.get_raw_result(query_body='', max_attempts=0)
        client.get_raw_result(query_body='', max_attempts=100)

    print('Asserting that we hit the GQL Rate Limit Exceeded exception')
    reponse_to_force_retry = {'json': {'errors': [{'type': 'RATE_LIMITED'}]}, 'status_code': 200}
    response_for_retry_rate = {
        'json': {'data': {'rateLimit': {'remaining': 10, 'resetAt': GQL_DATETIME_STR}}},
        'status_code': 200,
    }
    reponse_pairing = [reponse_to_force_retry, response_for_retry_rate]
    response_list = [*reponse_pairing, *reponse_pairing, *reponse_pairing]

    requests_mock.post(
        url=f'{TEST_BASE_URL}/graphql',
        response_list=response_list,
    )

    with pytest.raises(GqlRateLimitExceededException):
        client.get_raw_result(query_body='', max_attempts=2)


def test_get_raw_gql_result_successful_retry(mocker, requests_mock: requests_mock.Mocker, client: GithubClient):
    mocker.patch('time.sleep', return_value=None)
    session = requests.Session()
    successful_data = {'success': True}
    requests_mock.post(
        url=f'{TEST_BASE_URL}/graphql',
        response_list=[
            {'json': {'errors': [{'type': 'RATE_LIMITED'}]}, 'status_code': 200},
            {
                'json': {'data': {'rateLimit': {'remaining': 10, 'resetAt': GQL_DATETIME_STR}}},
                'status_code': 200,
            },
            {'json': successful_data, 'status_code': 200},
        ],
    )

    client.session = session

    data = client.get_raw_result(query_body='', max_attempts=10)
    assert data == successful_data


def test_github_client_error_raise_403(mocker, requests_mock: requests_mock.Mocker, client: GithubClient):
    mocker.patch('time.sleep', return_value=None)
    session = requests.Session()
    successful_data = {'success': True}
    requests_mock.post(
        url=f'{TEST_BASE_URL}/graphql',
        response_list=[
            {'status_code': 403},
        ],
    )

    # Mock out a Github GQL Client
    client.session = session

    retry_count = 10
    with pytest.raises(requests.HTTPError):
        client.get_raw_result(query_body='', max_attempts=retry_count)
        assert requests_mock.call_count == retry_count

def test_github_client_error_resolves_after_retry(mocker, requests_mock: requests_mock.Mocker, client: GithubClient):
    mocker.patch('time.sleep', return_value=None)
    session = requests.Session()
    successful_data = {'mantra': 'never give UP!'}
    response_list = [
        # A Beautiful Error Medley
        {'status_code': 403},
        {'status_code': 429},
        {'status_code': 500},
        {'status_code': 502},
        {'status_code': 503},
        {'status_code': 504},
        {'json': successful_data}
    ]
    retry_count = len(response_list)
    requests_mock.post(
        url=f'{TEST_BASE_URL}/graphql',
        response_list=response_list,
    )

    # Mock out a Github GQL Client
    client.session = session

    assert client.get_raw_result(query_body='', max_attempts=retry_count) == successful_data
    assert requests_mock.call_count == retry_count

def test_page_results_gql(mocker, requests_mock: requests_mock.Mocker):
    session = requests.Session()
    # Mock out a Github GQL Client
    github_auth_config = GithubAuthConfig(company_slug='A Company', base_url=TEST_BASE_URL, session=session, token='test')
    client = GithubClient(github_auth_config)
    client.session = session

    def _test_page_results_gql_intter(items_per_page: int, number_of_pages: int):
        print(
            f'Testing page_results_gql(items_per_page={items_per_page}, number_of_pages={number_of_pages})'
        )
        query_body = f"""{{
            baseQuery {{
                queryToPage(first: {items_per_page}, after: %s) {{
                    pageInfo {{hasNextPage, endCursor}}
                    testField
                }}
            }}
        }}
        """
        path_to_page_info = 'data.baseQuery.queryToPage'

        requests_mock.post(
            url=f'{TEST_BASE_URL}/graphql',
            response_list=[
                {
                    'json': {
                        'data': {
                            'baseQuery': {
                                'queryToPage': {
                                    'pageInfo': {
                                        'hasNextPage': i != number_of_pages - 1,
                                        'endCursor': f'endCursor_{i}',
                                    },
                                    'nodes': [
                                        {
                                            'testField': f'pageNumber={i}, nodeNumber={x}',
                                        }
                                        for x in range(0, items_per_page)
                                    ],
                                }
                            }
                        }
                    },
                    'status_code': 200,
                }
                for i in range(0, number_of_pages)
            ],
        )

        pages = [
            page
            for page in client.page_results_gql(
                query_body=query_body,
                path_to_page_info=path_to_page_info,
            )
        ]

        assert len(pages) == number_of_pages

        total_items = [
            item for page in pages for item in page['data']['baseQuery']['queryToPage']['nodes']
        ]

        assert len(total_items) == items_per_page * number_of_pages

    _test_page_results_gql_intter(items_per_page=1, number_of_pages=10)
    _test_page_results_gql_intter(items_per_page=10, number_of_pages=100)
