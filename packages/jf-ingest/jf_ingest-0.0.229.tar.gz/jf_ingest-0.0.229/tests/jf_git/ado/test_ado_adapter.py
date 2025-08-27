import copy
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import List
from unittest.mock import patch

from dateutil import parser

from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.adapters.azure_devops import AzureDevopsAdapter
from jf_ingest.jf_git.standardized_models import (
    StandardizedCommit,
    StandardizedFileData,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.utils import hash_filename
from tests.jf_git.ado.utils import (
    ADO_PROJECT_NAME,
    BASIC_ORG,
    BASIC_REPO,
    get_adapter,
    get_adapter_from_config,
    get_git_config,
    get_raw_branches,
    get_raw_change_counts,
    get_raw_commits,
    get_raw_diffs,
    get_raw_iterations,
    get_raw_prs,
    get_raw_repos,
    get_raw_teams,
    get_raw_threads_comments,
    get_raw_users,
)


def test_project_name_from_url():
    adapter = get_adapter()
    project_name = adapter._project_name_from_repo(BASIC_REPO)
    assert project_name == ADO_PROJECT_NAME


def test_get_organizations():
    adapter = get_adapter()
    organizations = adapter.get_organizations()

    assert len(organizations) == 1
    organization = organizations[0]

    assert BASIC_ORG == organization


def test_get_users():
    adapter = get_adapter()
    raw_users = get_raw_users()
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_graph_users',
        return_value=raw_users,
    ):
        users = list(adapter.get_users(standardized_organization=BASIC_ORG))
        raw_user_index = 0
        standard_user_index = 0
        while standard_user_index < len(users):
            raw_user = raw_users[raw_user_index]
            standard_user = users[standard_user_index]
            assert raw_user['descriptor'] == standard_user.id
            assert raw_user['principalName'] == standard_user.login
            assert raw_user['displayName'] == standard_user.name
            assert raw_user['mailAddress'] == standard_user.email
            assert raw_user['url'] == standard_user.url
            raw_user_index += 1
            standard_user_index += 1


def test_get_teams():
    # NOTE Redacting/stripping variables don't affect user ingestion at all
    adapter = get_adapter()
    raw_teams = get_raw_teams()
    raw_users = get_raw_users()
    # TODO: Also patch team members
    with (
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_teams',
            return_value=raw_teams,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_team_users',
            return_value=raw_users,
        ),
    ):
        teams: List[StandardizedTeam] = list(adapter.get_teams(standardized_organization=BASIC_ORG))

        for raw_team, standard_team in zip(raw_teams, teams):
            assert raw_team['descriptor'] == standard_team.id
            assert raw_team['descriptor'] == standard_team.slug
            assert raw_team['displayName'] == standard_team.name
            assert raw_team['description'] == standard_team.description

            members = standard_team.members
            raw_user_index = 0
            standard_user_index = 0
            while standard_user_index < len(members):
                raw_user = raw_users[raw_user_index]
                standard_user = members[standard_user_index]
                assert raw_user['descriptor'] == standard_user.id
                assert raw_user['principalName'] == standard_user.login
                assert raw_user['displayName'] == standard_user.name
                assert raw_user['mailAddress'] == standard_user.email
                assert raw_user['url'] == standard_user.url
                raw_user_index += 1
                standard_user_index += 1


def test_get_repos():
    # NOTE Redacting/stripping variables don't affect user ingestion at all
    adapter = get_adapter()
    raw_repos = get_raw_repos()
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
        return_value=raw_repos,
    ):
        standard_repos = adapter.get_repos(standardized_organization=BASIC_ORG)
        for raw_repo, standard_repo in zip(raw_repos, standard_repos):
            assert raw_repo['id'] == standard_repo.id
            assert f"{BASIC_ORG.login}/{raw_repo['name']}" == standard_repo.full_name
            assert raw_repo['webUrl'] == standard_repo.url
            assert raw_repo.get('isFork', False) == standard_repo.is_fork
            assert BASIC_ORG == standard_repo.organization
            assert (
                raw_repo['defaultBranch'].replace('refs/heads/', '')
                if 'defaultBranch' in raw_repo
                else None
            ) == standard_repo.default_branch_name
            assert None == standard_repo.default_branch_sha

