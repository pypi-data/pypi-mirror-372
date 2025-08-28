from datetime import datetime, timedelta, timezone

import pytest

from jf_ingest.config import GitAuthConfig, GitConfig, GitProvider
from jf_ingest.jf_git.adapters import (
    BackpopulationWindow,
    GitAdapter,
    determine_commit_backpopulation_window,
    determine_pr_backpopulation_window,
)
from jf_ingest.jf_git.adapters.github import GithubAdapter
from jf_ingest.jf_git.standardized_models import (
    StandardizedBranch,
    StandardizedCommit,
    StandardizedOrganization,
    StandardizedRepository,
)

GIT_CONFIG_DEFAULTS = {
    'company_slug': 'test_company',
    'instance_slug': 'test_instance',
    'instance_file_key': 'test_FILEKEY',
    'git_provider': 'GITHUB',
    'git_auth_config': None,
}

GIT_TEST_ORG = StandardizedOrganization(id='test_org', name='Test Org', login='Test-Org', url='')
GIT_TEST_REPO = StandardizedRepository(
    id='1',
    name='test_repo',
    full_name='test_repo_full_name',
    url='',
    is_fork=False,
    default_branch_name='main',
    default_branch_sha='test',
    organization=GIT_TEST_ORG,
)

TEST_GIT_AUTH_CONFIG = GitAuthConfig(
        company_slug='TEST COMPANY',
        base_url='www.base.com',
        token='apples',
        verify=False,
    )
BASE_ORGANIZATION = StandardizedOrganization(
    id='org_login',
    name='An Organizaiton',
    login='org_login',
    url='www.organization.com'
)

ALT_BASE_ORGANIZATION = StandardizedOrganization(
    id='org_login_alt',
    name='An Alternative Organizaiton',
    login='org_login_alt',
    url='www.organization.com'
)

GITHUB_CONFIG = GitConfig(
    company_slug=TEST_GIT_AUTH_CONFIG.company_slug,
    instance_slug=f'{TEST_GIT_AUTH_CONFIG}_slug',
    instance_file_key='TEST_INSTANCE_FILE_KEY',
    git_provider=GitProvider.GITHUB,
    git_auth_config=TEST_GIT_AUTH_CONFIG,
    git_organizations=[BASE_ORGANIZATION.login]
)

@pytest.fixture
def adapter() -> GitAdapter:
    # We can't stand up the abstract GitAdapter class,
    # so for now just use the GithubAdapter child class
    return GithubAdapter(GITHUB_CONFIG)

def create_git_config(*args, **kwargs):
    return GitConfig(*args, **kwargs)

STANDARDIZED_REPOS = [
    StandardizedRepository(
        id='repo_1',
        name='repo_1_name',
        full_name='repository_1_name',
        url='www.repo1.com',
        is_fork=False,
        default_branch_name='main',
        default_branch_sha='',
        organization=BASE_ORGANIZATION
    ),
    StandardizedRepository(
        id='repo_2',
        name='repo_2_name',
        full_name='repository_2_name',
        url='www.repo2.com',
        is_fork=False,
        default_branch_name='develop',
        default_branch_sha='',
        organization=BASE_ORGANIZATION
    ),
    StandardizedRepository(
        id='repo_3',
        name='repo_3_name',
        full_name='repository_3_name',
        url='www.repo3.com',
        is_fork=False,
        default_branch_name='main',
        default_branch_sha='',
        organization=ALT_BASE_ORGANIZATION
    )
]
    

def test_transform_repos_before_saving(adapter: GitAdapter):
    adapter.config.git_redact_names_and_urls = False
    adapter.config.git_strip_text_content = False
    transformed_objects = adapter._transform_data_objects_before_saving(STANDARDIZED_REPOS)
    for transformed_object, object in zip(transformed_objects, STANDARDIZED_REPOS):
        assert object.id == transformed_object['id']
        assert object.name == transformed_object['name']
        assert object.full_name == transformed_object['full_name']
        assert object.url == transformed_object['url']
        assert object.is_fork == transformed_object['is_fork']
        assert object.default_branch_sha == transformed_object['default_branch_sha']
        assert object.default_branch_name == transformed_object['default_branch_name']
        assert object.organization.name == transformed_object['organization']['name']
        assert object.organization.url == transformed_object['organization']['url']
    

