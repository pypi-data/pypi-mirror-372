import json
from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock
from requests_mock.exceptions import NoMockAddress

from jf_ingest.config import GitLabAuthConfig
from jf_ingest.constants import Constants
from jf_ingest.jf_git.clients.gitlab import GitlabClient
from jf_ingest.utils import RetryLimitExceeded
from tests.jf_git.gitlab.utils import (
    EXPECTED_AUTH_HEADER,
    TEST_BASE_GQL_URL,
    TEST_BASE_URL,
    TEST_COMPANY_SLUG,
    TEST_TOKEN,
    get_fixture_data,
    spoof_organizations_through_gql,
    spoof_repositories_through_gql,
)


def test_gitlab_client_constructor():
    auth_config = GitLabAuthConfig(
        company_slug=TEST_COMPANY_SLUG,
        base_url=TEST_BASE_URL,
        token=TEST_TOKEN,
        verify=False,
    )
    with patch.object(GitlabClient, 'get_api_version', return_value='17.4'):
        client = GitlabClient(auth_config)

    assert client.company_slug == auth_config.company_slug
    assert client.gql_base_url == f'{auth_config.base_url}/api/graphql'
    assert client.rest_api_url == auth_config.base_url
    assert client.session.headers['Authorization'] == f'Bearer {auth_config.token}'
    assert client.session.headers['Content-Type'] == 'application/json'


def test_gitlab_client_compat_configuration():
    auth_config = GitLabAuthConfig(
        company_slug=TEST_COMPANY_SLUG,
        base_url=TEST_BASE_URL,
        token=TEST_TOKEN,
        verify=False,
    )
    # This is list of tuples containing the version to test and a value for gql_skip_pr_closed_at.
    # We may want to spoof full configurations as more keys are added.
    test_values = [('17.4.0', False), ('17.4.0-pre', False), ('17.6.1', False), ('16.4.0-ee', True), ('16.4.0', True), ('garbage_input', True)]
    for test_value in test_values:
        with patch.object(GitlabClient, 'get_api_version', return_value=test_value[0]):
            client = GitlabClient(auth_config)
        assert client.compatibility_config['gql_skip_pr_closed_at'] == test_value[1]

def test_gitlab_client_constructor_with_passed_in_session():
    spoofed_session = requests.Session()
    spoofed_header_key = 'Spoofed-Header'
    spoofed_header_value = 123
    spoofed_session.headers.update({
        spoofed_header_key: spoofed_header_value
    })
    auth_config = GitLabAuthConfig(
        company_slug='A-Company',
        base_url='www.company.net',
        token='A Spoofed Token',
        verify=False,
        session=spoofed_session
    )
    with patch.object(GitlabClient, 'get_api_version', return_value='17.4'):
        client = GitlabClient(auth_config)

    assert client.company_slug == auth_config.company_slug
    assert client.gql_base_url == f'{auth_config.base_url}/api/graphql'
    assert client.rest_api_url == auth_config.base_url
    assert client.session.headers[spoofed_header_key] == spoofed_header_value



@pytest.fixture()
def client():
    auth_config = GitLabAuthConfig(
        company_slug=TEST_COMPANY_SLUG,
        base_url=TEST_BASE_URL,
        token=TEST_TOKEN,
        verify=False,
    )
    with patch.object(GitlabClient, 'get_api_version', return_value='17.4'):
        return GitlabClient(auth_config)

def test_get_raw_gql_result_simple(client: GitlabClient, requests_mock: requests_mock.Mocker):
    # Test Data
    test_query_body = "test_query_body"
    # Mock classes/data
    session_mock_caller_data = {'query': test_query_body}
    session_mock_return_data = {'data': {'test_key': 'test_value'}}
    requests_mock.post(url=TEST_BASE_GQL_URL, json=session_mock_return_data, request_headers=EXPECTED_AUTH_HEADER)

    # call function
    returned_data = client.get_raw_result_gql(query_body=test_query_body)

    assert returned_data == session_mock_return_data
    assert requests_mock.last_request.json() == session_mock_caller_data

