import json
import logging
from dataclasses import asdict
from datetime import datetime
from enum import Enum
from typing import Generator, Optional

from jira import JIRA

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import (
    IngestionConfig,
    IngestionType,
    IssueDownloadingResult,
    JiraAuthMethod,
    JiraDownloadConfig,
    UserMetadata,
)
from jf_ingest.constants import Constants
from jf_ingest.events.models import IngestType, JiraIngestEvent
from jf_ingest.file_operations import IngestIOHelper, SubDirectory
from jf_ingest.jf_jira.auth import get_jira_connection
from jf_ingest.jf_jira.downloaders import (
    download_boards_and_sprints,
    download_fields,
    download_issuelinktypes,
    download_issuetypes,
    download_priorities,
    download_projects_and_versions_and_components,
    download_resolutions,
    download_statuses,
    download_users,
    download_users_by_urls,
    download_worklogs,
    get_issue_ids_for_rekeys_and_deletes,
    get_jira_search_batch_size,
    is_jql_enhanced_search_available,
    pull_all_jira_issues_by_date,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.jf_jira.exceptions import AtlassianConnectException
from jf_ingest.jf_jira.utils import (
    JiraFieldIdentifier,
    expand_and_normalize_jira_fields,
    get_unique_users_from_issue,
    get_user_key,
)
from jf_ingest.telemetry import add_telemetry_fields, jelly_trace, record_span
from jf_ingest.utils import (
    batch_iterable_by_bytes_size,
    get_jellyfish_company_slug,
    get_object_bytes_size,
    init_jf_ingest_run,
)

logger = logging.getLogger(__name__)


def _generate_jira_event(event_name: str) -> JiraIngestEvent:
    return JiraIngestEvent(
        company_slug=get_jellyfish_company_slug(),
        event_name=event_name,
        ingest_type=IngestType.JIRA,
    )


class JiraObject(Enum):
    JiraFields = "jira_fields"
    JiraProjectsAndVersions = "jira_projects_and_versions"
    JiraUsers = "jira_users"
    JiraResolutions = "jira_resolutions"
    JiraIssueTypes = "jira_issuetypes"
    JiraLinkTypes = "jira_linktypes"
    JiraPriorities = "jira_priorities"
    JiraBoards = "jira_boards"
    JiraSprints = "jira_sprints"
    JiraBoardSprintLinks = "jira_board_sprint_links"
    JiraIssues = "jira_issues"
    JiraIssuesIdsDownloaded = "jira_issue_ids_downloaded"
    JiraIssuesIdsSkipped = "jira_issue_ids_skipped"
    JiraIssuesIdsDeleted = "jira_issue_ids_deleted"
    JiraWorklogs = "jira_worklogs"
    JiraStatuses = "jira_statuses"
    JiraDownloadMetadata = "jira_download_metadata"


@jelly_trace()
def load_issues_in_batches(
    issues_to_download: Generator[dict, None, None],
    ingest_io_helper: IngestIOHelper,
    ingest_config: IngestionConfig,
    jira_config: JiraDownloadConfig,
    batch_number_start: int = 0,
) -> IssueDownloadingResult:
    """given a generator object for issues to download; save them to disk in batches according to maximum size

    Args:
        issues_to_download: Generator object for issues to download
        ingest_io_helper: IngestIOHelper object for doing file operations
        ingest_config (IngestionConfig): A dataclass that holds several different configuration args for this task
        batch_number_start: starting index for the batch number (jira_issuesN.json). Used if you call this function multiple times

    Return:
        IssueDownloadingResult: A dataclass that holds the results of the download;
            - the ids for jira issues retrieved,
            - jira_ids for parents of those retrieved issues,
            - and the total number of batches it took
    """
    total_issue_batches = 0
    all_downloaded_issue_ids = set()
    collected_parent_ids = set()
    issues_ids_too_large_to_download = set()
    unique_users_across_all_issues = set()

    def _filter_out_large_issues(
        issues_generator: Generator[dict, None, None]
    ) -> Generator[dict, None, None]:
        """When processing issues we should not process any issue that's larger than 255 MB in it's string form.
        This is a hard limit we have on issue insertion logic.
        """
        for issue in issues_generator:
            if get_object_bytes_size(json.dumps(issue)) >= Constants.JIRA_ISSUE_SIZE_LIMIT:
                issues_ids_too_large_to_download.add(issue['id'])
                continue
            yield issue

    def _extract_unique_users_within_issues(
        issues_generator: Generator[dict, None, None]
    ) -> Generator[dict, None, None]:
        for issue in issues_generator:
            unique_users_across_all_issues.update(
                get_unique_users_from_issue(issue, gdpr_active=jira_config.gdpr_active)
            )
            yield issue

    issues_to_download = _filter_out_large_issues(issues_generator=issues_to_download)
    if jira_config.feature_flags.get(Constants.CHECK_ISSUES_FOR_EXTRA_USERS_AND_PULL):
        issues_to_download = _extract_unique_users_within_issues(
            issues_generator=issues_to_download
        )
    for batch_number, batch_issues in enumerate(
        batch_iterable_by_bytes_size(
            issues_to_download, batch_byte_size=Constants.JIRA_ISSUES_UNCOMPRESSED_FILE_SIZE
        ),
        start=batch_number_start,
    ):
        logging_helper.send_to_agent_log_file(
            f'Saving {len(batch_issues)} issues as batch number {batch_number}', level=logging.DEBUG
        )
        all_downloaded_issue_ids.update(set(issue['id'] for issue in batch_issues))
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraIssues.value,
            subdirectory=SubDirectory.JIRA,
            json_data=batch_issues,
            batch_number=batch_number,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )
        total_issue_batches += 1

        # we need to download parents of issues we just fetched
        collected_parent_ids.update(
            set(
                issue['fields']['parent']['id']
                for issue in batch_issues
                if 'parent' in issue['fields'].keys()
            )
        )

    logger.info(
        f"Successfully saved {len(all_downloaded_issue_ids)} Jira Issues in "
        f"{total_issue_batches} separate batches, with each batch limited to "
        f"{round(Constants.JIRA_ISSUES_UNCOMPRESSED_FILE_SIZE / Constants.MB_SIZE_IN_BYTES)}MB per batch"
    )

    return IssueDownloadingResult(
        discovered_parent_ids=collected_parent_ids,
        issue_ids_too_large_to_upload=issues_ids_too_large_to_download,
        downloaded_ids=all_downloaded_issue_ids,
        total_batches=total_issue_batches,
        users_found=unique_users_across_all_issues,
    )


