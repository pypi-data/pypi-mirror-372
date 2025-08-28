from unittest.mock import MagicMock, patch

import pytest
import requests_mock
from gitlab.v4.objects import ProjectBranch, ProjectCommit
from gitlab.v4.objects import User as GitlabUser

from jf_ingest.config import GitLabAuthConfig, GitConfig, GitProvider
from jf_ingest.utils import GitLabGidObjectMapping, get_id_from_gid, parse_gitlab_date
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.adapters.gitlab import GitlabAdapter
from jf_ingest.jf_git.clients.gitlab import GitlabClient
from jf_ingest.jf_git.standardized_models import (
    PullRequestReviewState,
    StandardizedOrganization,
    StandardizedRepository,
    StandardizedUser,
)
from jf_ingest.utils import parse_gitlab_date
from tests.jf_git.gitlab.fixtures import raw_api_responses
from tests.jf_git.gitlab.utils import (
    EXPECTED_AUTH_HEADER,
    TEST_BASE_URL,
    TEST_COMPANY_SLUG,
    TEST_INSTANCE_FILE_KEY,
    TEST_INSTANCE_SLUG,
    TEST_TOKEN,
    spoof_organizations_through_gql,
)

TEST_GIT_AUTH_CONFIG = GitLabAuthConfig(
        company_slug=TEST_COMPANY_SLUG,
        base_url=TEST_BASE_URL,
        token=TEST_TOKEN,
        verify=False,
    )

GITLAB_GIT_CONFIG = GitConfig(
    company_slug=TEST_COMPANY_SLUG,
    instance_slug=TEST_INSTANCE_SLUG,
    instance_file_key=TEST_INSTANCE_FILE_KEY,
    git_provider=GitProvider.GITLAB,
    git_auth_config=TEST_GIT_AUTH_CONFIG
)


    
BASE_ORGANIZATION = StandardizedOrganization(
    id='org_login',
    name='An Organizaiton',
    login='org_login',
    url='www.organization.com'
)
BASE_ORGANIZATION_FULL_PATH = 'group_full_path'

BASE_REPOSITORY = StandardizedRepository(
    id='repo_id',
    name='A Repository',
    full_name='A Repository',
    url='www.example.com',
    is_fork=False,
    default_branch_name='main',
    default_branch_sha='',
    organization=BASE_ORGANIZATION,
    full_path='example/path',
)

def _get_gitlab_adapter() -> GitlabAdapter:
    with patch.object(GitlabClient, 'get_api_version', return_value='17.4'):
        adapter: GitlabAdapter = GitAdapter.get_git_adapter(GITLAB_GIT_CONFIG)
        adapter.group_id_to_full_path[BASE_ORGANIZATION.login] = BASE_ORGANIZATION_FULL_PATH
        return adapter

def test_gitlab_adapter():
    gitlab_adapter = _get_gitlab_adapter()
    assert type(gitlab_adapter) == GitlabAdapter
    assert gitlab_adapter.config.git_provider == GitProvider.GITLAB
    assert type(gitlab_adapter.client) == GitlabClient
    
@pytest.fixture
def gitlab_adapter():
    print(f'Getting adapter')
    return _get_gitlab_adapter()
    
def test_gitlab_adapter_supports_date_filtering(gitlab_adapter: GitlabAdapter):
    assert gitlab_adapter.git_provider_pr_endpoint_supports_date_filtering() == True
    
def test_gitlab_adapter_get_api_scopes(gitlab_adapter: GitlabAdapter):
    with pytest.raises(NotImplementedError):
        gitlab_adapter.get_api_scopes()
        
def test_gitlab_adapter_get_group_id_from_gid():
    group_id = '1234'
    gid = f'gid://gitlab/Group/{group_id}'
    assert get_id_from_gid(gid, GitLabGidObjectMapping.GROUP.value) == group_id
    
    group_id = 'applecatbanana'
    gid = f'gid://gitlab/Group/{group_id}'
    assert get_id_from_gid(gid, GitLabGidObjectMapping.GROUP.value) == group_id
    
def test_gitlab_adapter_get_repository_id_from_gid():
    project_id = '1234'
    gid = f'gid://gitlab/Project/{project_id}'
    assert get_id_from_gid(gid, GitLabGidObjectMapping.PROJECT.value) == project_id
    
    project_id = 'applecatbanana'
    gid = f'gid://gitlab/Project/{project_id}'
    assert get_id_from_gid(gid, GitLabGidObjectMapping.PROJECT.value) == project_id
    