def test_get_repos_with_excluded_project():
    # NOTE Redacting/stripping variables don't affect user ingestion at all
    adapter = get_adapter()
    raw_repos = get_raw_repos()
    test_git_repo_name = 'TestGit'
    fabrikam_project = f'Fabrikam-Fiber-Git'
    
    # TEST 1: Assert we get 4 repos without filtering
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
        return_value=raw_repos,
    ):
        standard_repos = list(adapter.get_repos(standardized_organization=BASIC_ORG))
        assert len(standard_repos) == 3
        assert any(repo.name == test_git_repo_name for repo in standard_repos)
        
    
    config = get_git_config()
    config.git_organizations = [BASIC_ORG.login]
    config.excluded_organizations = [f'{BASIC_ORG.login}/{fabrikam_project}']
    adapter = get_adapter_from_config(config)
    raw_repos = get_raw_repos()
    # TEST 2: Assert we get 1 repo by excluding 1 project
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
        return_value=raw_repos,
    ):
        standard_repos = list(adapter.get_repos(standardized_organization=BASIC_ORG))
        assert len(standard_repos) == 1
        repo = standard_repos[0]
        assert repo.name == 'TestGit'
    
    config = get_git_config()
    config.git_organizations = [f'{BASIC_ORG.login}/{test_git_repo_name}']
    adapter = get_adapter_from_config(config)
    raw_repos = get_raw_repos()
    # TEST 3: Assert we attempt to fetch for specific project
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
        return_value=raw_repos,
    ) as m:
        standard_repos = list(adapter.get_repos(standardized_organization=BASIC_ORG))
        m.assert_called_once_with(org_name=f'{BASIC_ORG.login}/{test_git_repo_name}')
        
    config = get_git_config()
    config.git_organizations = [f'{BASIC_ORG.login}/project_1', f'{BASIC_ORG.login}/project_2']
    adapter = get_adapter_from_config(config)
    raw_repos = get_raw_repos()
    # TEST 4: Assert we attempt to fetch for all specified projects
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
        return_value=raw_repos,
    ) as m:
        standard_repos = list(adapter.get_repos(standardized_organization=BASIC_ORG))
        for org_project in config.git_organizations:
            m.assert_any_call(org_name=org_project)
            
        assert m.call_count == len(config.git_organizations)
    

def test_get_commits_for_default_branch():
    # NOTE Redacting/stripping variables don't affect user ingestion at all
    adapter = get_adapter()
    raw_commits = get_raw_commits()
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_commits',
        return_value=raw_commits,
    ):
        standard_commits = adapter.get_commits_for_default_branch(standardized_repo=BASIC_REPO)
        for raw_commit, standard_commit in zip(raw_commits, standard_commits):
            assert standard_commit.hash == raw_commit['commitId']
            assert standard_commit.url == raw_commit['url']
            assert standard_commit.message == raw_commit['comment']
            assert standard_commit.branch_name == BASIC_REPO.default_branch_name
            assert standard_commit.commit_date == parser.parse(raw_commit['committer']['date'])
            assert standard_commit.author_date == parser.parse(raw_commit['author']['date'])
            assert type(standard_commit.author) == StandardizedUser
            assert standard_commit.author != None
            assert standard_commit.repo.id == BASIC_REPO.id
            assert standard_commit.repo.url == BASIC_REPO.url
            assert standard_commit.repo.name == BASIC_REPO.name
            assert standard_commit.is_merge == False


def test_get_branches_for_repo():
    # NOTE Redacting/stripping variables don't affect user ingestion at all
    adapter = get_adapter()
    raw_branches = get_raw_branches()

    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_branches',
        return_value=raw_branches,
    ):
        standard_branches = adapter.get_branches_for_repo(BASIC_REPO, pull_branches=True)
        for standard_branch, raw_branch in zip(standard_branches, raw_branches):
            branch_name = raw_branch['name'].replace('refs/heads/', '')
            assert standard_branch.is_default == (
                standard_branch.name == BASIC_REPO.default_branch_name
            )
            assert standard_branch.name == branch_name
            assert standard_branch.repo_id == BASIC_REPO.id
            assert standard_branch.sha == raw_branch['objectId']