@jelly_trace()
def pull_issues_wrapper(
    jira_connect_or_fallback_connection: JIRA,
    jira_config: JiraDownloadConfig,
    projects_and_versions: list[dict],
    include_fields: list[JiraFieldIdentifier],
    exclude_fields: list[JiraFieldIdentifier],
    jira_issues_batch_size: int,
    ingest_io_helper: IngestIOHelper,
    ingest_config: IngestionConfig,
    use_jql_enhanced_search: bool = False,
) -> tuple[set[str], set[str], set[UserMetadata]]:
    """Pulls issues using the "new" sync path, based on our ability to pull 10,000 jira issue IDs at one time
        as long as you only ask for `id` and `key` in the returned fields. Because we get no more fields we detect
        deletes as the absence of an issue on remote which we have local, and key changes as id match key mismatch
    Args:
        jira_connect_or_fallback_connection: either the basic connection or the special atlassian connect keys
        jira_config: jira config for jf_ingest from JF
        projects_and_versions: list of projects and versions to pull issues from
        jira_issues_batch_size: batch size to use for actually downloading issues (much lower than the 10k for IDs)
        ingest_io_helper: IngestIOHelper object for doing file operations
        ingest_config: full jf_ingest config
        use_jql_enhanced_search: whether to use JQL Enhanced Search API (/search/jql) or legacy API (/search)

    Returns:
        tuple[set[str], set[str], set[UserMetadata]]: returns a tuple of three sets:
            The first set is all the Jira Issue IDs that we downloaded
            The second set is all the Jira IDs that have been deleted
            The third set is all the unique user objects across every issue
    """

    logging_helper.send_to_agent_log_file("Running 10k batched sync path")
    logger.info(
        f"Using {jira_issues_batch_size} as batch size for issue downloads. Full Redownload is {jira_config.full_redownload}"
    )
    issue_ids_not_uploaded: set[str] = set()
    ###########################################################################
    #
    # STEP ONE: Crawl across all projects to pull all Issue ID and Keys
    # to detect potential deletions, rekeys, or creations
    #
    ###########################################################################
    with record_span('pull_jira_issues_crawl'):
        issue_list_diff = get_issue_ids_for_rekeys_and_deletes(
            jira_connection=jira_connect_or_fallback_connection,
            jellyfish_issue_metadata=jira_config.jellyfish_issue_metadata,
            project_key_to_id={
                proj["key"]: proj["id"]
                for proj in projects_and_versions
                if proj["key"] not in jira_config.exclude_projects
            },
            pull_from=jira_config.pull_from,
            jql_filter=jira_config.issue_jql_filter,
            use_jql_enhanced_search=use_jql_enhanced_search,
        )
        ids_to_delete = issue_list_diff.ids_to_delete
        ids_to_download = issue_list_diff.ids_to_download

    ###########################################################################
    #
    # STEP TWO [Optional]: Pull issues by their updated date
    #
    ###########################################################################
    issues_by_updated_date_results: IssueDownloadingResult = IssueDownloadingResult(
        downloaded_ids=set(),
        issue_ids_too_large_to_upload=set(),
        discovered_parent_ids=set(),
        total_batches=0,
        users_found=set(),
    )
    if jira_config.pull_issues_by_date:
        project_id_to_pull_from: dict[str, datetime] = {
            str(proj["id"]): (
                jira_config.project_id_to_pull_from.get(str(proj["id"]), jira_config.pull_from)
                if not jira_config.full_redownload and jira_config.project_id_to_pull_from
                else jira_config.pull_from
            )
            for proj in projects_and_versions
            if proj["key"] not in jira_config.exclude_projects
        }
        logger.info(
            f'Attempting to pull all the full Jira Issues that have been updated since our last Jira Download across {len(project_id_to_pull_from)} projects.'
        )
        issues_by_updated_date_generator = pull_all_jira_issues_by_date(
            jira_connection=jira_connect_or_fallback_connection,
            project_key_to_pull_from=project_id_to_pull_from,
            num_parallel_threads=jira_config.issue_download_concurrent_threads,
            batch_size=jira_issues_batch_size,
            jql_project_batch_size=50,
            jql_filter=jira_config.issue_jql_filter,
            expand_fields=["changelog"],
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            use_jql_enhanced_search=use_jql_enhanced_search,
        )
        with record_span('pull_jira_issues_by_date'):
            issues_by_updated_date_results = load_issues_in_batches(
                issues_by_updated_date_generator,
                ingest_io_helper,
                ingest_config,
                ingest_config.jira_config,
            )
            issue_ids_not_uploaded.update(
                issues_by_updated_date_results.issue_ids_too_large_to_upload
            )
            logger.info(
                f'We have downloaded {len(issues_by_updated_date_results.downloaded_ids)} issues that have been updated or created since our last pull across {len(project_id_to_pull_from)} projects.'
            )

    file_batch_cursor = issues_by_updated_date_results.total_batches
    ###########################################################################
    #
    # Step 3: Download the full Jira Issues for potentially rekeys and/or missing issues.
    # Also redownload issues that have been marked for redownload in our system
    #
    ###########################################################################
    # Extend this list with issues that need to be redownloaded for Jellyfish reasons
    ids_to_download.update(jira_config.jellyfish_issue_ids_for_redownload)
    # Next, exclude any IDs that we have just done a download for, via the updated date
    ids_to_download = ids_to_download.difference(issues_by_updated_date_results.downloaded_ids)
    logging_helper.send_to_agent_log_file(
        f'We need to download an additional {len(ids_to_download)} issues because they have been rekeyed or marked for redownload by Jellyfish'
    )

    # Finally, we have a "shopping list" of IDs to download
    issues_by_ids_generator = pull_jira_issues_by_jira_ids(
        jira_connection=jira_connect_or_fallback_connection,
        jira_ids=ids_to_download,
        num_parallel_threads=jira_config.issue_download_concurrent_threads,
        batch_size=jira_issues_batch_size,
        expand_fields=["changelog"],
        include_fields=include_fields,
        exclude_fields=exclude_fields,
        use_jql_enhanced_search=use_jql_enhanced_search,
    )
    with record_span('pull_jira_issues_by_ids'):
        issues_by_ids_results: IssueDownloadingResult = load_issues_in_batches(
            issues_by_ids_generator,
            ingest_io_helper,
            ingest_config,
            ingest_config.jira_config,
            batch_number_start=file_batch_cursor,
        )
        file_batch_cursor += issues_by_ids_results.total_batches
        issue_ids_not_uploaded.update(issues_by_ids_results.issue_ids_too_large_to_upload)
    # Now, combine all issue IDs that we've downloaded
    all_downloaded_ids: set[str] = set()
    all_downloaded_ids.update(issues_by_updated_date_results.downloaded_ids)
    all_downloaded_ids.update(issues_by_ids_results.downloaded_ids)

    # Then, combine the parents of the issues we downloaded by update date, and issues we downloaded by ID
    all_discovered_parent_ids: set[str] = set()
    all_discovered_parent_ids.update(issues_by_updated_date_results.discovered_parent_ids)
    all_discovered_parent_ids.update(issues_by_ids_results.discovered_parent_ids)

    # Now, find unique parents that we have NOT downloaded and that we need to
    existing_ids = set([jimd.id for jimd in jira_config.jellyfish_issue_metadata])
    all_known_ids = existing_ids.union(all_downloaded_ids)
    to_be_downloaded_parent_ids = all_discovered_parent_ids.difference(all_known_ids)

    # Track all unique users across all issues we're downloading
    users_found_across_all_issues: set[UserMetadata] = set()
    users_found_across_all_issues.update(issues_by_updated_date_results.users_found)
    users_found_across_all_issues.update(issues_by_ids_results.users_found)

    ###########################################################################
    #
    # STEP FOUR: fetch parents
    # NOTE: For the general Jellyfish use case, we only need to go "one level deep" on parents,
    # i.e. pull the set of missing parents but NOT the parents of those parents (the "grandparents").
    # There is an optional feature, however, that will allow us to pull the parents of parents of parents
    # until we've pulled all parents. This is NOT the general use case, and will likely add a lot of computation
    # time to this function, so we advise you only use it in very specific use cases
    #
    ###########################################################################
    with record_span('pull_jira_issues_parents'):
        depth_level = 1
        while to_be_downloaded_parent_ids:
            logging_helper.send_to_agent_log_file(
                f'Attempting to pull more parents ({len(to_be_downloaded_parent_ids)} detected parents to pull). Some of them are {sorted(list(to_be_downloaded_parent_ids))[:30]} Depth level: {depth_level}. Any parents before {jira_config.pull_from} will not be downloaded'
            )
            # Finally, we have a "shopping list" of IDs to download
            issues_by_ids_generator = pull_jira_issues_by_jira_ids(
                jira_connection=jira_connect_or_fallback_connection,
                jira_ids=to_be_downloaded_parent_ids,
                num_parallel_threads=jira_config.issue_download_concurrent_threads,
                batch_size=jira_issues_batch_size,
                expand_fields=["changelog"],
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                pull_from=jira_config.pull_from,  # NOTE: We never pull any parents that were last updated before our pull from date! Jira Load WILL NOT load these
                use_jql_enhanced_search=use_jql_enhanced_search,
            )
            with record_span('write_jira_parent_issues_batch_to_local_or_s3'):
                parents_batch_result: IssueDownloadingResult = load_issues_in_batches(
                    issues_to_download=issues_by_ids_generator,
                    ingest_io_helper=ingest_io_helper,
                    ingest_config=ingest_config,
                    jira_config=ingest_config.jira_config,
                    batch_number_start=file_batch_cursor,
                )
                issue_ids_not_uploaded.update(parents_batch_result.issue_ids_too_large_to_upload)

            all_known_ids.update(parents_batch_result.downloaded_ids)
            all_downloaded_ids.update(parents_batch_result.downloaded_ids)
            users_found_across_all_issues.update(parents_batch_result.users_found)
            more_parent_ids = parents_batch_result.discovered_parent_ids - all_known_ids

            if jira_config.recursively_download_parents:
                # TODO: We could probably reduce the numbers of files we upload by grouping
                # all extra parents in joined files, but I don't think it's a big deal to upload
                # a large number of small files
                file_batch_cursor += parents_batch_result.total_batches
                to_be_downloaded_parent_ids = more_parent_ids
                depth_level += 1
            else:
                logging_helper.send_to_agent_log_file(
                    f'recursively_download_parents is set to {jira_config.recursively_download_parents}. Exiting execution'
                )
                break

    # Write Issue IDs that we've downloaded
    ingest_io_helper.write_json_to_local_or_s3(
        object_name=JiraObject.JiraIssuesIdsDownloaded.value,
        json_data=[int(issue_id) for issue_id in all_downloaded_ids],
        subdirectory=SubDirectory.JIRA,
        save_locally=ingest_config.save_locally,
        upload_to_s3=ingest_config.upload_to_s3,
    )

    # Write Issue IDs that we skipped uploading
    ingest_io_helper.write_json_to_local_or_s3(
        object_name=JiraObject.JiraIssuesIdsSkipped.value,
        json_data={'skipped_issue_ids': [int(issue_id) for issue_id in issue_ids_not_uploaded]},
        subdirectory=SubDirectory.JIRA,
        save_locally=ingest_config.save_locally,
        upload_to_s3=ingest_config.upload_to_s3,
    )

    add_telemetry_fields({'jira_downloaded_issue_count': len(all_downloaded_ids)})
    add_telemetry_fields(
        {
            'users_found_across_all_issues': len(users_found_across_all_issues),
            # Also log what users are in our DB, to make more information available
            # in our telemetry data
            'users_in_jellyfish_db': len(jira_config.user_keys_in_jellyfish),
        }
    )
    return all_downloaded_ids, ids_to_delete, users_found_across_all_issues


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def load_and_push_jira_to_s3(ingest_config: IngestionConfig) -> bool:
    """Loads data from JIRA, Dumps it to disk, and then uploads that data to S3

    All configuration for this object is done via the JIRAIngestionConfig object

    Args:
        ingest_config (IngestionConfig): A dataclass that holds several different configuration args for this task

    Returns:
        bool: Returns True on Success
    """
    init_jf_ingest_run(ingestion_config=ingest_config)
    company_slug = ingest_config.company_slug
    add_telemetry_fields({'company_slug': company_slug})
    return _run_load_and_push_to_s3(ingest_config=ingest_config)


