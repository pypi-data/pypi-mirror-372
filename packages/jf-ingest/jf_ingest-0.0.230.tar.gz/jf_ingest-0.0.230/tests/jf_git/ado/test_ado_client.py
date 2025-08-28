from datetime import datetime
from itertools import chain
from typing import Generator

import pytest
import requests
import requests_mock

from jf_ingest.config import AzureDevopsAuthConfig
from jf_ingest.jf_git.clients.azure_devops import AzureDevopsClient

TEST_BASE_URL = 'https://ado.com/'
CONTINUATION_TOKEN_HEADER_SLUG = 'x-ms-continuationtoken'


def _get_client(api_version: str = None):
    session = requests.Session()
    auth_config = AzureDevopsAuthConfig(
        company_slug='company_slug',
        token='let-me-in',
        base_url=TEST_BASE_URL,
        session=session,
    )
    if api_version:
        auth_config.api_version = api_version
    return AzureDevopsClient(auth_config)

def test_format_datetime_to_ado_str():
    dt = datetime(2024, 11, 12, 4, 30, 0)
    assert AzureDevopsClient.format_datetime_to_ado_str(dt) == '2024-11-12'

def test_get_json(requests_mock: requests_mock.Mocker):
    def _test_get_json(status_code: int, api_version: str = '7.0', ignore_404: bool = False):
        requests_mock.reset()
        client = _get_client(api_version=api_version)
        # Mock classes/data
        session_mock_return_data = {'data': {'results': [1, 2, 3]}}
        params = {}

        url = f'{TEST_BASE_URL}?api-version={api_version}'
        continuation_token = 'onwards!!!'
        requests_mock.get(
            url,
            headers={CONTINUATION_TOKEN_HEADER_SLUG: continuation_token},
            json=session_mock_return_data,
            status_code=status_code,
        )
        response, returned_continuation_token = client.get_json(
            url=f'{TEST_BASE_URL}', params={}, ignore404=ignore_404
        )
        assert api_version == requests_mock.last_request.qs['api-version'][0]
        if status_code == 404 and ignore_404:
            assert response == {}
            assert returned_continuation_token == None
            return
        assert returned_continuation_token == continuation_token
        assert response == session_mock_return_data

    # Basic smoke test
    _test_get_json(200)
    # Test that API version works with non default value
    _test_get_json(200, api_version='6.4')

    # Test that API version works with non default value
    _test_get_json(404, ignore_404=True)

    with pytest.raises(requests.exceptions.HTTPError):
        _test_get_json(404, ignore_404=False)
        _test_get_json(500)


# NOTE: This test is effectively the same as above
def test_get_single_object(requests_mock: requests_mock.Mocker):
    def _test_get_json(status_code: int, api_version: str = '7.0', ignore_404: bool = False):
        requests_mock.reset()
        client = _get_client(api_version=api_version)
        # Mock classes/data
        session_mock_return_data = {'data': {'results': [1, 2, 3]}}
        params = {}

        url = f'{TEST_BASE_URL}?api-version={api_version}'
        continuation_token = 'onwards!!!'
        requests_mock.get(
            url,
            headers={CONTINUATION_TOKEN_HEADER_SLUG: continuation_token},
            json=session_mock_return_data,
            status_code=status_code,
        )
        response = client.get_single_object(url=f'{TEST_BASE_URL}', params={}, ignore404=ignore_404)
        assert api_version == requests_mock.last_request.qs['api-version'][0]
        if status_code == 404 and ignore_404:
            assert response == {}
            return
        assert response == session_mock_return_data

    # Basic smoke test
    _test_get_json(200)
    # Test that API version works with non default value
    _test_get_json(200, api_version='6.4')

    # Test that API version works with non default value
    _test_get_json(404, ignore_404=True)

    with pytest.raises(requests.exceptions.HTTPError):
        _test_get_json(404, ignore_404=False)
        _test_get_json(500)


def test_get_single_page(requests_mock: requests_mock.Mocker):
    client = _get_client()
    result_container_str = f'date_is_here'
    result_page = ["page", "list", "results"]
    # Mock classes/data
    session_mock_return_data = {result_container_str: result_page}

    url = f'{TEST_BASE_URL}?api-version={client.api_version}'
    requests_mock.get(url, headers={}, json=session_mock_return_data, status_code=200)
    results_from_client = client.get_single_page(url=url, result_container=result_container_str)

    assert result_page == results_from_client