def test_get_commits_for_branches():
    # NOTE This test doesn't test if we're pulling for branches at all, it's just testing
    # that we are stripping text content!
    adapter = get_adapter()
    raw_commits = get_raw_commits()
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_commits',
        return_value=raw_commits,
    ):
        standard_commits = adapter.get_commits_for_branches(
            standardized_repo=BASIC_REPO, branches=[]
        )
        for raw_commit, standard_commit in zip(raw_commits, standard_commits):
            assert standard_commit.hash == raw_commit['commitId']
            assert standard_commit.url == raw_commit['url']
            assert standard_commit.message == raw_commit['comment']
            assert standard_commit.branch_name == BASIC_REPO.default_branch_name
            assert standard_commit.commit_date == parser.parse(raw_commit['committer']['date'])
            assert standard_commit.author_date == parser.parse(raw_commit['author']['date'])
            assert type(standard_commit.author) == StandardizedUser
            assert standard_commit.author != None
            assert standard_commit.repo.id == BASIC_REPO.id
            assert standard_commit.repo.url == BASIC_REPO.url
            assert standard_commit.repo.name == BASIC_REPO.name
            assert standard_commit.is_merge == False


def test_get_pr_updated_date_only_closed():
    adapter = get_adapter()

    closed_api_prs = [datetime(2020, 1, 1), datetime(2024, 1, 1, tzinfo=timezone.utc)]
    closed_api_prs_raw = [
        {'closedDate': closed_api_pr.isoformat()} for closed_api_pr in closed_api_prs
    ]

    for closed_api_pr, closed_api_pr_raw in zip(closed_api_prs, closed_api_prs_raw):
        assert adapter.get_pr_updated_date(BASIC_REPO, closed_api_pr_raw) == closed_api_pr


def test_get_pr_updated_date_with_iterations():
    adapter = get_adapter()
    raw_iterations = get_raw_iterations()
    raw_prs = [
        {
            'pullRequestId': 0,
            'creationDate': datetime(2000, 10, 26, tzinfo=timezone.utc).isoformat(),
        },
        {
            'pullRequestId': 1,
            'creationDate': datetime(2000, 11, 26, tzinfo=timezone.utc).isoformat(),
            'closedDate': datetime(2000, 11, 26, tzinfo=timezone.utc).isoformat(),
        },
        {
            'pullRequestId': 2,
            'creationDate': datetime(2000, 11, 30, tzinfo=timezone.utc).isoformat(),
            'closedDate': datetime(2000, 11, 30, tzinfo=timezone.utc).isoformat(),
        },
    ]
    with patch(
        'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pull_request_iterations',
        return_value=raw_iterations,
    ):
        for pr in raw_prs:
            if closed_date := pr.get('closedDate'):
                closed_date = datetime.fromisoformat(closed_date)
                assert adapter.get_pr_updated_date(BASIC_REPO, pr) == closed_date
            else:
                latest_iteration_date_str = raw_iterations[-1]['updatedDate']
                latest_iteration_update = datetime.fromisoformat(latest_iteration_date_str)
                assert adapter.get_pr_updated_date(BASIC_REPO, pr) == latest_iteration_update


def test_git_provider_pr_endpoint_supports_date_filtering():
    adapter = get_adapter()
    assert adapter.git_provider_pr_endpoint_supports_date_filtering()


@contextmanager
def _get_pr_mocking_context_manager():
    raw_prs = get_raw_prs()
    raw_iterations = get_raw_iterations()
    raw_diffs = get_raw_diffs()
    raw_change_counts = get_raw_change_counts()
    raw_commits = get_raw_commits()
    raw_threads = get_raw_threads_comments()
    with (
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pull_requests',
            return_value=raw_prs,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pull_request_iterations',
            return_value=raw_iterations,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pull_request_diff',
            return_value=raw_diffs,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pull_request_changes_counts',
            return_value=raw_change_counts,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pr_commits',
            return_value=raw_commits,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_pr_comment_threads',
            return_value=raw_threads,
        ),
    ):
        yield raw_prs, raw_iterations, raw_diffs, raw_change_counts, raw_commits, raw_threads