def _run_load_and_push_to_s3(ingest_config: IngestionConfig) -> bool:
    """Inner function for load_and_push_jira_to_s3

    Args:
        ingest_config (IngestionConfig): A dataclass that holds several different configuration args for this task

    Returns:
        bool: Returns True on Success
    """
    logger.info('Beginning load_and_push_jira_to_s3')
    if not ingest_config.save_locally and not ingest_config.upload_to_s3:
        logger.error(
            f'Configuration error! Ingestion configuration must have either save_locally or upload_to_s3 set to True!'
        )
        raise Exception(
            'Save Locally and Upload to S3 are both set to False! Set one to true or no data will be saved!'
        )

    if not (jira_config := ingest_config.jira_config):
        raise Exception(
            f'load_and_push_to_s3 (Jira Download) was provided without a valid Jira Config!'
        )

    if jira_config.skip_issues and jira_config.only_issues:
        raise Exception(
            'skip_issues and only_issues have both been set to True! This is an invalid JF Ingest object'
        )

    logging_helper.send_to_agent_log_file(f"Feature flags: {jira_config.feature_flags}")

    logger.info("Using local version of ingest")

    #######################################################################
    # SET UP JIRA CONNECTIONS (Basic and Potentially Atlassian Connect)
    # First create test connection with v3 to check JQL Enhanced Search availability
    #######################################################################

    # Calculate API selection decision first
    should_attempt_enhanced_search = jira_config.feature_flags.get(
        Constants.JQL_ENHANCED_SEARCH_ENABLED, False
    ) and not jira_config.feature_flags.get(Constants.FORCE_LEGACY_API, False)

    # Create test connection with v3 if we should attempt enhanced search
    use_jql_enhanced_search = False
    if should_attempt_enhanced_search:
        try:
            test_connection = get_jira_connection(
                config=jira_config,
                auth_method=JiraAuthMethod.BasicAuth,
                use_jql_enhanced_search=True,
            )
            use_jql_enhanced_search = is_jql_enhanced_search_available(test_connection)
        except Exception as e:
            logger.warning(f"Failed to create v3 test connection for JQL Enhanced Search: {e}")
            use_jql_enhanced_search = False

    # Create final connections with appropriate API version
    jira_basic_connection = get_jira_connection(
        config=jira_config,
        auth_method=JiraAuthMethod.BasicAuth,
        use_jql_enhanced_search=use_jql_enhanced_search,
    )

    jira_atlas_connect_connection = (
        get_jira_connection(
            config=jira_config,
            auth_method=JiraAuthMethod.AtlassianConnect,
            use_jql_enhanced_search=use_jql_enhanced_search,
        )
        if JiraAuthMethod.AtlassianConnect in jira_config.available_auth_methods
        else None
    )
    # There is an ongoing effort to cut all things over to Atlassian Connect only,
    # but it is a piecewise migration for now.
    # OJ-29745
    jira_connect_or_fallback_connection = jira_basic_connection
    using_connect_as_primary_auth = False

    if jira_config.feature_flags.get("lusca-auth-always-use-connect-for-atlassian-apis-Q423"):
        logging_helper.send_to_agent_log_file("Will use connect for most API calls")

        if not isinstance(jira_atlas_connect_connection, JIRA):
            raise AtlassianConnectException(
                'Atlassian Connect Connection is not a JIRA object, unable to proceed'
            )

        jira_connect_or_fallback_connection = jira_atlas_connect_connection
        using_connect_as_primary_auth = True
    else:
        logging_helper.send_to_agent_log_file("Will use basic auth for most API calls")

    #######################################################################
    # Init IO Helper
    #######################################################################
    ingest_io_helper = IngestIOHelper(ingest_config=ingest_config)

    S3_OR_JELLYFISH_LOG_STATEMENT = (
        's3' if ingest_config.ingest_type == IngestionType.DIRECT_CONNECT else 'jellyfish'
    )
    if ingest_config.save_locally:
        logger.info(f"Data will be saved locally to: {ingest_io_helper.local_file_path}")
    else:
        logger.info("Data will not be saved locally")
    if ingest_config.upload_to_s3:
        logger.info(f"Data will be submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")
    else:
        logger.info(f"Data will NOT be submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")

    ########################################################################
    # Normalize Jira Config to the Timezone that this Jira Instance exists
    # within
    ########################################################################
    instance_metadata = jira_connect_or_fallback_connection.myself()
    timezone_locale = instance_metadata.get('timeZone', '')
    logger.info(
        f'Jira Instance Timezone Locale detected as: {timezone_locale}. Datetimes will be normalized to this timezone locale'
    )
    try:
        jira_config.normalize_datetimes_to_timezone_locale(timezone_locale)
    except Exception as e:
        # No error should get raised, but just in case
        logger.error(
            f'Failed to normalize datetimes to timezone locale: {timezone_locale}. Error: {e}'
        )

    #######################################################################
    # Jira Projects
    #######################################################################
    projects_and_versions = download_projects_and_versions_and_components(
        jira_connection=jira_connect_or_fallback_connection,
        is_agent_run=ingest_config.ingest_type == IngestionType.AGENT,
        jellyfish_project_ids_to_keys=jira_config.jellyfish_project_ids_to_keys,
        jellyfish_issue_metadata=jira_config.jellyfish_issue_metadata,
        include_projects=jira_config.include_projects,
        exclude_projects=jira_config.exclude_projects,
        include_categories=jira_config.include_project_categories,
        exclude_categories=jira_config.exclude_project_categories,
    )

    project_ids = {proj["id"] for proj in projects_and_versions}
    ingest_io_helper.write_json_to_local_or_s3(
        object_name=JiraObject.JiraProjectsAndVersions.value,
        json_data=projects_and_versions,
        subdirectory=SubDirectory.JIRA,
        save_locally=ingest_config.save_locally,
        upload_to_s3=ingest_config.upload_to_s3,
    )
    #######################################################################
    # Jira Fields
    # NOTE: Here we need to download the fields from the fields endpoint
    # and then filter out fields based on the include/exclude list.
    # The tricky part here is that it's possible for customers to provide
    # us either a fields Unique Key (something like customfield_10008), or
    # the fields human readable name (something like "Sprint"). We must
    # support BOTH use cases!
    # To do so, grab all fields data from the API endpoint. Then, expand
    # and normalize the field exclude/include lists to contain both the
    # ID and the name. THEN filter out fields by their ID
    # Once fields have been normalized and expanded we must overwrite
    # the jira_config object to have the expanded list. That way we can
    # pass both the IDs and Keys to our issue downloading logic, which needs
    # both for IDs for grabbing fields AND names for filtering the changelog
    #######################################################################
    jira_fields_data = download_fields(
        jira_connect_or_fallback_connection,
    )
    normalized_include_fields = expand_and_normalize_jira_fields(
        jira_fields_data, jira_config.include_fields
    )
    normalized_exclude_fields = expand_and_normalize_jira_fields(
        jira_fields_data, jira_config.exclude_fields
    )

    users: list[dict] = []
    if not jira_config.only_issues:

        filters = _construct_field_filters(
            include_field_ids=[f.jira_field_id for f in normalized_include_fields],
            exclude_field_ids=[f.jira_field_id for f in normalized_exclude_fields],
        )

        filtered_jira_fields = [
            field for field in jira_fields_data if all(filt(field) for filt in filters)
        ]

        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraFields.value,
            subdirectory=SubDirectory.JIRA,
            json_data=filtered_jira_fields,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        ######################################################################
        # Jira Users
        #######################################################################
        if not jira_config.skip_downloading_users or not jira_config.user_keys_in_jellyfish:
            users = download_users(
                jira_basic_connection=jira_connect_or_fallback_connection,
                jira_atlas_connect_connection=(
                    jira_atlas_connect_connection if jira_config.should_augment_emails else None
                ),  # Use AtlasConnect for 'augment with email' subtask
                gdpr_active=jira_config.gdpr_active,
                search_users_by_letter_email_domain=jira_config.search_users_by_letter_email_domain,
                required_email_domains=jira_config.required_email_domains,
                is_email_required=jira_config.is_email_required,
                using_connect_as_primary_auth=using_connect_as_primary_auth,
            )
        # Upload users, even if there aren't any
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraUsers.value,
            subdirectory=SubDirectory.JIRA,
            json_data=users,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Resolutions
        #######################################################################
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraResolutions.value,
            subdirectory=SubDirectory.JIRA,
            json_data=download_resolutions(jira_connect_or_fallback_connection),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Issue Types
        #######################################################################
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraIssueTypes.value,
            subdirectory=SubDirectory.JIRA,
            json_data=download_issuetypes(
                jira_connect_or_fallback_connection, project_ids=list(project_ids)
            ),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Link Types
        #######################################################################
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraLinkTypes.value,
            subdirectory=SubDirectory.JIRA,
            json_data=download_issuelinktypes(jira_connect_or_fallback_connection),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Priorities
        #######################################################################
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraPriorities.value,
            subdirectory=SubDirectory.JIRA,
            json_data=download_priorities(jira_connect_or_fallback_connection),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Statuses
        #######################################################################
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraStatuses.value,
            subdirectory=SubDirectory.JIRA,
            json_data=download_statuses(jira_connect_or_fallback_connection),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        #######################################################################
        # Jira Boards, Sprints, and Links
        #######################################################################
        if jira_config.download_boards:
            boards, sprints, links = download_boards_and_sprints(
                jira_connect_or_fallback_connection,
                jira_config.download_sprints,
                jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_ID, False),
                jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_BOARD_MAX_WORKERS, 5),
                jira_config.feature_flags.get(Constants.PULL_SPRINTS_BY_ID_MAX_WORKERS, 5),
                jira_config.feature_flags.get(Constants.PULL_SPRINTS_SKIP_INACTIVE, False),
                filter_boards_by_projects=(
                    set(project_ids) if jira_config.filter_boards_by_projects else None
                ),
            )
        else:
            boards, sprints, links = [], [], []
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraBoards.value,
            subdirectory=SubDirectory.JIRA,
            json_data=boards,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraSprints.value,
            subdirectory=SubDirectory.JIRA,
            json_data=sprints,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraBoardSprintLinks.value,
            subdirectory=SubDirectory.JIRA,
            json_data=links,
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

    if not jira_config.skip_issues:
        api_type = "JQL Enhanced Search" if use_jql_enhanced_search else "Legacy"
        logger.info(f"Using {api_type} API for Jira operations")

        # For Jira Issue operations we need to determine the batch size that
        # the JIRA provider will limit us to
        jira_issues_batch_size = get_jira_search_batch_size(
            jira_connection=jira_connect_or_fallback_connection,
            optimistic_batch_size=jira_config.issue_batch_size,
            use_jql_enhanced_search=use_jql_enhanced_search,
        )

        all_downloaded_issue_ids, all_deleted_issue_ids, users_found_across_all_issues = (
            pull_issues_wrapper(
                jira_connect_or_fallback_connection,
                jira_config=jira_config,
                projects_and_versions=projects_and_versions,
                include_fields=normalized_include_fields,
                exclude_fields=normalized_exclude_fields,
                jira_issues_batch_size=jira_issues_batch_size,
                ingest_io_helper=ingest_io_helper,
                ingest_config=ingest_config,
                use_jql_enhanced_search=use_jql_enhanced_search,
            )
        )

        logger.info(f'{len(all_deleted_issue_ids)} issues have been detected as being deleted')
        # Write issues that got deleted
        ingest_io_helper.write_json_to_local_or_s3(
            object_name=JiraObject.JiraIssuesIdsDeleted.value,
            subdirectory=SubDirectory.JIRA,
            json_data=list(all_deleted_issue_ids),
            save_locally=ingest_config.save_locally,
            upload_to_s3=ingest_config.upload_to_s3,
        )

        # For now, don't download any user data. Instead, upload the user data
        # so that we can see how many/which users would get downloaded
        logger.info(
            f'Found {len(users_found_across_all_issues)} unique users across all issues (and we have already pulled {len(users)} users in bulk)'
        )
        if jira_config.feature_flags.get(Constants.CHECK_ISSUES_FOR_EXTRA_USERS_AND_PULL):
            _process_additional_users_from_issues(
                jira_basic_connection=jira_basic_connection,
                jira_atlas_connect_connection=jira_atlas_connect_connection,
                ingest_config=ingest_config,
                jira_config=jira_config,
                ingest_io_helper=ingest_io_helper,
                users_downloaded_in_bulk=users,
                user_metadata_from_issues=users_found_across_all_issues,
            )

        #######################################################################
        # Jira Work Logs
        #######################################################################
        if jira_config.download_worklogs:
            ingest_io_helper.write_json_to_local_or_s3(
                object_name=JiraObject.JiraWorklogs.value,
                subdirectory=SubDirectory.JIRA,
                json_data=download_worklogs(
                    jira_connect_or_fallback_connection,
                    all_downloaded_issue_ids,
                    jira_config.work_logs_pull_from,
                ),
                save_locally=ingest_config.save_locally,
                upload_to_s3=ingest_config.upload_to_s3,
            )
    else:
        logger.info(
            f"Skipping issues and worklogs bc config.skip_issues is {jira_config.skip_issues}"
        )

    if ingest_config.save_locally:
        logger.info(f"Data has been saved locally to: {ingest_io_helper.local_file_path}")
    else:
        logger.info(
            f"Data has not been saved locally, because save_locally was set to false in the ingest config!"
        )

    if ingest_config.upload_to_s3:
        logger.info(f"Data has been submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")
    else:
        logger.info(f"Data was not submitted to {S3_OR_JELLYFISH_LOG_STATEMENT}")

    download_metadata = {
        'company_slug': ingest_config.company_slug,
        'ingest_type': ingest_config.ingest_type.value if ingest_config.ingest_type else None,
        'users_downloaded': not jira_config.skip_downloading_users,
        'boards_downloaded': jira_config.download_boards,
        'sprints_downloaded': jira_config.download_boards and jira_config.download_sprints,
        'issues_downloaded': not jira_config.skip_issues,
    }

    ingest_io_helper.write_json_to_local_or_s3(
        object_name=JiraObject.JiraDownloadMetadata.value,
        subdirectory=SubDirectory.JIRA,
        json_data=download_metadata,
        save_locally=ingest_config.save_locally,
        upload_to_s3=ingest_config.upload_to_s3,
    )

    return True


