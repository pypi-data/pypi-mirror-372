import requests
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