def test_transform_repos_before_saving_with_strip_text(adapter: GitAdapter):
    adapter.config.git_redact_names_and_urls = False
    adapter.config.git_strip_text_content = True
    transformed_objects = adapter._transform_data_objects_before_saving(STANDARDIZED_REPOS)
    for transformed_object, object in zip(transformed_objects, STANDARDIZED_REPOS):
        assert object.id == transformed_object['id']
        assert object.name == transformed_object['name']
        assert object.full_name == transformed_object['full_name']
        assert object.url == transformed_object['url']
        assert object.is_fork == transformed_object['is_fork']
        assert object.default_branch_sha == transformed_object['default_branch_sha']
        assert object.default_branch_name == transformed_object['default_branch_name']
        assert object.organization.name == transformed_object['organization']['name']
        assert object.organization.url == transformed_object['organization']['url']

def test_transform_repos_before_saving_with_redaction(adapter: GitAdapter):
    adapter.config.git_redact_names_and_urls = True
    adapter.config.git_strip_text_content = False
    transformed_objects = adapter._transform_data_objects_before_saving(STANDARDIZED_REPOS)
    repo_redaction_index = 0
    for (transformed_object, object) in zip(transformed_objects, STANDARDIZED_REPOS):
        assert object.id == transformed_object['id']
        assert f'redacted-000{repo_redaction_index}' == transformed_object['name']
        assert f'redacted-000{repo_redaction_index+1}' == transformed_object['full_name']
        assert None == transformed_object['url']
        assert object.is_fork == transformed_object['is_fork']
        assert object.default_branch_sha == transformed_object['default_branch_sha']
        if object.id == 'repo_3':  # Repo 3 is in a differnt org, so the redaction counter should go up
            assert f'redacted-0001' == transformed_object['organization']['name']
        else:
            assert f'redacted-0000' == transformed_object['organization']['name']
        assert None == transformed_object['organization']['url']
        
        repo_redaction_index += 2

# Test strip text content with commits
STANDARDIZED_COMMITS = [
    StandardizedCommit(
        hash='1234',
        url='www.commit-1.com',
        message='OJ-12342: new commit',
        commit_date=datetime(2024, 1, 1),
        author=datetime(2024, 1, 1),
        author_date=None,
        repo=STANDARDIZED_REPOS[0],
        is_merge=False,
        branch_name='main'
    ),
    StandardizedCommit(
        hash='12345',
        url='www.commit-2.com',
        message='OJ-60845515: new commit',
        commit_date=datetime(2024, 1, 1),
        author=datetime(2024, 1, 1),
        author_date=None,
        repo=STANDARDIZED_REPOS[-1],
        is_merge=False,
        branch_name='master'
    ),
]

def test_transform_commits_before_saving(adapter: GitAdapter):
    adapter.config.git_redact_names_and_urls = False
    adapter.config.git_strip_text_content = False
    transformed_objects = adapter._transform_data_objects_before_saving(STANDARDIZED_COMMITS)
    for transformed_object, standardized_object in zip(transformed_objects, STANDARDIZED_COMMITS):
        assert transformed_object['hash'] == standardized_object.hash
        assert transformed_object['url'] == standardized_object.url
        assert transformed_object['message'] == standardized_object.message
        assert transformed_object['commit_date'] == standardized_object.commit_date
        assert transformed_object['author_date'] == standardized_object.author_date
        assert transformed_object['author'] == standardized_object.author
        assert transformed_object['is_merge'] == standardized_object.is_merge
        assert transformed_object['branch_name'] == standardized_object.branch_name
        # short repo fields
        assert transformed_object['repo']['id'] == standardized_object.repo.id
        assert transformed_object['repo']['name'] == standardized_object.repo.name
        assert transformed_object['repo']['full_name'] == standardized_object.repo.full_name
        assert transformed_object['repo']['url'] == standardized_object.repo.url
        # Org fields
        assert transformed_object['repo']['organization']['login'] == standardized_object.repo.organization.login
        assert transformed_object['repo']['organization']['url'] == standardized_object.repo.organization.url
        assert transformed_object['repo']['organization']['name'] == standardized_object.repo.organization.name
        
        