def test_get_organization_full_path(client: GitlabClient, requests_mock: requests_mock.Mocker):
    raw_data = get_fixture_data('raw_organization_from_rest_api.json')
    group_id = raw_data['id']
    requests_mock.get(
        url=f'{TEST_BASE_URL}/api/v4/groups/{group_id}?with_projects=False', 
        json=raw_data, 
        request_headers=EXPECTED_AUTH_HEADER
    )
    
    name, full_path_response, web_url = client.get_organization_name_full_path_and_url(login=group_id)
    
    assert name == raw_data['name']
    assert full_path_response == raw_data['full_path']
    assert web_url == raw_data['web_url']
    
def test_get_raw_gql_results_retries_on_429s(mocker, client: GitlabClient, requests_mock: requests_mock.Mocker):
    attempts = 10
    requests_mock.post(url=TEST_BASE_GQL_URL, request_headers=EXPECTED_AUTH_HEADER, status_code=429)
    with mocker.patch('time.sleep', return_value=None), pytest.raises(RetryLimitExceeded):
        client.get_raw_result_gql('', max_attempts=attempts)
        assert requests_mock.call_count == attempts

def test_get_raw_gql_result_verify_headers_present(client: GitlabClient, requests_mock: requests_mock.Mocker):
    # Test Data
    test_query_body = "test_query_body"
    # Mock classes/data
    session_mock_caller_data = {'query': test_query_body}
    session_mock_return_data = {'data': {'test_key': 'test_value'}}
    requests_mock.post(url=TEST_BASE_GQL_URL, json=session_mock_return_data, request_headers=EXPECTED_AUTH_HEADER)

    # call function
    returned_data = client.get_raw_result_gql(query_body=test_query_body)

    assert returned_data == session_mock_return_data
    assert requests_mock.last_request.json() == session_mock_caller_data
 
def test_get_raw_gql_result_verify_headers_not_present(client: GitlabClient, requests_mock: requests_mock.Mocker):
    requests_mock.post(url=TEST_BASE_GQL_URL, json={}, request_headers={'Authorization': "A BAD TOKEN"})
    with pytest.raises(NoMockAddress):
        client.get_raw_result_gql(query_body='')
        
def test_page_results_gql_no_next_page(client: GitlabClient, requests_mock: requests_mock.Mocker):
    path_to_page_results = 'data.pages'
    query = """
        {{
            pages(first: %s, cursor: %s) {{
                pageInfo {{ hasNextPage, endCursor }}
                id, name
            }}
        }}
    """
    json_payload = {
            'data': {
                'pages': {
                    'pageInfo': {
                        'hasNextPage': False,
                        'endCursor': '123'
                    },
                    'page': [
                        {
                            'id': 1,
                            'name': 'one'
                        },
                        {
                            'id': 2,
                            'name': 'two'
                        }
                    ]
                }
            }
        }
    requests_mock.post(
        url=TEST_BASE_GQL_URL, 
        request_headers=EXPECTED_AUTH_HEADER,
        json=json_payload,
    )
    results = []
    for result_page in client.page_results_gql(query_body=query, path_to_page_info=path_to_page_results, page_size=2):
        for item in result_page['data']['pages']['page']:
            results.append(item)
            
    assert len(results) == 2
    assert results[0]['id'] == 1
    assert results[1]['id'] == 2

def test_get_organizations_with_gql(client: GitlabClient, requests_mock: requests_mock.Mocker):
    combined_raw_groups = spoof_organizations_through_gql(requests_mock)
    
    organizations = [o for o in client.get_organizations_gql()]
    assert len(organizations) == len(combined_raw_groups)
    for group in organizations:
        assert group in combined_raw_groups

def test_get_repositories_with_gql(client: GitlabClient, requests_mock: requests_mock.Mocker):
    combined_raw_repos = spoof_repositories_through_gql(requests_mock)
    
    repos = [o for o in client.get_repos_gql(group_full_path='')]
    assert len(repos) == len(combined_raw_repos)
    assert len(repos) == 2
    for repo in repos:
        assert repo in combined_raw_repos