def test_gitlab_adapter_get_group_full_path_from_organizations(gitlab_adapter: GitlabAdapter):
    # This value is set in the gitlab_adapter fixture class
    assert gitlab_adapter.get_group_full_path_from_organization(BASE_ORGANIZATION) == BASE_ORGANIZATION_FULL_PATH
        
def test_gitlab_adapter_get_new_organizations_with_gql(gitlab_adapter: GitlabAdapter, requests_mock: requests_mock.Mocker):
    raw_groups = spoof_organizations_through_gql(requests_mock)
    gitlab_adapter.config.discover_organizations = True
    standardized_organizations = gitlab_adapter.get_organizations()
    
    assert len(raw_groups) == len(standardized_organizations)
    for standardized_org, raw_group in zip(standardized_organizations, raw_groups):
        assert type(standardized_org) == StandardizedOrganization
        group_id = get_id_from_gid(raw_group['groupIdStr'], GitLabGidObjectMapping.GROUP.value)
        assert standardized_org.id == group_id
        assert standardized_org.login == group_id
        assert standardized_org.name == raw_group['name']
        assert standardized_org.url == raw_group['webUrl']
        # Assert that we are staching a mapping between group ID and full path
        assert group_id in gitlab_adapter.group_id_to_full_path
        assert gitlab_adapter.get_group_full_path_from_id(group_id=group_id) == raw_group['fullPath']
        
def test_gitlab_adapter_get_no_new_organizations_using_rest(gitlab_adapter: GitlabAdapter, requests_mock: requests_mock.Mocker):
    gitlab_adapter.config.discover_organizations = False
    group_ids_to_get = ['1', '2', '3']
    gitlab_adapter.config.git_redact_names_and_urls = False
    gitlab_adapter.config.git_organizations = group_ids_to_get
    
    def _construct_fake_name(id: str):
        return f'name-{id}'
    
    def _construct_fake_web_url(id: str):
        return f'www.website.com/{id}'
    
    for id in group_ids_to_get:
        requests_mock.get(
            url=f'{TEST_BASE_URL}/api/v4/groups/{id}?with_projects=False',
            headers=EXPECTED_AUTH_HEADER,
            json={
                'id': f'gid://gitlab/Group/{id}',
                'name': _construct_fake_name(id),
                'full_path': f'full_path_for_{id}',
                'web_url': _construct_fake_web_url(id)
            }
        )
    
    standardized_organizations = gitlab_adapter.get_organizations()
    
    assert len(group_ids_to_get) == len(standardized_organizations)
    for standardized_org, group_id in zip(standardized_organizations, group_ids_to_get):
        assert standardized_org.id == group_id
        assert standardized_org.login == group_id
        assert standardized_org.name == _construct_fake_name(group_id)
        assert standardized_org.url == _construct_fake_web_url(group_id)
        # assert we are caching group ID to group full path
        assert group_id in gitlab_adapter.group_id_to_full_path
        assert f'full_path_for_{group_id}' == gitlab_adapter.get_group_full_path_from_id(group_id)
        
def test_gitlab_adapter_get_group_full_path_from_id(gitlab_adapter: GitlabAdapter, requests_mock: requests_mock.Mocker):
    gitlab_adapter.config.discover_organizations = False
    group_ids_to_get = ['1', '2', '3']
    gitlab_adapter.config.git_redact_names_and_urls = False
    gitlab_adapter.config.git_organizations = group_ids_to_get
    
    def _construct_fake_name(id: str):
        return f'name-{id}'
    
    def _construct_fake_web_url(id: str):
        return f'www.website.com/{id}'
    
    for id in group_ids_to_get:
        requests_mock.get(
            url=f'{TEST_BASE_URL}/api/v4/groups/{id}?with_projects=False',
            headers=EXPECTED_AUTH_HEADER,
            json={
                'id': f'gid://gitlab/Group/{id}',
                'name': _construct_fake_name(id),
                'full_path': f'full_path_for_{id}',
                'web_url': _construct_fake_web_url(id)
            }
        )
        
    for group_id in group_ids_to_get:
        # Assert when we don't have group ID cached that we will get it and then cache it
        assert group_id not in gitlab_adapter.group_id_to_full_path
        assert f'full_path_for_{group_id}' == gitlab_adapter.get_group_full_path_from_id(group_id)
        assert group_id in gitlab_adapter.group_id_to_full_path
        