def test_transform_commits_before_saving_with_redact_and_strip(adapter: GitAdapter):
    adapter.config.git_redact_names_and_urls = True
    adapter.config.git_strip_text_content = True
    transformed_objects = adapter._transform_data_objects_before_saving(STANDARDIZED_COMMITS)
    branch_redaction_index = 0
    repo_redaction_index = 0
    organization_redaction_index = 0
    for transformed_object, standardized_object in zip(transformed_objects, STANDARDIZED_COMMITS):
        assert transformed_object['hash'] == standardized_object.hash
        assert transformed_object['url'] == None
        assert 'OJ-60845515' == transformed_object['message'] or transformed_object['message'] == 'OJ-12342'
        assert transformed_object['commit_date'] == standardized_object.commit_date
        assert transformed_object['author_date'] == standardized_object.author_date
        assert transformed_object['author'] == standardized_object.author
        assert transformed_object['is_merge'] == standardized_object.is_merge
        assert transformed_object['branch_name'] == f'redacted-000{branch_redaction_index}' or transformed_object['branch_name'] == 'master'
        # short repo fields
        assert transformed_object['repo']['id'] == standardized_object.repo.id
        assert transformed_object['repo']['name'] == f'redacted-000{repo_redaction_index}'
        assert transformed_object['repo']['full_name'] == f'redacted-000{repo_redaction_index + 1}'
        assert transformed_object['repo']['url'] == None
        # Orgs
        assert transformed_object['repo']['organization']['login'] == standardized_object.repo.organization.login and 'redacted' not in standardized_object.repo.organization.login
        assert transformed_object['repo']['organization']['url'] == None
        assert transformed_object['repo']['organization']['name'] == f'redacted-000{organization_redaction_index}'
        repo_redaction_index += 4
        organization_redaction_index += 1
        branch_redaction_index += 1

def test_backpopulation_window_helper_confirm_always_none_cases():
    pull_from = datetime(2024, 1, 1)
    object_last_pulled_date = pull_from

    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        'backpopulation_window_days': 10,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == None
    assert prs_back_population_window == None

    ######################################################
    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        'backpopulation_window_days': 10,
        'repos_to_prs_backpopulated_to': {
            GIT_TEST_REPO.id: object_last_pulled_date - timedelta(days=1)
        },
        'repos_to_commits_backpopulated_to': {
            GIT_TEST_REPO.id: object_last_pulled_date - timedelta(days=1)
        },
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == None
    assert prs_back_population_window == None


def test_backpopulation_window_helper_with_force_pull():
    pull_from = datetime(2024, 1, 1)
    object_last_pulled_date = datetime(2024, 2, 1)
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert prs_back_population_window == BackpopulationWindow(pull_from, object_last_pulled_date)

    #############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        pull_from, object_last_pulled_date
    )


def test_backpopulation_window_helper_with_custom_days_window():
    pull_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
    object_last_pulled_date = datetime(2024, 2, 1, tzinfo=timezone.utc)
    backpop_window_days = 10
    target_backpopulation_start_date = object_last_pulled_date - timedelta(days=backpop_window_days)
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert prs_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )

    #############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )

    ##############################
    git_config_args = {
        'pull_from': pull_from,
        'repos_to_prs_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'repos_to_commits_backpopulated_to': {GIT_TEST_REPO.id: object_last_pulled_date},
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )
    assert prs_back_population_window == BackpopulationWindow(
        target_backpopulation_start_date, object_last_pulled_date
    )


def test_backpopulation_window_when_there_is_no_data_in_jellyfish():
    pull_from = datetime(2024, 1, 1, tzinfo=timezone.utc)
    start_time = datetime.now().astimezone(timezone.utc)
    backpop_window_days = 10
    git_config_args = {
        'pull_from': pull_from,
        'backpopulation_window_days': backpop_window_days,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_end >= start_time
    assert (
        prs_back_population_window.backpopulation_window_end
        - prs_back_population_window.backpopulation_window_start
    ).days == 10
    assert (
        commits_back_population_window.backpopulation_window_end
        - commits_back_population_window.backpopulation_window_start
    ).days == 10

    #####################################################
    git_config_args = {
        'pull_from': pull_from,
        'force_full_backpopulation_pull': True,
        **GIT_CONFIG_DEFAULTS,
    }
    config = create_git_config(**git_config_args)
    repo = GIT_TEST_REPO

    prs_back_population_window = determine_pr_backpopulation_window(config=config, repo=repo)
    commits_back_population_window = determine_commit_backpopulation_window(
        config=config, repo=repo
    )
    assert commits_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_end >= start_time
    assert prs_back_population_window.backpopulation_window_start == pull_from
    assert commits_back_population_window.backpopulation_window_start == pull_from
