import logging
import os
import sys
from datetime import datetime

import pytz
import urllib3
import yaml

from jf_ingest.config import (
    AzureDevopsAuthConfig,
    GitAuthConfig,
    GitConfig,
    GitLabAuthConfig,
    GitProvider,
)
from jf_ingest.constants import Constants
from jf_ingest.jf_git.adapters import load_and_push_git_to_s3
from jf_ingest.jf_jira import IngestionConfig, load_and_push_jira_to_s3
from jf_ingest.jf_jira.auth import JiraDownloadConfig, get_jira_connection
from jf_ingest.jf_jira.custom_fields import identify_custom_field_mismatches
from jf_ingest.jf_jira.downloaders import is_jql_enhanced_search_available
from jf_ingest.validation import validate_git, validate_jira

logger = logging.getLogger(__name__)

# Start of Epoch Time
_default_datetime_str = '1970-01-01'


def setup_harness_logging(logging_level: int):
    """Helper function to setting up logging in the harness"""
    logging.basicConfig(
        level=logging_level,
        format=(
            "%(asctime)s %(threadName)s %(levelname)s %(name)s %(message)s"
            if logging_level == logging.DEBUG
            else "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger(urllib3.__name__).setLevel(logging.WARNING)


def _process_jira_config(general_config_data: dict) -> JiraDownloadConfig:
    jira_config_data = general_config_data["jira_config"]
    # Translate Datetimes first
    jira_config_data["work_logs_pull_from"] = datetime.strptime(
        jira_config_data.get("work_logs_pull_from", _default_datetime_str), "%Y-%m-%d"
    )
    jira_config_data["pull_from"] = datetime.strptime(
        jira_config_data.get("pull_from", _default_datetime_str), "%Y-%m-%d"
    )
    jira_config_data["project_id_to_pull_from"] = {
        project_id: datetime.strptime(pull_from, "%Y-%m-%d")
        for project_id, pull_from in jira_config_data.get("project_id_to_pull_from", {}).items()
    }
    if not (jira_url := os.getenv("JIRA_URL")):
        raise Exception(
            f'JIRA_URL not detected as an environment variable! Is it set in your creds.env?'
        )
    jira_config_data['url'] = jira_url
    # Generate object in memory
    jira_config = JiraDownloadConfig(**jira_config_data)
    if not (jira_username := os.getenv("JIRA_USERNAME")):
        raise Exception(
            f'JIRA_USERNAME not detected as an environment variable! Is it set in your creds.env?'
        )
    if not (jira_password := os.getenv("JIRA_PASSWORD")):
        raise Exception(
            f'JIRA_PASSWORD not detected as an environment variable! Is it set in your creds.env?'
        )
    jira_config.user = jira_username
    jira_config.password = jira_password
    return jira_config


def _process_git_configs(general_config_data: dict) -> list[GitConfig]:
    git_config_data = general_config_data["git_configs"][0]
    company_slug = git_config_data['company_slug']
    # Process 'default' time for repos and commits
    git_config_data["pull_from"] = datetime.strptime(
        git_config_data.get("pull_from", _default_datetime_str),
        "%Y-%m-%d",
    ).replace(tzinfo=pytz.UTC)

    # Translate PRs
    for repo_id, date_str in git_config_data[f'repos_to_prs_last_updated'].items():
        git_config_data[f'repos_to_prs_last_updated'][repo_id] = datetime.strptime(
            date_str, "%Y-%m-%d"
        ).replace(tzinfo=pytz.UTC)

    # Create separate auth config
    git_provider = GitProvider(git_config_data['git_provider'].upper())
    if git_provider == GitProvider.GITHUB:
        auth_config = GitAuthConfig(
            company_slug=company_slug,
            token=os.getenv('GITHUB_TOKEN'),
            base_url='',
            verify=False,
            session=None,
        )
    elif git_provider == GitProvider.ADO:
        auth_config = AzureDevopsAuthConfig(
            company_slug=company_slug,
            token=os.getenv(f'GITHUB_TOKEN'),
            base_url='',
            verify=True,
            session=None,
        )
    elif git_provider == GitProvider.GITLAB:
        auth_config = GitLabAuthConfig(
            company_slug=company_slug,
            token=os.getenv(f'GITHUB_TOKEN'),
            base_url='',
            verify=True,
            session=None,
        )
    else:
        raise Exception(f'{git_provider} not recognized in harness init')
    return [GitConfig(git_auth_config=auth_config, **git_config_data)]


if __name__ == "__main__":
    """
    NOTE: This is a work in progress developer debugging tool.
    it is currently run by using the following command:
       pdm run ingest_harness [--debug]
    and it requires you to have a creds.env and a config.yml file at
    the root of this project
    """
    debug_mode = "--debug" in sys.argv
    validate_mode = "--validate" in sys.argv
    run_git_harness = '--git' in sys.argv
    run_jira_harness = '--jira' in sys.argv
    skip_custom_field_detect_and_repair = '--skip-field-repair' in sys.argv

    if not run_git_harness and not run_jira_harness:
        # If neither the git or jira arg are supplied, run validation for both
        run_git_harness = True
        run_jira_harness = True

    # Get Config data for Ingestion Config
    with open("./config.yml") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        general_config_data = yaml_data["general"]
        if not (company_slug := os.getenv('COMPANY_SLUG')):
            raise Exception(f'COMPANY_SLUG not found as an env variable. Is it set in creds.env?')
        if not (api_token := os.getenv("JELLYFISH_API_TOKEN")):
            raise Exception(f'COMPANY_SLUG not found as an env variable. Is it set in creds.env?')
        ingest_config = IngestionConfig(
            timestamp=datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
            jellyfish_api_token=api_token,
            **general_config_data,
            company_slug=company_slug,
        )
        ingest_config.local_file_path = f"{ingest_config.local_file_path}/{ingest_config.timestamp}"
        print(f'Saving data locally to {ingest_config.local_file_path}')

        # Processes Jira Info
        if run_jira_harness:
            if 'jira_config' in general_config_data:
                ingest_config.jira_config = _process_jira_config(general_config_data)
            else:
                logger.warning(
                    f'Attempted to run Jira Validation but the Jira Config was not found in the config.yml file'
                )

        # Process Git Info
        if run_git_harness:
            if 'git_configs' in general_config_data:
                ingest_config.git_configs = _process_git_configs(general_config_data)
            else:
                logger.warning(
                    f'Attempting to run Git Validation but the Git Config was not found in the config.yml file'
                )

    setup_harness_logging(logging_level=logging.DEBUG if debug_mode else logging.INFO)

    if validate_mode:
        if run_jira_harness and ingest_config.jira_config:
            validate_jira(ingest_config.jira_config)
        if run_git_harness and 'git_configs' in general_config_data:
            validate_git(ingest_config.git_configs)
    else:
        if run_jira_harness and ingest_config.jira_config:
            # NOTE: The config file stores this value as a list, when it should actually be a set.
            # This is a quick and cheap fix to re-cast this
            ingest_config.jira_config.jellyfish_issue_ids_for_redownload = set(
                ingest_config.jira_config.jellyfish_issue_ids_for_redownload
            )
            if not skip_custom_field_detect_and_repair:
                # Calculate API selection decision using the same logic as _run_load_and_push_to_s3()
                should_attempt_enhanced_search = ingest_config.jira_config.feature_flags.get(
                    Constants.JQL_ENHANCED_SEARCH_ENABLED, False
                ) and not ingest_config.jira_config.feature_flags.get(
                    Constants.FORCE_LEGACY_API, False
                )

                # Create test connection with v3 if we should attempt enhanced search
                use_jql_enhanced_search = False
                if should_attempt_enhanced_search:
                    try:
                        test_connection = get_jira_connection(
                            config=ingest_config.jira_config, use_jql_enhanced_search=True
                        )
                        use_jql_enhanced_search = is_jql_enhanced_search_available(test_connection)
                    except Exception as e:
                        logger.warning(
                            f"Failed to create v3 test connection for JQL Enhanced Search: {e}"
                        )
                        use_jql_enhanced_search = False

                api_type = "JQL Enhanced Search" if use_jql_enhanced_search else "Legacy"
                logger.info(f"Using {api_type} API for custom field detection")

                jcfv_update_payload = identify_custom_field_mismatches(
                    ingest_config=ingest_config, use_jql_enhanced_search=use_jql_enhanced_search
                )
                logger.info("Submitting list of issue IDs to repair to Jellyfish")

                # TODO: All this stuff should be moved INTO the identify_custom_field_mismatches function.
                # The identify_custom_field_mismatches should post the list of all_ids_to_redownload to Jellyfish,
                # and then Jira Download should pull that list
                missing_db_ids = [
                    jcfv.jira_issue_id for jcfv in jcfv_update_payload.missing_from_db_jcfv
                ]
                missing_jira_ids = [
                    jcfv.jira_issue_id for jcfv in jcfv_update_payload.missing_from_jira_jcfv
                ]
                missing_out_of_sync_ids = [
                    jcfv.jira_issue_id for jcfv in jcfv_update_payload.out_of_sync_jcfv
                ]

                all_ids = set(missing_db_ids + missing_jira_ids + missing_out_of_sync_ids)

                all_ids_to_redownload = set([str(id) for id in all_ids])

                ingest_config.jira_config.jellyfish_issue_ids_for_redownload.update(
                    all_ids_to_redownload
                )
                logger.info(f'----')
                logger.info(
                    f'Done detecting customfield mismatches, {len(all_ids_to_redownload)} additional IDs will be redownloaded in Jira Download.'
                )
            logger.info('Beginning Jira Download')
            logger.info(f'----')

            jira_success = load_and_push_jira_to_s3(ingest_config)
            if not jira_success:
                raise RuntimeError(
                    f'Jira Download function {load_and_push_jira_to_s3.__name__} did not return True, which indicates a failure!'
                )
        if run_git_harness:
            load_and_push_git_to_s3(ingest_config)