def test_gitlab_adapter_get_group_full_path_from_id_assert_caching(gitlab_adapter: GitlabAdapter):
    group_id_to_full_pathes = {
        '1': 'full_path_1',
        '2': 'full_path_2',
        '3': 'full_path_3'
    }
    
    gitlab_adapter.group_id_to_full_path = group_id_to_full_pathes
    
    for group_id, full_path in group_id_to_full_pathes.items():
        # Assert we are using the dictionary and never making an API call
        assert gitlab_adapter.get_group_full_path_from_id(group_id) == full_path


def test_gitlab_get_commits_for_default_branch(gitlab_adapter: GitlabAdapter):
    raw_commits = [
        {
            "id": "ed899a2f4b50b4370feeea94676502b42383c746",
            "short_id": "ed899a2f4b5",
            "title": "Replace sanitize with escape once",
            "author_name": "Example User",
            "author_email": "user@example.com",
            "authored_date": "2021-09-20T11:50:22.001+00:00",
            "committer_name": "Administrator",
            "committer_email": "admin@example.com",
            "committed_date": "2021-09-20T11:50:22.001+00:00",
            "created_at": "2021-09-20T11:50:22.001+00:00",
            "message": "Replace sanitize with escape once",
            "parent_ids": [
                "6104942438c14ec7bd21c6cd5bd995272b3faff6"
            ],
            "web_url": "https://gitlab.example.com/janedoe/gitlab-foss/-/commit/ed899a2f4b50b4370feeea94676502b42383c746",
        },
        {
            "id": "6104942438c14ec7bd21c6cd5bd995272b3faff6",
            "title": "Sanitize for network graph",
            "author_name": "randx",
            "author_email": "randx@example.com",
            "authored_date": "2021-09-20T09:06:12.201+00:00",
            "committer_name": "ExampleName",
            "committer_email": "user@example.com",
            "committed_date": "2021-09-20T09:06:12.201+00:00",
            "created_at": "2021-09-20T09:06:12.201+00:00",
            "message": "Sanitize for network graph\nCc: John Doe <johndoe@gitlab.com>\nCc: Jane Doe <janedoe@gitlab.com>",
            "parent_ids": [
                "ae1d9fb46aa2b07ee9836d49862ec4e2c46fbbba"
            ],
            "web_url": "https://gitlab.example.com/janedoe/gitlab-foss/-/commit/ed899a2f4b50b4370feeea94676502b42383c746",
        }
    ]
    commits_response = [ProjectCommit(attrs=raw_commits[0], manager=MagicMock()), ProjectCommit(attrs=raw_commits[1], manager=MagicMock())]
    with patch.object(GitlabClient, 'get_commits', return_value=commits_response):

        standardized_commits = [commit for commit in gitlab_adapter.get_commits_for_default_branch(BASE_REPOSITORY)]
        for standardized_commit, raw_commit in zip(standardized_commits, raw_commits):
            assert standardized_commit.hash == raw_commit['id']
            assert standardized_commit.author.name == raw_commit['author_name']
            assert standardized_commit.author.email == raw_commit['author_email']
            assert standardized_commit.url == raw_commit['web_url']
            assert standardized_commit.author_date == parse_gitlab_date(raw_commit['authored_date'])
            assert standardized_commit.commit_date == parse_gitlab_date(raw_commit['committed_date'])
            assert standardized_commit.message == raw_commit['message']
            assert standardized_commit.is_merge is False
            assert standardized_commit.branch_name == 'main'  # Pulled from BASE_REPOSITORY default


def test_gitlab_get_branches_for_repo(gitlab_adapter: GitlabAdapter):
    # NOTE: These are just the bare minimum fields needed for standardization.
    raw_branches = [
        {
            "name": "main",
            "default": True,
            "commit": {
                "id": "7b5c3cc8be40ee161ae89a06bba6229da1032a0c",
            }
        },
        {
            "name": "develop",
            "default": False,
            "commit": {
                "id": "3z5c3cc8be40ee161ae89a16bba6229ds1032a0c",
            }
        },
    ]
    branches_response = [ProjectBranch(attrs=raw_branches[0], manager=MagicMock()), ProjectBranch(attrs=raw_branches[1], manager=MagicMock())]
    with patch.object(GitlabClient, 'get_branches_for_repo', return_value=branches_response) as mock_client:
        standardized_branches = [branch for branch in gitlab_adapter.get_branches_for_repo(BASE_REPOSITORY, pull_branches=True)]
        for standardized_branch, raw_branch in zip(standardized_branches, raw_branches):
            assert standardized_branch.name == raw_branch['name']
            assert standardized_branch.sha == raw_branch['commit']['id']
            assert standardized_branch.repo_id == BASE_REPOSITORY.id
            assert standardized_branch.is_default == raw_branch['default']

        mock_client.assert_called_once_with(BASE_REPOSITORY, branch_name=None)
        mock_client.reset_mock()

        # We don't care about the return result here, only that we forward the default branch name as a search term.
        # GitLab handles limiting the return results on their api by the matching name.
        sb = [b for b in gitlab_adapter.get_branches_for_repo(BASE_REPOSITORY, pull_branches=False)]
        mock_client.assert_called_once_with(BASE_REPOSITORY, branch_name=BASE_REPOSITORY.default_branch_name)
        

