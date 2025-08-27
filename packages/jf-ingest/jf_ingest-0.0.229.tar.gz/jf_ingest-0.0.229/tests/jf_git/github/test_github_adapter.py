
from dataclasses import asdict
from unittest.mock import patch
import pytest
from jf_ingest.config import GitAuthConfig, GitConfig, GitProvider, GithubAuthConfig
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.adapters.github import GithubAdapter
from jf_ingest.jf_git.clients.github import GithubClient
from jf_ingest.jf_git.standardized_models import StandardizedOrganization
from tests.jf_git.github.utils import (
    TEST_COMPANY_SLUG,
    TEST_BASE_URL,
    TEST_BASE_GQL_URL,
    TEST_INSTANCE_FILE_KEY,
    TEST_INSTANCE_SLUG,
    TEST_TOKEN
)

TEST_GIT_AUTH_CONFIG = GitAuthConfig(
        company_slug=TEST_COMPANY_SLUG,
        base_url=TEST_BASE_URL,
        token=TEST_TOKEN,
        verify=False,
    )
BASE_ORGANIZATION = StandardizedOrganization(
    id='org_login',
    name='An Organizaiton',
    login='org_login',
    url='www.organization.com'
)

GITHUB_CONFIG = GitConfig(
    company_slug=TEST_COMPANY_SLUG,
    instance_slug=TEST_INSTANCE_SLUG,
    instance_file_key=TEST_INSTANCE_FILE_KEY,
    git_provider=GitProvider.GITHUB,
    git_auth_config=TEST_GIT_AUTH_CONFIG,
    git_organizations=[BASE_ORGANIZATION.login]
)

BASE_ORGANIZATION_FULL_PATH = 'group_full_path'


def _get_github_adapter() -> GithubAdapter:
    adapter: GithubAdapter = GitAdapter.get_git_adapter(GITHUB_CONFIG)
    return adapter

def test_github_adapter():
    gitlab_adapter = _get_github_adapter()
    assert type(gitlab_adapter) == GithubAdapter
    assert gitlab_adapter.config.git_provider == GitProvider.GITHUB
    assert type(gitlab_adapter.client) == GithubClient
    
TEST_BASE_URL = 'https://gav.com/gql'

# Shared test data
GQL_DATETIME_STR = "2024-12-29T12:00:58Z"
    
@pytest.fixture
def github_adapter():
    print(f'Getting adapter')
    return _get_github_adapter()

def test_get_api_scopes(github_adapter: GithubAdapter):
    ret_val = '[user:email, repo, user, organization]'
    with patch.object(GithubClient, 'get_scopes_of_api_token', return_value=ret_val):
        github_adapter.get_api_scopes() == ret_val
        
def test_get_api_scopes(github_adapter: GithubAdapter):
    ret_val = '[user:email, repo, user, organization]'
    with patch.object(GithubClient, 'get_scopes_of_api_token', return_value=ret_val):
        github_adapter.get_api_scopes() == ret_val
        
def test_get_organizations_discover(github_adapter: GithubAdapter):
    github_adapter.config.discover_organizations = True
    raw_orgs = [
        {
            'id': 'id_1',
            'login': 'login_1',
            'name': 'name_1',
            'url': 'www.url-1.com'
        },
        {
            'id': 'id_2',
            'login': 'login_2',
            'name': 'name_2',
            'url': 'www.url-2.com'
        },
    ]
    with patch.object(GithubClient, 'get_all_organizations', return_value=raw_orgs):
        standardized_orgs = github_adapter.get_organizations()
        assert len(standardized_orgs) == len(raw_orgs)
        for org, raw_org in zip(standardized_orgs, raw_orgs):
            assert type(org) == StandardizedOrganization
            assert org.id == raw_org['id']
            assert org.login == raw_org['login']
            assert org.name == raw_org['name']
            assert org.url == raw_org['url']
        
def test_get_organizations_not_discover(github_adapter: GithubAdapter):
    github_adapter.config.discover_organizations = False
    with patch.object(GithubClient, 'get_organization_by_login', return_value=asdict(BASE_ORGANIZATION)):
        standardized_orgs = github_adapter.get_organizations()
        assert len(standardized_orgs) == 1
        org = standardized_orgs[0]
        assert type(org) == StandardizedOrganization
        assert org.id == BASE_ORGANIZATION.id
        assert org.login == BASE_ORGANIZATION.login
        assert org.name == BASE_ORGANIZATION.name
        assert org.url == BASE_ORGANIZATION.url