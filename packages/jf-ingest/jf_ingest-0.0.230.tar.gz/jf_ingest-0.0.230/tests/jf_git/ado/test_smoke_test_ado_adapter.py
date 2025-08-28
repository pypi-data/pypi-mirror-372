from contextlib import contextmanager
from unittest.mock import patch

from jf_ingest.config import IngestionConfig
from tests.jf_git.ado.utils import (
    get_adapter,
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


@contextmanager
def _spoof_all_client_functions():
    raw_prs = get_raw_prs()
    raw_iterations = get_raw_iterations()
    raw_diffs = get_raw_diffs()
    raw_change_counts = get_raw_change_counts()
    raw_commits = get_raw_commits()
    raw_threads = get_raw_threads_comments()
    raw_branches = get_raw_branches()
    raw_repos = get_raw_repos()
    raw_teams = get_raw_teams()
    raw_users = get_raw_users()
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
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_branches',
            return_value=raw_branches,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_all_repos',
            return_value=raw_repos,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_teams',
            return_value=raw_teams,
        ),
        patch(
            'jf_ingest.jf_git.clients.azure_devops.AzureDevopsClient.get_graph_users',
            return_value=raw_users,
        ),
    ):
        yield


def test_ado_smoke_test():
    adapter = get_adapter()
    ingest_config = IngestionConfig(
        jellyfish_api_token='abc',
        company_slug='',
        save_locally=False,
        upload_to_s3=False,
    )
    with _spoof_all_client_functions():
        adapter.load_and_dump_git(adapter.config, ingest_config)