@pytest.fixture
def mock_gitlab_users():
    """
    Return a list of mock GitLab user objects for testing.
    Each object is a MagicMock that simulates a gitlab.v4.objects.User.
    """
    user1 = MagicMock(spec=GitlabUser)
    user1.id = 101
    user1.name = "Test User"
    user1.username = "testuser"
    user1.web_url = "http://gitlab.com/testuser"

    user2 = MagicMock(spec=GitlabUser)
    user2.id = 102
    user2.name = "Another User"
    user2.username = "anotheruser"
    user2.web_url = "http://gitlab.com/anotheruser"

    return [user1, user2]


def get_org() -> StandardizedOrganization:
    return StandardizedOrganization(
        id="12345",
        name="MockGroup",
        login="12345",
        url="http://someurl"
    )

def test_gitlab_adapter_get_users_no_limit(gitlab_adapter: GitlabAdapter, mock_gitlab_users):
    """
    Verifies that get_users returns a generator of StandardizedUser objects
    for all users if no limit is provided.
    """
    org = get_org()
    gitlab_adapter.client.get_users = MagicMock(return_value=mock_gitlab_users)
    result = list(gitlab_adapter.get_users(standardized_organization=org, limit=None))

    gitlab_adapter.client.get_users.assert_called_once_with(group_id="12345")
    assert len(result) == len(mock_gitlab_users)
    for idx, standardized_user in enumerate(result):
        assert isinstance(standardized_user, StandardizedUser)
        assert standardized_user.id == mock_gitlab_users[idx].id
        assert standardized_user.login == mock_gitlab_users[idx].username
        assert standardized_user.name == mock_gitlab_users[idx].name
        assert standardized_user.url == mock_gitlab_users[idx].web_url

def test_gitlab_adapter_get_users_with_limit(gitlab_adapter: GitlabAdapter, mock_gitlab_users):
    """
    Verifies that get_users stops yielding after reaching the user-supplied limit.
    """
    org = get_org()
    gitlab_adapter.client.get_users = MagicMock(return_value=mock_gitlab_users)
    result = list(gitlab_adapter.get_users(standardized_organization=org, limit=1))

    gitlab_adapter.client.get_users.assert_called_once_with(group_id="12345")
    assert len(result) == 1
    assert result[0].id == mock_gitlab_users[0].id
    assert result[0].login == mock_gitlab_users[0].username


@pytest.mark.skip(reason="TODO")
def test_gitlab_get_commits_for_branches(gitlab_adapter: GitlabAdapter):
    with pytest.raises(NotImplementedError):
        gitlab_adapter.get_commits_for_branches(
            standardized_repo=None,
            branches=[]
        )
        
def test_gitlab_get_pr_metadata(gitlab_adapter: GitlabAdapter):
    with pytest.raises(NotImplementedError):
        gitlab_adapter.get_pr_metadata(
            standardized_repo=None,
        )

