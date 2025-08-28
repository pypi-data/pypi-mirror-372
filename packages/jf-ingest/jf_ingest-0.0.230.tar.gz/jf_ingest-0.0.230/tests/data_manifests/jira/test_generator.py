import unittest
from unittest.mock import MagicMock, Mock

from jf_ingest.config import JiraDownloadConfig
from jf_ingest.data_manifests.jira.generator import (
    ManifestAdapter,
    generate_project_manifest,
    process_global_jira_data,
)


class TestGenerator(unittest.TestCase):
    def test_generate_project_manifest(self):
        # Arrange
        mock_create_jira_project_manifest = Mock()
        mock_reset_current_tenant = Mock()
        mock_manifest_adapter = MagicMock(spec=ManifestAdapter)
        mock_manifest_adapter.config = MagicMock(spec=JiraDownloadConfig)
        mock_manifest_adapter.manifest_source = 'test_source'
        mock_manifest_adapter.company_slug = 'test_company'
        mock_manifest_adapter.excluded_project_keys = []
        mock_manifest_adapter.get_issues_count_for_project.return_value = 10
        mock_manifest_adapter.get_project_versions_count_for_project.return_value = 5
        mock_manifest_adapter.get_last_updated_for_project.return_value = '2023-12-05'
        mock_manifest_adapter.project_keys_to_classification_type = {
            'test_project': 'test_classification'
        }
        mock_manifest_adapter.test_basic_auth_for_project.return_value = True

        project_data_dict = {'key': 'test_project', 'id': '1'}
        classifications_name_lookup = {'test_classification': 'Test Classification'}

        # Act
        result = generate_project_manifest(
            manifest_adapter=mock_manifest_adapter,
            project_data_dict=project_data_dict,
            classifications_name_lookup=classifications_name_lookup,
            create_jira_project_manifest=mock_create_jira_project_manifest,
            reset_current_tenant=mock_reset_current_tenant,
        )

        # Assert
        mock_create_jira_project_manifest.assert_called_once_with(
            company='test_company',
            data_source='test_source',
            project_id='1',
            project_key='test_project',
            issues_count=10,
            version_count=5,
            excluded=False,
            pull_from=mock_manifest_adapter.config.pull_from,
            last_issue_updated_date='2023-12-05',
            classification='test_classification',
            classification_str='Test Classification',
        )
        mock_reset_current_tenant.assert_called_once()
        self.assertEqual(result, mock_create_jira_project_manifest.return_value)

    def test_process_global_jira_data(self):
        # Arrange
        mock_create_jira_data_manifest = Mock()
        mock_reset_current_tenant = Mock()
        mock_manifest_adapter = MagicMock(spec=ManifestAdapter)
        mock_manifest_adapter.config = MagicMock(spec=JiraDownloadConfig)
        mock_manifest_adapter.company_slug = 'test_company'
        mock_manifest_adapter.manifest_source = 'test_source'
        mock_manifest_adapter.config.pull_from = '2023-12-05'
        mock_manifest_adapter.get_users_count.return_value = 100
        mock_manifest_adapter.get_fields_count.return_value = 50
        mock_manifest_adapter.get_resolutions_count.return_value = 10
        mock_manifest_adapter.get_issue_types_count.return_value = 20
        mock_manifest_adapter.get_issue_link_types_count.return_value = 30
        mock_manifest_adapter.get_priorities_count.return_value = 40
        mock_manifest_adapter.get_project_data_dicts.return_value = [
            {'key': 'test_project', 'id': '1'}
        ]
        mock_manifest_adapter.get_boards_count.return_value = 60
        mock_manifest_adapter.get_project_versions_count.return_value = 70
        mock_manifest_adapter.get_issues_count.return_value = 80

        # Act
        result = process_global_jira_data(
            manifest_adapter=mock_manifest_adapter,
            create_jira_data_manifest=mock_create_jira_data_manifest,
            reset_current_tenant=mock_reset_current_tenant,
        )

        # Assert
        mock_create_jira_data_manifest.assert_called_once_with(
            company='test_company',
            data_source='test_source',
            pull_from='2023-12-05',
            users_count=100,
            fields_count=50,
            resolutions_count=10,
            issue_types_count=20,
            issue_link_types_count=30,
            priorities_count=40,
            projects_count=1,
            boards_count=60,
            project_versions_count=70,
            issues_count=80,
            project_manifests=[],
            encountered_errors_for_projects={},
        )
        mock_reset_current_tenant.assert_called_once()
        self.assertEqual(result, mock_create_jira_data_manifest.return_value)