def _construct_field_filters(include_field_ids: list[str], exclude_field_ids: list[str]) -> list:
    """Filter out fields we want to exclude, provided exclude and include lists must have the Jira
    field ID names in them

    Args:
        include_field_ids (list[str]): A list of fields (by their Jira Field ID value)
        exclude_field_ids (list[str]): A list of fields (by their Jira Field ID value)

    Returns:
        list: A list of filter functions to filter out fields we don't want to submit to Jellyfish
    """
    filters = []
    if include_field_ids:
        filters.append(lambda field: field["id"] in include_field_ids)
    if exclude_field_ids:
        filters.append(lambda field: field["id"] not in exclude_field_ids)

    return filters


def _process_additional_users_from_issues(
    jira_basic_connection: JIRA,
    jira_atlas_connect_connection: Optional[JIRA],
    ingest_config: IngestionConfig,
    jira_config: JiraDownloadConfig,
    ingest_io_helper: IngestIOHelper,
    users_downloaded_in_bulk: list[dict],
    user_metadata_from_issues: list[UserMetadata],
):
    user_key = get_user_key(jira_config.gdpr_active)
    downloaded_user_keys = set([user[user_key] for user in users_downloaded_in_bulk])
    all_known_user_keys = downloaded_user_keys.union(jira_config.user_keys_in_jellyfish)
    user_data_to_download: list[UserMetadata] = []
    for user in user_metadata_from_issues:
        if user.user_key not in all_known_user_keys:
            user_data_to_download.append(user)

    additional_users = download_users_by_urls(
        jira_basic_connection=jira_basic_connection,
        jira_atlas_connect_connection=jira_atlas_connect_connection,
        user_urls=[u.self_url for u in user_data_to_download],
        required_email_domains=jira_config.required_email_domains,
        is_email_required=jira_config.is_email_required,
        num_parallel_threads=jira_config.issue_download_concurrent_threads,
    )

    all_users = []
    all_users.extend(users_downloaded_in_bulk)
    all_users.extend(additional_users)
    logger.info(
        f'Found an additional {len(additional_users)} users to the already downloaded {len(users_downloaded_in_bulk)} users downloaded in bulk. Uploading these users now'
    )
    # Overwrite users that were potentially already uploaded
    ingest_io_helper.write_json_to_local_or_s3(
        object_name=JiraObject.JiraUsers.value,
        subdirectory=SubDirectory.JIRA,
        json_data=all_users,
        save_locally=ingest_config.save_locally,
        upload_to_s3=ingest_config.upload_to_s3,
    )