def _verify_gitlab_get_prs_helper(standardized_prs, raw_prs, redact_names_and_urls):
    for standardized_pr, raw_pr in zip(standardized_prs, raw_prs):
        assert standardized_pr.id == int(get_id_from_gid(raw_pr['id'], GitLabGidObjectMapping.MERGE_REQUEST.value))
        assert standardized_pr.additions == raw_pr['diffStatsSummary']['additions']
        assert standardized_pr.deletions == raw_pr['diffStatsSummary']['deletions']
        assert standardized_pr.changed_files == raw_pr['diffStatsSummary']['fileCount']
        assert standardized_pr.is_closed == bool(raw_pr['closedAt'])
        assert standardized_pr.is_merged == bool(raw_pr['mergedAt'])
        assert standardized_pr.created_at == parse_gitlab_date(raw_pr['createdAt'])
        assert standardized_pr.updated_at == parse_gitlab_date(raw_pr['updatedAt'])
        assert standardized_pr.merge_date == parse_gitlab_date(raw_pr['mergedAt'])
        assert standardized_pr.closed_date == parse_gitlab_date(raw_pr['closedAt'])
        assert standardized_pr.title == raw_pr['title']
        assert standardized_pr.body == raw_pr['description']
        if redact_names_and_urls:
            if raw_pr['targetBranch'] != 'master':
                assert 'redacted' in standardized_pr.base_branch
            assert 'redacted' in standardized_pr.head_branch
            assert standardized_pr.url == None
        else:
            assert standardized_pr.base_branch == raw_pr['targetBranch']
            assert standardized_pr.head_branch == raw_pr['sourceBranch']
            assert standardized_pr.url == raw_pr['webUrl']
        assert standardized_pr.author == GitlabAdapter._standardize_gitlab_user_gql(raw_pr['author'])
        assert standardized_pr.merged_by == GitlabAdapter._standardize_gitlab_user_gql(raw_pr['mergeUser'])

        # Check short-form repos for base and head repos
        assert standardized_pr.head_repo.id == get_id_from_gid(raw_pr['sourceProject']['id'], GitLabGidObjectMapping.PROJECT.value)
        if redact_names_and_urls:
            assert 'redacted' in standardized_pr.base_repo.name
            assert 'redacted' in standardized_pr.head_repo.name
            assert standardized_pr.base_repo.url == None
            assert standardized_pr.head_repo.url == None

        else:
            assert standardized_pr.base_repo.name == raw_pr['targetProject']['name']
            assert standardized_pr.base_repo.url == raw_pr['targetProject']['webUrl']
            assert standardized_pr.head_repo.name == raw_pr['sourceProject']['name']
            assert standardized_pr.head_repo.url == raw_pr['sourceProject']['webUrl']

        # Verify we built commits correctly.
        for standardized_commit, raw_commit in zip(standardized_pr.commits, raw_pr['commits']['nodes']):
            assert standardized_commit.hash == raw_commit['sha']
            assert standardized_commit.url == (raw_commit['webUrl'] if not redact_names_and_urls else None)
            assert standardized_commit.message == raw_commit['message']
            assert standardized_commit.commit_date == parse_gitlab_date(raw_commit['committedDate'])
            assert standardized_commit.author_date == parse_gitlab_date(raw_commit['authoredDate'])
            assert standardized_commit.author == GitlabAdapter._standardize_gitlab_user_gql(raw_commit['author'])
            assert standardized_commit.repo == BASE_REPOSITORY.short()
            assert standardized_commit.is_merge == bool(raw_pr['mergeCommitSha'] == raw_commit['sha'])
            if redact_names_and_urls:
                assert 'redacted' in standardized_commit.branch_name
            else:
                assert standardized_commit.branch_name == raw_pr['sourceBranch']

        # Verify we built comments correctly.
        for standardized_comment, raw_comment in zip(standardized_pr.comments, raw_pr['notes']['nodes']):
            assert standardized_comment.user == GitlabAdapter._standardize_gitlab_user_gql(raw_comment['author'])
            assert standardized_comment.body == raw_comment['body']
            assert standardized_comment.created_at == parse_gitlab_date(raw_comment['createdAt'])
            assert standardized_comment.system_generated == raw_comment['system']

        # Verify we built approvals correctly.
        for standardized_approval, raw_approval in zip(standardized_pr.approvals, raw_pr['approvedBy']['nodes']):
            standardized_approval_user = GitlabAdapter._standardize_gitlab_user_gql(raw_approval)
            assert standardized_approval.user == standardized_approval_user
            assert standardized_approval.foreign_id == standardized_approval_user.id if standardized_approval_user else ''
            assert standardized_approval.review_state == PullRequestReviewState.APPROVED.name

        # Verify we build file data correctly.
        for standardized_file, raw_file in zip(standardized_pr.files.values(), raw_pr['diffStats']):
            assert standardized_file.status == ''
            assert standardized_file.changes == raw_file['additions'] + raw_file['deletions']
            assert standardized_file.additions == raw_file['additions']
            assert standardized_file.deletions == raw_file['deletions']

def test_gitlab_get_prs(gitlab_adapter: GitlabAdapter):
    raw_prs = raw_api_responses.raw_get_pr_gql
    gitlab_adapter.config.git_redact_names_and_urls = False
    with (patch.object(GitlabClient, 'get_prs', return_value=raw_prs)):
        standardized_prs = [pr for pr in gitlab_adapter.get_prs(BASE_REPOSITORY)]
        _verify_gitlab_get_prs_helper(standardized_prs=standardized_prs, raw_prs=raw_prs, redact_names_and_urls=gitlab_adapter.config.git_redact_names_and_urls)