def _test_get_prs_helper(
    pull_files_for_prs: bool,
    hash_files_for_prs: bool,
):
    adapter = get_adapter()

    with _get_pr_mocking_context_manager() as raw_values:
        raw_prs, raw_iterations, raw_diffs, raw_change_counts, raw_commits, raw_threads = raw_values
        standard_prs = adapter.get_prs(
            standardized_repo=BASIC_REPO,
            pull_files_for_pr=pull_files_for_prs,
            hash_files_for_prs=hash_files_for_prs,
        )
        for raw_pr, standard_pr in zip(raw_prs, standard_prs):
            assert standard_pr.id == raw_pr['pullRequestId']
            assert standard_pr.additions == raw_change_counts['Add']
            assert standard_pr.deletions == raw_change_counts['Delete']
            assert standard_pr.changed_files == sum(raw_change_counts.values())
            assert standard_pr.is_closed == (raw_pr['status'] != 'active')
            assert standard_pr.is_merged == (raw_pr['status'] == 'completed')
            if standard_pr.is_closed:
                assert standard_pr.closed_date == parser.parse(raw_pr['closedDate'])
                assert standard_pr.updated_at == parser.parse(raw_pr['closedDate'])
            else:
                assert standard_pr.closed_date == None
                assert standard_pr.updated_at == parser.parse(raw_iterations[-1]['updatedDate'])
            if standard_pr.is_merged:
                assert standard_pr.merged_by != None
                assert type(standard_pr.merged_by) is StandardizedUser
                assert standard_pr.merge_date == parser.parse(raw_pr['mergeDate'])
                assert standard_pr.is_closed == True
                assert standard_pr.updated_at == standard_pr.closed_date
                assert standard_pr.merge_commit != None
                assert type(standard_pr.merge_commit) is StandardizedCommit
            else:
                assert standard_pr.merge_commit == None
                assert standard_pr.merged_by == None
                assert standard_pr.merge_date == None
                assert standard_pr.updated_at == parser.parse(raw_iterations[-1]['updatedDate'])
                assert standard_pr.is_closed == False
            assert standard_pr.created_at == parser.parse(raw_pr['creationDate'])
            assert standard_pr.title == raw_pr['title']
            assert standard_pr.body == raw_pr['description']
            assert standard_pr.url == raw_pr['url']
            assert standard_pr.head_branch == raw_pr['sourceRefName'].replace('refs/heads/', '')
            assert standard_pr.base_branch == raw_pr['targetRefName'].replace('refs/heads/', '')
            assert standard_pr.base_repo == BASIC_REPO.short()
            assert standard_pr.head_repo == BASIC_REPO.short()

            assert standard_pr.author != None
            assert type(standard_pr.author) is StandardizedUser

            if pull_files_for_prs:
                files = {raw_file['item']['path']: StandardizedFileData(status=raw_file.get('changedType', ''), changes=0, additions=0, deletions=0) for raw_file in raw_diffs if not raw_file['item'].get('isFolder', False)}
                if hash_files_for_prs:
                    files = {hash_filename(file_path): file_data for file_path, file_data in files.items()}
            else:
                files = {}
            assert standard_pr.files == files
            labels = [label['name'] for label in raw_pr.get('labels', [])]
            assert standard_pr.labels == labels

            # Assert we're getting all comments
            comments = []
            for thread in raw_threads:
                comments.extend(thread['comments'])

            assert len(standard_pr.comments) == len(comments)
            assert len(standard_pr.approvals) == 4

            assert len(standard_pr.commits) == len(raw_commits)


def test_get_prs_base():
    _test_get_prs_helper(
        pull_files_for_prs=False,
        hash_files_for_prs=False,
    )


def test_get_prs_pull_files():
    _test_get_prs_helper(
        pull_files_for_prs=True,
        hash_files_for_prs=False,
    )


def test_get_prs_hash_files():
    _test_get_prs_helper(
        pull_files_for_prs=True,
        hash_files_for_prs=True,
    )
