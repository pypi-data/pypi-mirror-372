import json

from jf_ingest.config import AzureDevopsAuthConfig, GitConfig, GitProvider
from jf_ingest.jf_git.adapters.azure_devops import AzureDevopsAdapter
from jf_ingest.jf_git.standardized_models import (
    StandardizedOrganization,
    StandardizedRepository,
)

PATH_TO_TEST_FIXTURES = 'tests/jf_git/ado/fixtures'
TEST_BASE_URL = 'https://ado.com/'
ADO_ORGANIZATION_LOGIN = 'ADO-Organization'
ADO_PROJECT_NAME = 'ADO-Project-Name'

BASIC_ORG = StandardizedOrganization(
    id=ADO_ORGANIZATION_LOGIN,
    name=ADO_ORGANIZATION_LOGIN,
    login=ADO_ORGANIZATION_LOGIN,
    url=TEST_BASE_URL,
)

BASIC_REPO = StandardizedRepository(
    id=f'STANDARD_REPO_ID',
    name='STANDARD_REPO_NAME',
    full_name=f'STANDARD_REPO_FULL_NAME',
    url=f'{TEST_BASE_URL}{ADO_ORGANIZATION_LOGIN}/{ADO_PROJECT_NAME}/_git/test',
    is_fork=False,
    default_branch_name='master',
    default_branch_sha=None,
    organization=BASIC_ORG,
    commits_backpopulated_to=None,
    prs_backpopulated_to=None,
)


def get_fixture_data(file_name: str):
    with open(file=f'{PATH_TO_TEST_FIXTURES}/{file_name}', mode='r') as f:
        return json.loads(f.read())['value']


def get_raw_users():
    # This raw file is populated from this data set from the ADO docs:
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/graph/users/list?view=azure-devops-rest-7.1&tabs=HTTP
    return get_fixture_data('raw_graph_users.json')


def get_raw_teams():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/graph/groups/list?view=azure-devops-rest-7.1&tabs=HTTP
    return get_fixture_data('raw_graph_teams.json')


def get_raw_repos():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/repositories/list?view=azure-devops-rest-7.1&tabs=HTTP
    return get_fixture_data('raw_repos.json')


def get_raw_commits():
    return get_fixture_data('raw_commits.json')


def get_raw_branches():
    return get_fixture_data('raw_branches.json')


def get_raw_iterations():
    # I just made this one up, ADO doesn't provide examples
    return get_fixture_data('raw_iterations.json')


def get_raw_prs():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-requests/get-pull-requests?view=azure-devops-rest-7.1&tabs=HTTP
    return get_fixture_data('raw_prs.json')


def get_raw_diffs():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/diffs/get?view=azure-devops-rest-7.1&tabs=HTTP
    with open(file=f'{PATH_TO_TEST_FIXTURES}/raw_diff.json', mode='r') as f:
        return json.loads(f.read())['changes']


def get_raw_change_counts():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/diffs/get?view=azure-devops-rest-7.1&tabs=HTTP
    with open(file=f'{PATH_TO_TEST_FIXTURES}/raw_diff.json', mode='r') as f:
        return json.loads(f.read())['changeCounts']


def get_raw_threads_comments():
    # https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads/list?view=azure-devops-rest-7.1&tabs=HTTP
    return get_fixture_data('raw_threads.json')

def get_git_config(redact_names_and_urls: bool = False, strip_text_content: bool = False):
    auth_config = AzureDevopsAuthConfig(
        company_slug='company_slug',
        token='let-me-in',
        base_url=TEST_BASE_URL,
    )
    return GitConfig(
        company_slug='test_company',
        instance_slug='test_company_instance_slug',
        instance_file_key='FILE_KEY',
        git_auth_config=auth_config,
        git_organizations=[ADO_ORGANIZATION_LOGIN],
        git_redact_names_and_urls=redact_names_and_urls,
        git_strip_text_content=strip_text_content,
        git_provider=GitProvider.ADO,
    )
    

def get_adapter():
    config = get_git_config()
    adapter = AzureDevopsAdapter(config)
    adapter.repo_id_to_project_name[BASIC_REPO.id] = ADO_PROJECT_NAME
    return adapter

def get_adapter_from_config(config: GitConfig):
    adapter = AzureDevopsAdapter(config)
    adapter.repo_id_to_project_name[BASIC_REPO.id] = ADO_PROJECT_NAME
    return adapter