def test_get_single_page_on_ignore_404(requests_mock: requests_mock.Mocker):
    client = _get_client()
    result_container_str = f'date_is_here'
    result_page = ["page", "list", "results"]
    # Mock classes/data
    session_mock_return_data = {result_container_str: result_page}

    url = f'{TEST_BASE_URL}?api-version={client.api_version}'
    requests_mock.get(url, headers={}, json=session_mock_return_data, status_code=404)
    results_from_client = client.get_single_page(
        url=url, result_container=result_container_str, ignore404=True
    )

    assert [] == results_from_client


def test_get_all_pages_using_skip_and_top_one_page(requests_mock: requests_mock.Mocker):
    client = _get_client()

    url = f'{TEST_BASE_URL}'

    result_container = 'value'
    page_results = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    response = {result_container: page_results, 'count': len(page_results)}
    page_size = 100
    requests_mock.get(
        f'{url}?api-version=7.0&%24skip=0&%24top={page_size}',
        headers={},
        json=response,
        status_code=200,
    )

    results = list(
        client.get_all_pages_using_skip_and_top(
            url, result_container=result_container, top=page_size
        )
    )

    assert results == list(page_results)


def test_get_all_pages_using_skip_and_top_multi_page(requests_mock: requests_mock.Mocker):
    client = _get_client()

    url = f'{TEST_BASE_URL}'

    result_container = 'value'
    page_size = 3
    page_one_result = [1, 2, 3]
    page_one_response = {result_container: page_one_result, 'count': len(page_one_result)}
    requests_mock.get(
        f'{url}?api-version=7.0&%24skip=0&%24top={page_size}',
        headers={},
        json=page_one_response,
        status_code=200,
    )
    page_two_results = [4, 5, 6]
    page_two_response = {result_container: page_two_results, 'count': len(page_two_results)}
    requests_mock.get(
        f'{url}?api-version=7.0&%24skip=3&%24top={page_size}',
        headers={},
        json=page_two_response,
        status_code=200,
    )
    page_three_results = [7, 8]
    page_three_response = {result_container: page_three_results, 'count': len(page_three_results)}
    requests_mock.get(
        f'{url}?api-version=7.0&%24skip=6&%24top={page_size}',
        headers={},
        json=page_three_response,
        status_code=200,
    )
    results = list(
        client.get_all_pages_using_skip_and_top(
            url, result_container=result_container, top=page_size
        )
    )

    assert results == list(chain(page_one_result, page_two_results, page_three_results))


def test_get_all_pages_using_skip_and_top_check_assertion_error(
    requests_mock: requests_mock.Mocker,
):
    client = _get_client()

    url = f'{TEST_BASE_URL}'

    result_container = 'value'
    page_results = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    response = {result_container: page_results, 'count': len(page_results)}
    page_size = 100
    requests_mock.get(
        f'{url}?api-version=7.0&%24skip=0&%24top={page_size}',
        headers={CONTINUATION_TOKEN_HEADER_SLUG: 'continuation_token'},
        json=response,
        status_code=200,
    )

    with pytest.raises(AssertionError):
        list(
            client.get_all_pages_using_skip_and_top(
                url, result_container=result_container, top=page_size
            )
        )


def test_get_all_pages_using_pagination_token(requests_mock: requests_mock.Mocker):
    client = _get_client()
    url = f'{TEST_BASE_URL}'
    result_page_one = [1, 2, 3]
    result_page_two = [4, 5, 6]
    result_page_three = [7, 8, 9]

    result_container = 'value'

    def _create_response(result_list):
        return {result_container: result_list}

    requests_mock.get(
        f'{url}?api-version=7.0',
        headers={CONTINUATION_TOKEN_HEADER_SLUG: '1'},
        json=_create_response(result_page_one),
        status_code=200,
    )
    requests_mock.get(
        f'{url}?api-version=7.0&continuationToken=1',
        headers={CONTINUATION_TOKEN_HEADER_SLUG: '2'},
        json=_create_response(result_page_two),
        status_code=200,
    )
    requests_mock.get(
        f'{url}?api-version=7.0&continuationToken=2',
        headers={},
        json=_create_response(result_page_three),
        status_code=200,
    )

    results = list(client.get_all_pages_using_pagination_token(url=url))

    assert results == list(chain(result_page_one, result_page_two, result_page_three))


def test_get_all_pages_using_pagination_token_one_page(requests_mock: requests_mock.Mocker):
    client = _get_client()
    url = f'{TEST_BASE_URL}'
    results = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    result_container = 'value'

    def _create_response(result_list):
        return {result_container: result_list}

    requests_mock.get(
        f'{url}?api-version=7.0', headers={}, json=_create_response(results), status_code=200
    )

    response_results = list(client.get_all_pages_using_pagination_token(url=url))

    assert response_results == results
