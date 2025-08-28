"""Tests for jf_ingest.config module, specifically JiraDownloadConfig feature flag access patterns."""

import pytest

from jf_ingest.config import JiraDownloadConfig
from jf_ingest.constants import Constants


class TestJiraDownloadConfigFeatureFlags:
    """Test feature flag access patterns in JiraDownloadConfig following existing codebase conventions."""

    def test_jql_enhanced_search_enabled_default_false(self):
        """Test that JQL Enhanced Search feature flag defaults to False when not set."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={}
        )
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is False

    def test_jql_enhanced_search_enabled_true_when_flag_set(self):
        """Test that JQL Enhanced Search feature flag returns True when enabled."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={Constants.JQL_ENHANCED_SEARCH_ENABLED: True}
        )
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is True

    def test_jql_enhanced_search_enabled_false_when_flag_explicitly_disabled(self):
        """Test that JQL Enhanced Search feature flag returns False when explicitly disabled."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={Constants.JQL_ENHANCED_SEARCH_ENABLED: False}
        )
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is False

    def test_force_legacy_api_default_false(self):
        """Test that Force Legacy API feature flag defaults to False when not set."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={}
        )
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is False

    def test_force_legacy_api_true_when_flag_set(self):
        """Test that Force Legacy API feature flag returns True when enabled."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={Constants.FORCE_LEGACY_API: True}
        )
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is True

    def test_force_legacy_api_false_when_flag_explicitly_disabled(self):
        """Test that Force Legacy API feature flag returns False when explicitly disabled."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={Constants.FORCE_LEGACY_API: False}
        )
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is False

    def test_both_feature_flags_work_together(self):
        """Test that both feature flags can be set independently using the standard pattern."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={
                Constants.JQL_ENHANCED_SEARCH_ENABLED: True,
                Constants.FORCE_LEGACY_API: False
            }
        )
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is True
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is False

    def test_feature_flags_with_none_values(self):
        """Test that feature flags handle None values gracefully using the standard pattern."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={
                Constants.JQL_ENHANCED_SEARCH_ENABLED: None,
                Constants.FORCE_LEGACY_API: None
            }
        )
        # None values should return None, not the default, when key exists
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is None
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is None

    def test_feature_flags_with_no_feature_flags_dict(self):
        """Test that feature flag access works when feature_flags uses default empty dict."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False
        )
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is False
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is False

    def test_feature_flag_constants_match_expected_values(self):
        """Test that the constants have the expected values as specified in the task."""
        assert Constants.JQL_ENHANCED_SEARCH_ENABLED == 'makara-jql-enhanced-search-enabled-2025Q3'
        assert Constants.FORCE_LEGACY_API == 'makara-force-legacy-api-2025Q3'

    def test_feature_flags_follow_existing_pattern(self):
        """Test that the new feature flags follow the same pattern as existing ones."""
        config = JiraDownloadConfig(
            company_slug='test',
            url='https://test.atlassian.net',
            gdpr_active=False,
            feature_flags={
                Constants.JQL_ENHANCED_SEARCH_ENABLED: True,
                Constants.FORCE_LEGACY_API: False,
                Constants.PULL_SPRINTS_BY_ID: True,  # Existing feature flag for comparison
            }
        )
        
        # Test that all feature flags use the same access pattern
        assert config.feature_flags.get(Constants.JQL_ENHANCED_SEARCH_ENABLED, False) is True
        assert config.feature_flags.get(Constants.FORCE_LEGACY_API, False) is False
        assert config.feature_flags.get(Constants.PULL_SPRINTS_BY_ID, False) is True