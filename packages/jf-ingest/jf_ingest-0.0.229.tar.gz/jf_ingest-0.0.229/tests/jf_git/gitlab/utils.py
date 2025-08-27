from functools import partial
import json
from typing import Dict, List

import requests
import requests_mock

from jf_ingest.constants import Constants

PATH_TO_TEST_FIXTURES = 'tests/jf_git/gitlab/fixtures'

TEST_COMPANY_SLUG = 'A-Company'
TEST_BASE_URL = 'https://www.a-website.com'
TEST_BASE_GQL_URL = f'{TEST_BASE_URL}/api/graphql'
TEST_TOKEN = 'A Spoofed Token'
TEST_ORG_LOGIN = '1'
TEST_FULL_PATH = 'test-full-path'
TEST_INSTANCE_SLUG = 'a-test-instance-slug'
TEST_INSTANCE_FILE_KEY = 'a-test-file-key'
EXPECTED_AUTH_HEADER = {
    'Authorization': f'Bearer {TEST_TOKEN}',
    'Content-Type': 'application/json',
    'User-Agent': f'{Constants.JELLYFISH_USER_AGENT} ({requests.utils.default_user_agent()})',
}

def get_fixture_data(file_name: str):
    with open(file=f'{PATH_TO_TEST_FIXTURES}/{file_name}', mode='r') as f:
        return json.loads(f.read())
    
def get_object_data_page(object_name: str, page_number: int):
    return get_fixture_data(f'raw_{object_name}_page_{page_number}.json')

def get_raw_organizations(page_number: int):
    return get_fixture_data(f'raw_organizations_page_{page_number}.json')

def get_raw_repositories(page_number: int):
    return get_fixture_data(f'raw_repositories_page_{page_number}.json')

def spoof_pages_for_object(object_name: str, path_to_object_data: str, requests_mock: requests_mock.Mocker) -> List[Dict]:
    
    pages = []
    while True:
        try:
            pages.append(
                get_object_data_page(object_name, len(pages) + 1)
            )
        except Exception:
            print(f'Found {len(pages)} for object {object_name}')
            break
    
    
    # Get relevant data and yield it
    path_tokens = path_to_object_data.split('.')
    combined_raw_objects = []
    page_info_blocks = []
    for page in pages:
        result = page
        for token in path_tokens:
            if 'pageInfo' in result:
                page_info_blocks.append(result['pageInfo'])
            result = result[token]
        combined_raw_objects.extend(result)
        
        
    previous_end_cursor = None
            
    def _matcher(request: requests.Request, end_cursor):
        if f'after: {end_cursor}' in request.json()['query']:
            return True
        return None
    
    for objects, page_info in zip(pages, page_info_blocks):
        end_cursor = 'null' if not previous_end_cursor else f'"{previous_end_cursor}"'
        
        requests_mock.post(
            url=TEST_BASE_GQL_URL, 
            request_headers=EXPECTED_AUTH_HEADER,
            additional_matcher=partial(_matcher, end_cursor=end_cursor),
            json=objects,
        )
        previous_end_cursor = page_info['endCursor']
            
    return combined_raw_objects

def spoof_organizations_through_gql(requests_mock: requests_mock.Mocker) -> List[Dict]:
    return spoof_pages_for_object('organizations', path_to_object_data='data.groupsQuery.groups', requests_mock=requests_mock)


def spoof_repositories_through_gql(requests_mock: requests_mock.Mocker) -> List[Dict]:
    return spoof_pages_for_object('repositories', path_to_object_data='data.group.projectsQuery.projects', requests_mock=requests_mock)