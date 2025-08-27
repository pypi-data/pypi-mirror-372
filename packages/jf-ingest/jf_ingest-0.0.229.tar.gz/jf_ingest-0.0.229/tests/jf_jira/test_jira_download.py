from jf_ingest.config import IngestionConfig, JiraDownloadConfig
from jf_ingest.constants import Constants
from jf_ingest.jf_jira import load_issues_in_batches
from tests.test_file_operations import TestIngestIOHelper
from unittest.mock import patch

SPOOF_INGEST_CONFIG = IngestionConfig(company_slug='Test', jellyfish_api_token='', jira_config=JiraDownloadConfig('', '', False))

def get_ingest_io_helper():
    test_ingest_io_helper = TestIngestIOHelper()
    test_ingest_io_helper.setup_method()
    return test_ingest_io_helper.ingest_io_helper
    

def test_load_issues_in_batches_base_line():
    issues = [
        {'id': '1', 'key': 'issue_1', 'fields': {}},
        {'id': '2', 'key': 'issue_2', 'fields': {}},
        {'id': '3', 'key': 'issue_3', 'fields': {}},
        {'id': '4', 'key': 'issue_4', 'fields': {}},
    ]
    ingest_io_helper = get_ingest_io_helper()
    ingest_config = SPOOF_INGEST_CONFIG
    def _generate_issues():
        for issue in issues:
            yield issue
            
    issues_generator = _generate_issues()
    issue_download_info = load_issues_in_batches(
        issues_to_download=issues_generator,
        ingest_io_helper=ingest_io_helper,
        ingest_config=ingest_config,
        jira_config=ingest_config.jira_config,
        batch_number_start=0
    )
    
    for issue in issues:
        assert issue['id'] in issue_download_info.downloaded_ids
        
    assert issue_download_info.issue_ids_too_large_to_upload == set()
    assert issue_download_info.total_batches == 1
    assert issue_download_info.discovered_parent_ids == set()

def test_load_issues_in_batches_filter_out_issue_size():
    JIRA_ISSUE_SIZE_LIMIT = 10000
    issues = [
        {'id': '1', 'key': 'issue_1', 'fields': {}},
        {'id': '2', 'key': 'issue_2', 'fields': {}},
        {'id': '3', 'key': 'issue_3', 'fields': {}},
        {'id': '4', 'key': 'issue_4', 'fields': {}},
        {'id': '5', 'key': 'JUMBO_ISSUE', 'fields': {}, 'changelogs': ['a' for x in range(0, JIRA_ISSUE_SIZE_LIMIT)]}
    ]
    ingest_io_helper = get_ingest_io_helper()
    ingest_config = SPOOF_INGEST_CONFIG
    def _generate_issues():
        for issue in issues:
            yield issue
    
    with patch('jf_ingest.constants.Constants.JIRA_ISSUE_SIZE_LIMIT', new=JIRA_ISSUE_SIZE_LIMIT):
        issues_generator = _generate_issues()
        issue_download_info = load_issues_in_batches(
            issues_to_download=issues_generator,
            ingest_io_helper=ingest_io_helper,
            ingest_config=ingest_config,
            jira_config=ingest_config.jira_config,
            batch_number_start=0
        )
        
        assert len(issue_download_info.downloaded_ids) == 4
        assert '1' in issue_download_info.downloaded_ids
        assert '2' in issue_download_info.downloaded_ids
        assert '3' in issue_download_info.downloaded_ids
        assert '4' in issue_download_info.downloaded_ids
        assert '5' not in issue_download_info.downloaded_ids
        assert '5' in issue_download_info.issue_ids_too_large_to_upload


def test_load_issues_in_batches_with_parents():
    issues = [
        {'id': '1', 'key': 'issue_1', 'fields': {}},
        {'id': '2', 'key': 'issue_2', 'fields': {}},
        {'id': '3', 'key': 'issue_3', 'fields': {}},
        {'id': '4', 'key': 'issue_4', 'fields': {'parent': {'id': '5'}}},
        {'id': '5', 'key': 'issue_5', 'fields': {'parent': {'id': '6'}}}
    ]
    ingest_io_helper = get_ingest_io_helper()
    ingest_config = SPOOF_INGEST_CONFIG
    def _generate_issues():
        for issue in issues:
            yield issue

    issues_generator = _generate_issues()
    issue_download_info = load_issues_in_batches(
        issues_to_download=issues_generator,
        ingest_io_helper=ingest_io_helper,
        ingest_config=ingest_config,
        jira_config=ingest_config.jira_config,
        batch_number_start=0
    )
    
    assert len(issue_download_info.downloaded_ids) == len(issues)
    assert '1' in issue_download_info.downloaded_ids
    assert '2' in issue_download_info.downloaded_ids
    assert '3' in issue_download_info.downloaded_ids
    assert '4' in issue_download_info.downloaded_ids
    assert '5' in issue_download_info.downloaded_ids
    assert '5' in issue_download_info.discovered_parent_ids
    assert '6' in issue_download_info.discovered_parent_ids
    assert '6' not in issue_download_info.downloaded_ids