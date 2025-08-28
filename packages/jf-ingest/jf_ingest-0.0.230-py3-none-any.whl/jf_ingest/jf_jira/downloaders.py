import json
import logging
import math
import string
import threading
from contextlib import AbstractContextManager, nullcontext
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Union

import pytz
from jira import JIRA, JIRAError, Project
from requests import Response

from jf_ingest import diagnostics, logging_helper
from jf_ingest.adaptive_throttler import AdaptiveThrottler
from jf_ingest.config import IssueListDiff, IssueMetadata
from jf_ingest.constants import Constants
from jf_ingest.jf_jira.exceptions import (
    NoAccessibleProjectsException,
    NoJiraUsersFoundException,
)
from jf_ingest.jf_jira.utils import JiraFieldIdentifier, get_user_key_from_user
from jf_ingest.telemetry import add_telemetry_fields, jelly_trace, record_span
from jf_ingest.utils import (
    JIRA_SPRINT_ERRORS_TO_RETRY,
    JIRA_STATUSES_TO_RETRY,
    PROJECT_HTTP_CODES_TO_RETRY_ON,
    RetryLimitExceeded,
    ThreadPoolWithTqdm,
    batch_iterable,
    chunk_iterator_in_lists,
    format_date_to_jql,
    retry_for_status,
    tqdm_to_logger,
)

logger = logging.getLogger(__name__)


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_fields(
    jira_connection: JIRA,
) -> list[dict]:
    """Download JIRA Fields from the fields API endpoint

    Args:
        jira_connection (JIRA): A Jira Connection Object

    Returns:
        list[dict]: A list of raw JIRA Field Objects
    """
    logger.info("Downloading Jira Fields... ")

    fields = [
        field
        for field in retry_for_status(
            jira_connection.fields, statuses_to_retry=JIRA_STATUSES_TO_RETRY
        )
    ]

    logger.info(f"Done downloading Jira Fields! Found {len(fields)} fields")
    return fields


def _detect_project_rekeys_and_update_metadata(
    projects: list[Project],
    jellyfish_project_ids_to_keys: dict[str, str],
    jellyfish_issue_metadata: list[IssueMetadata],
) -> None:
    """Detects if a project has been rekeyed, and marks all related issue data as needs to be redownloaded.

    It marks the issues as needing to be redownloaded by setting their 'updated' field to datetime.min!

    Args:
        projects (list[Project]): A list of JIRA Project objects
        jellyfish_project_ids_to_keys (dict[str, str]): A lookup table for getting jira project IDs to Keys. Necesarry because a project KEY can change but it's ID never does
        jellyfish_issue_metadata (dict[str, dict]): A list of issue metadata from our database. Used to mark issues for potential redownload
    """
    rekeyed_projects = []
    for project in projects:
        # Detect if this project has potentially been rekeyed !
        if (
            project.id in jellyfish_project_ids_to_keys
            and project.raw["key"] != jellyfish_project_ids_to_keys[project.id]
        ):
            logging_helper.send_to_agent_log_file(
                f'Project (project_id={project.id}) {project.raw["key"]} was detected as being rekeyed (it was previously {jellyfish_project_ids_to_keys[project.id]}. Attempting to re-download all related jira issue data'
            )
            rekeyed_projects.append(project.id)

    # Mark issues for redownload if they are associated with rekeyed projects
    for metadata in jellyfish_issue_metadata:
        if metadata.project_id in rekeyed_projects:
            # Updating the updated time for each issue will force a redownload
            metadata.updated = pytz.utc.localize(datetime.min)


def _get_project_filters(
    include_projects: list[str],
    exclude_projects: list[str],
    include_categories: list[str],
    exclude_categories: list[str],
) -> list:
    filters = []
    if include_projects:
        filters.append(lambda proj: proj.key in include_projects)
    if exclude_projects:
        filters.append(lambda proj: proj.key not in exclude_projects)
    if include_categories:

        def _include_filter(proj):
            # If we have a category-based allowlist and the project
            # does not have a category, do not include it.
            if not hasattr(proj, "projectCategory"):
                return False

            return proj.projectCategory.name in include_categories

        filters.append(_include_filter)

    if exclude_categories:

        def _exclude_filter(proj):
            # If we have a category-based excludelist and the project
            # does not have a category, include it.
            if not hasattr(proj, "projectCategory"):
                return True

            return proj.projectCategory.name not in exclude_categories

        filters.append(_exclude_filter)
    return filters


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_projects_and_versions_and_components(
    jira_connection: JIRA,
    is_agent_run: bool,
    jellyfish_project_ids_to_keys: dict[str, str],
    jellyfish_issue_metadata: list[IssueMetadata],
    include_projects: list[str],
    exclude_projects: list[str],
    include_categories: list[str],
    exclude_categories: list[str],
) -> list[dict]:
    """Download Project Versions and Components

    Hits three separate APIs (projects, versions, and components)
    and squashes all of the data into one list of Project Data

    Args:
        jira_connection (JIRA): A Jira Connection Object
        is_agent_run (bool): A boolean flag that represents if the current run is an agent run
        jellyfish_project_ids_to_keys (dict[str, str]): A lookup table of Jellyfish Project IDs to Keys. Used for detecting rekeys
        jellyfish_issue_metadata (dict[str,dict]): A list of jellyfish issue metadata. Used to potentially mark issues as needing a redownload
        include_projects (list[str]): A list of projects to include exclusively
        exclude_projects (list[str]): A list of projects and exclude
        include_categories (list[str]): A list of categories to determine which projects to exclusively include
        exclude_categories (list[str]): A list of categories to determine which potential projects to exclude

    Raises:
        NoAccessibleProjectsException: Raise an exception if we cannot connect to a project

    Returns:
        list[dict]: A list of projects that includes Versions and Component data
    """
    with record_span('download_jira_projects'):
        logger.info("Downloading Jira Projects...")
        filters: list = (
            _get_project_filters(
                include_projects=include_projects,
                exclude_projects=exclude_projects,
                include_categories=include_categories,
                exclude_categories=exclude_categories,
            )
            if is_agent_run
            else []
        )

        all_projects: list[Project] = retry_for_status(
            jira_connection.projects, statuses_to_retry=PROJECT_HTTP_CODES_TO_RETRY_ON
        )

        projects = [proj for proj in all_projects if all(filt(proj) for filt in filters)]

        if not projects:
            raise NoAccessibleProjectsException(
                "No Jira projects found that meet all the provided filters for project and project category. Aborting... "
            )
        add_telemetry_fields({'jira_project_count': len(projects)})

        _detect_project_rekeys_and_update_metadata(
            projects=projects,
            jellyfish_project_ids_to_keys=jellyfish_project_ids_to_keys,
            jellyfish_issue_metadata=jellyfish_issue_metadata,
        )

        logger.info("Done downloading Projects!")

    with record_span('download_jira_components'):
        logger.info("Downloading Jira Project Components...")
        component_count = 0
        for p in projects:
            components = [
                c.raw
                for c in retry_for_status(
                    jira_connection.project_components,
                    p,
                    statuses_to_retry=PROJECT_HTTP_CODES_TO_RETRY_ON,
                )
            ]
            p.raw.update({"components": components})
            component_count += len(components)
        add_telemetry_fields({'jira_project_component_count': component_count})
        logger.info("Done downloading Project Components!")

    with record_span('download_jira_versions'):
        logger.info("Downloading Jira Versions...")
        result: list[dict] = []
        version_count = 0
        for p in projects:
            # OJ-47905: Fail gracefully if we cannot access versions for a project which is private/archived.
            try:
                versions = retry_for_status(
                    jira_connection.project_versions,
                    p,
                    max_retries_for_retry_for_status=3,
                    statuses_to_retry=PROJECT_HTTP_CODES_TO_RETRY_ON,
                )
            except RetryLimitExceeded as e:
                src_error = e.args[0]
                if getattr(src_error, "status_code", None) == 404 and p.raw.get("archived", False):
                    # If we get a 404 and the project is private AND
                    # we cannot access versions for this project, so just return an empty list
                    logger.info(
                        f'Cannot access versions for private and archived project {p.key}, returning empty list of versions.'
                    )
                    versions = []
                else:
                    raise e

            p.raw.update({"versions": [v.raw for v in versions]})
            result.append(p.raw)
            version_count += len(versions)
        add_telemetry_fields({'jira_project_version_count': version_count})
        logger.info("Done downloading Jira Versions!")

    logger.info(
        f"Done downloading Jira Project, Components, and Version. Found {len(result)} projects"
    )
    return result


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def _augment_users_helper(
    jira_atlas_connect_connection: Optional[JIRA], jira_users: list[dict]
) -> list[dict]:

    # Fetching user email requires Atlassian Connect connection
    if jira_atlas_connect_connection:
        augment_jira_users_with_email(jira_atlas_connect_connection, jira_users)
    else:
        # If we don't have emails, we don't need to record the date at
        # which we pulled them.
        for u in jira_users:
            u["email_pulled"] = None

    return jira_users


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_users_by_urls(
    jira_basic_connection: JIRA,
    jira_atlas_connect_connection: Optional[JIRA],
    user_urls: list[str],
    required_email_domains: list[str],
    is_email_required: bool,
    num_parallel_threads: int,
) -> list[dict]:
    jira_users: list[dict] = []
    with ThreadPoolWithTqdm(
        desc=f"Pulling {len(user_urls)} additional users by their URL (Thread Count: {num_parallel_threads})",
        total=len(user_urls),
        max_workers=num_parallel_threads,
    ) as pool:

        def _get_user(url: str) -> Optional[dict]:
            resp = jira_basic_connection._session.get(url)
            if resp.status_code == 200:
                resp_json: dict = resp.json()
                return resp_json
            else:
                return None

        for user_url in user_urls:
            pool.submit(_get_user, user_url)

        for user in pool.get_results():
            if user:
                jira_users.append(user)

    jira_users = _augment_users_helper(
        jira_atlas_connect_connection=jira_atlas_connect_connection, jira_users=jira_users
    )
    jira_users = _scrub_jira_users(jira_users, required_email_domains, is_email_required)

    return jira_users


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_users(
    jira_basic_connection: JIRA,
    jira_atlas_connect_connection: Optional[JIRA],  # Set this to NONE for Agent
    gdpr_active: bool,
    search_users_by_letter_email_domain: Optional[str] = None,  # Direct connect related Field
    required_email_domains: list[str] = [],  # Agent related field
    is_email_required: bool = False,  # Agent related Field
    using_connect_as_primary_auth: bool = False,
) -> list[dict]:
    """Download Jira Users to memory

    Args:
        jira_basic_connection (JIRA): A Jira connection authenticated with Basic Auth. Should NEVER be set to None!
        jira_atlas_connect_connection (JIRA): A Jira connection authenticated with Atlassian Direct Connect. Should be set to None
        when working with Agent or for specific instances in M.I.
        gdpr_active (bool): A boolean flag that represents if the client is Jira Server or Jira Cloud. If gdpr_active is False than the client is on Jira Server. For Jira Server clients we search for user data via _search_by_letter
        search_users_by_letter_email_domain (str, optional): Something set on Jira Instances (M.I.) that narrows down
        the search results when using _search_users_by_letter. ONLY APPLICABLE WITH JIRA SERVER INSTANCES. Defaults to None.
        required_email_domains (list[str], optional): Used by Agent, set up in the config.yml file. Used to filter for only specific users that we care about. Defaults to None.
        is_email_required (str, optional): When provided, if we are filtering by email domains (with required_email_domains) than this field WILL INCLUDE emails that have a null email field!!! Beware: counter intuitive!. Defaults to None.
        using_connect_as_primary_auth (bool, optional): If True, we are using Atlassian Connect for connections by default. Defaults to False.

    Returns:
        list[dict]: A list of raw jira users, augmented with emails
    """
    logger.info("Downloading Users...")
    jira_users = search_users(
        jira_connection=jira_basic_connection,
        gdpr_active=gdpr_active,
        search_users_by_letter_email_domain=search_users_by_letter_email_domain,
        using_connect_as_primary_auth=using_connect_as_primary_auth,
    )

    jira_users = _augment_users_helper(
        jira_atlas_connect_connection=jira_atlas_connect_connection, jira_users=jira_users
    )
    jira_users = _scrub_jira_users(jira_users, required_email_domains, is_email_required)

    if len(jira_users) == 0:
        raise NoJiraUsersFoundException(
            'We are unable to see any users. Please verify that this user has the "browse all users" permission.'
        )

    add_telemetry_fields({'jira_user_count': len(jira_users)})

    logger.info(f"Done downloading Users! Found {len(jira_users)} users")
    return jira_users


def search_users(
    jira_connection: JIRA,
    gdpr_active: bool,
    search_users_by_letter_email_domain: Optional[str] = None,
    page_size: int = 1000,
    using_connect_as_primary_auth: bool = False,
) -> list[dict]:
    """Handler for searching for users. IF GDPR is active, we use a good API endpoint. If GDPR is not active,
    we do a crazy 'search all letters' approach, because of a known bug in JIRA Server instances (https://jira.atlassian.com/browse/JRASERVER-65089)

    Args:
        jira_connection (JIRA): A Jira connection (Basic Auth)
        gdpr_active (bool): If True, we are on Jira Cloud (use the good API). If False, we use the painful _search_by_letter_approach
        search_users_by_letter_email_domain (str, optional): For Server only. Allows us to narrow down search results. Defaults to None.
        page_size (int, optional): _description_. Defaults to 1000.
        using_connect_as_primary_auth (bool, optional): If True, we are using Atlassian Connect for connections by default. Defaults to False.

    Raises:
        NoJiraUsersFoundException: _description_

    Returns:
        _type_: A list of raw jira users
    """
    if gdpr_active and not using_connect_as_primary_auth:
        jira_users = _get_all_users_for_gdpr_active_instance(
            jira_connection=jira_connection, page_size=page_size
        )
    else:
        jira_users = _search_users_by_letter(
            jira_connection=jira_connection,
            gdpr_active=gdpr_active,
            search_users_by_letter_email_domain=search_users_by_letter_email_domain,
            page_size=page_size,
            using_connect_as_primary_auth=using_connect_as_primary_auth,
        )

    logging_helper.send_to_agent_log_file(f"found {len(jira_users)} users")
    return jira_users


def get_searchable_jira_letters() -> list[str]:
    """Returns a list of lowercase ascii letters and all digits. DOES NOT INCLUDE PUNCTUATION!!!

    Note from Noah 6/28/22 - when using _search_users_by_letter with at least some
    jira server instances, some strange behavior occurs, explained with an example:
    take a case where search_users_by_letter_email_domain is set to '@business.com'
    meaning the query for the letter 'a' will be 'a@business.com'. Jira appears to
    take this query and split it on the punctuation and symbols, e.g [a, business, com].
    It then searches users username, name, and emailAddress for matches, performing the
    same punctuation and symbol split, and looking for matches starting at the beginning
    of each string, e.g. anna@business.com is split into [anna, business, com] and matches,
    but barry@business.com, split into [barry, business, com] will not match. Notably,
    these splits can match multiple substrings, which can lead to large lists of users.
    For example, when searching on the letter c, the full query would be 'c@business.com'
    split into [c, business, com]. This would obviously match cam@business.com, following
    the pattern from before, but unfortunately, the 'c' in the query will match any email
    ending in 'com', so effectively we will download every user. This will occur for
    letters matching every part of the variable search_users_by_letter_email_domain, split
    on punctuation and symbols.
    Notably, this will also happen when search_users_by_letter_email_domain is not set but
    there is still an overlap in the query and email address, e.g. query 'b' would hit all
    users in this hypothetical instance with an '@business.com' email address, since jira
    will split that address and search for strings starting with that query, matching b to business.
    In the future, this domain searching could provide a faster way than searching every
    letter to get all users for instances that have that variable set, but for the time
    being it requires pagination when searching by letter.


    Returns:
        list[str]: A list of lowercase ascii letters and all digits
    """
    return [*string.ascii_lowercase, *string.digits]


def _search_by_users_by_letter_helper(
    jira_connection: JIRA,
    base_query: str,
    search_users_by_letter_email_domain: Optional[str] = None,
    max_results: int = 1000,
    using_connect_as_primary_auth: bool = False,
    logged_warning: bool = False,
) -> list[dict]:
    """This is both a recursive and iterative function for searching for users on GDPR non compliant instances.
    It works by searching for each letter/number in the ascii set (get_searchable_jira_letters). If we find there
    are more than 1000 values for a letter, we will page for more results for that letter.

    IF we find that we can get exactly 1000 results for a letter and nothing more, that means we've likely hit
    this jira bug: https://jira.atlassian.com/browse/JRASERVER-65089. The work around for this scenario is to
    recursively iterate on THE NEXT letters that we want to search on. For example, if we are searching for the
    letter 'a', and we get exactly 1000 results than we would recurse on this function with the following queries:
    'aa', 'ab', 'ac', 'ad'... until we no longer run into this error

    Args:
        jira_connection (JIRA): _description_
        base_query (str): _description_
        search_users_by_letter_email_domain (str, optional): _description_. Defaults to None.
        max_results (int, optional): _description_. Defaults to 1000.
        using_connect_as_primary_auth (bool, optional): If True, we are using Atlassian Connect for connections by default. Defaults to False.
        logged_warning (bool, optional): A boolean flag that represents if we have already logged a warning about the jira bug. Defaults to False. Useful for reducing the volume of our logs when recursing, if recursing is necessary.

    Returns:
        list[dict]: A list of raw user objects
    """
    users: list[dict] = []
    for letter in get_searchable_jira_letters():
        start_at = 0
        query_iteration = f"{base_query}{letter}"
        query_to_search = (
            f"{query_iteration}@{search_users_by_letter_email_domain}"
            if search_users_by_letter_email_domain
            else f"{query_iteration}"
        )
        total_found_for_current_letters = 0
        while True:
            payload: dict[str, Union[str, int, bool]] = {
                "startAt": start_at,
                "maxResults": max_results,
                "includeActive": True,
                "includeInactive": True,
            }
            if not using_connect_as_primary_auth:
                payload["username"] = query_to_search
            else:
                payload["query"] = query_to_search

            users_page: list[dict] = retry_for_status(
                jira_connection._get_json,
                "user/search",
                payload,
                statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            )
            users.extend(users_page)
            total_found_for_current_letters += len(users_page)

            if not users_page:
                break
            start_at += len(users_page)

        # IF we get back a full page for a letter, than we need to refire I query.
        # Example: if we get 1000 users for the letter 'b', than we need to search
        # for ba, bb, bc, bd, etc.
        # Following work around from here: https://jira.atlassian.com/browse/JRASERVER-65089
        if total_found_for_current_letters in (10, 100, 1000):
            if not logged_warning:
                logger.warning(
                    f"Jira bug relating to only getting limited (10, 100, or 1000) results per page hit when querying for {query_to_search} encountered. "
                    f"Specifically it looks like we have found {total_found_for_current_letters} results for {query_to_search}"
                    "Recursing on this function to search for more user results"
                )
                logged_warning = True
            users.extend(
                _search_by_users_by_letter_helper(
                    jira_connection=jira_connection,
                    base_query=query_iteration,
                    search_users_by_letter_email_domain=search_users_by_letter_email_domain,
                    max_results=max_results,
                    using_connect_as_primary_auth=using_connect_as_primary_auth,
                    logged_warning=logged_warning,
                )
            )

    return users


def _search_users_by_letter(
    jira_connection: JIRA,
    gdpr_active: bool,
    search_users_by_letter_email_domain: Optional[str] = None,
    page_size: int = 1000,
    using_connect_as_primary_auth: bool = False,
) -> list[dict]:
    """Search the 'old' API with each letter in the alphabet. Only used for non-GDPR compliant servers or apps using Connect-based auth.

    Args:
        jira_connection (JIRA): Basic Jira Connection
        gdpr_active (bool): A boolean flag that represents if the client is Jira Server or Jira Cloud. If gdpr_active is False than the client is on Jira Server. For Jira Server clients we search for user data via _search_by_letter
        search_users_by_letter_email_domain (str, optional): If provided, email domain will be used to narrow down the list of returned users from the API. Defaults to None.
        page_size (int, optional): _description_. Defaults to 1000.
        using_connect_as_primary_auth (bool, optional): If True, we are using Atlassian Connect for connections by default. Defaults to False.

    Returns:
        _type_: _description_
    """
    non_deduped_jira_users: list[dict] = []
    if search_users_by_letter_email_domain and not gdpr_active:
        # NOTE: search_users_by_letter_email_domain doing searches by email domain
        # only works for Jira Servers (which should always have gdpr_active set to False)
        # support multiple domains via comma separated list
        for domain in search_users_by_letter_email_domain.split(","):
            if not domain:
                continue
            non_deduped_jira_users.extend(
                _search_by_users_by_letter_helper(
                    jira_connection=jira_connection,
                    base_query="",
                    search_users_by_letter_email_domain=domain,
                    max_results=page_size,
                    using_connect_as_primary_auth=using_connect_as_primary_auth,
                )
            )
    else:
        non_deduped_jira_users = _search_by_users_by_letter_helper(
            jira_connection=jira_connection,
            base_query="",
            max_results=page_size,
            using_connect_as_primary_auth=using_connect_as_primary_auth,
        )
    jira_users_dict = {
        get_user_key_from_user(u, using_connect_as_primary_auth): u for u in non_deduped_jira_users
    }

    return list(jira_users_dict.values())


def _get_all_users_for_gdpr_active_instance(
    jira_connection: JIRA,
    page_size=1000,
) -> list[dict]:
    """Gets ALL users from JIRA API. This includes active and inactive. Leverages
    the "Get All Users" API endpoint:
    https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-users/#api-rest-api-2-users-search-get

    Args:
        jira_connection (JIRA): Jira Connection
        max_results (int, optional): Total number of users per page. Defaults to 1000.

    Returns:
        _type_: Returns unique list of all Jira Users in the Jira instance
    """
    jira_users: dict[str, dict] = {}
    start_at = 0

    # Fetch users one page at a time
    while True:
        users = retry_for_status(
            jira_connection._get_json,
            "users/search",
            {
                "startAt": start_at,
                "maxResults": page_size,
            },
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )

        jira_users.update({get_user_key_from_user(u, gdpr_active=True): u for u in users})

        if len(users) == 0:
            break  # no need to keep paging
        else:
            start_at += len(users)

    return list(jira_users.values())


def _scrub_jira_users(
    jira_users: list[dict], required_email_domains: list[str], is_email_required: bool
) -> list[dict]:
    """Helper function for removing users we want to ignore. This is used predominantly by the agent as of 10/30/23

    Args:
        jira_users (list): _description_
        required_email_domains (list[str]): _description_
        is_email_required (bool): _description_
    """

    def _get_email_domain(email: str):
        try:
            return email.split("@")[1]
        except AttributeError:
            return ""
        except IndexError:
            return ""

    filtered_users: list[dict] = []
    required_email_domains_lowered = [
        email_domain.lower() for email_domain in required_email_domains
    ]
    for user in jira_users:
        """
        Scrubs external jira users in-place by overwriting 'displayName' and 'emailAddress' fields
        See OJ-5558 for more info.
        """
        if "accountType" in user and user["accountType"] == "customer":
            user["displayName"] = "EXTERNAL"
            user["emailAddress"] = ""

        # Filter out unwanted emails
        # (Agent use case)
        if required_email_domains_lowered:
            try:
                email = user["emailAddress"]
                email_domain = _get_email_domain(email)
                if email_domain.lower() in required_email_domains_lowered:
                    filtered_users.append(user)
            except KeyError:
                # NOTE: This was introduced in the Agent awhile ago
                # and honestly it seems like a bug from a UX perspective.
                # The comment around this functionality (see example.yml)
                # implies that this statement should really be 'if not is_email_required'
                # Switching this without doing any research could cause a flood
                # of bad user data to get ingested, though, so we'd need to do a careful
                # analysis of who has this flag set and work with them to straighten it out.
                # Pain.
                if is_email_required:
                    filtered_users.append(user)
        else:
            filtered_users.append(user)

    return filtered_users


def _should_augment_email(user: dict) -> bool:
    """Helper function for determing if a user should be augmented

    Args:
        user (dict): Raw user Object

    Returns:
        bool: Boolean (true if we SHOULD augment a user)
    """
    # if we don't have an accountId, or we got an email already,
    # then this instance isn't GPDR-ified; just use what we've got
    email = user.get("emailAddress")
    account_id = user.get("accountId")
    account_type = user.get("accountType")

    if email or not account_id:
        return False

    # OJ-6900: Skip Jira users that are of type "customer". These
    # are not particularly useful to Jellyfish (they are part of
    # Jira Service Desk) so skip fetching emails for them.
    elif account_type == "customer":
        return False

    return True


def augment_jira_users_with_email(jira_atlassian_connect_connection: JIRA, jira_users: list):
    """Attempts to augment a raw user object with an email, pulled from the
    atlassian direct connect JIRA connection. IF we do augment a user, we
    will add a new dictionary key to the raw user called 'email_pulled', which
    represents a UTC datetime of when we used the atlassian direct connect API.
    We need this timestamp to submit reports to Atlassian of when we used this
    API endpoint, see: https://developer.atlassian.com/cloud/jira/platform/user-privacy-developer-guide/#reporting-user-personal-data-for-your-apps

    Args:
        jira_atlassian_connect_connection (JIRA): A connection to Atlassian via their AtlassianConnect authentication
        jira_users (list): A list of raw users
    """

    user_ids = [u['accountId'] for u in jira_users if _should_augment_email(u) and 'accountId' in u]

    # Get all users in bulk
    id_to_email = dict()

    for chunk in tqdm_to_logger(
        chunk_iterator_in_lists(90, user_ids), desc='fetching bulk jira emails'
    ):
        qs = '&'.join(f'accountId={i}' for i in chunk)
        res = retry_for_status(
            jira_atlassian_connect_connection._get_json,
            f'user/email/bulk?{qs}',
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
        id_to_email.update({i['accountId']: i['email'] for i in res})

    for u in jira_users:
        # If we don't have an email, skip it
        if u['accountId'] not in id_to_email:
            u['email_pulled'] = None
            continue

        u['emailAddress'] = id_to_email[u['accountId']]
        u['email_pulled'] = datetime.now(timezone.utc)


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_resolutions(jira_connection: JIRA) -> list[dict]:
    """Downloads Jira Resolution objects

    Args:
        jira_connection (JIRA): A Jira connection object

    Returns:
        list[dict]: The raw Resolution objects
    """
    logger.info("Downloading Jira Resolutions...")
    try:
        result = [
            r.raw
            for r in retry_for_status(
                jira_connection.resolutions,
                statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            )
        ]
        logger.info(f"Done downloading Jira Resolutions! Found {len(result)} resolutions")
        return result
    except Exception as e:
        logger.warning(f'Error downloading resolutions, got {e}')
        return []


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_issuetypes(
    jira_connection: JIRA,
    project_ids: list[str],
) -> list[dict]:
    """
    For Jira next-gen projects, issue types can be scoped to projects.
    For issue types that are scoped to projects, only extract the ones
    in the included projects (by project_ids).

    Args:
        jira_connection (JIRA): Jira Connection
        project_ids (list[str]): List of Project IDs to include, if we
        are dealing with a 'next-gen' Jira Project

    Returns:
        list[dict]: List of Raw Issue Types pulled direct from Jira API
    """
    logger.info(
        "Downloading IssueTypes...",
    )
    result: list[dict] = []
    for it in retry_for_status(
        jira_connection.issue_types,
        statuses_to_retry=JIRA_STATUSES_TO_RETRY,
    ):
        if "scope" in it.raw and it.raw["scope"]["type"] == "PROJECT":
            if it.raw["scope"]["project"]["id"] in project_ids:
                result.append(it.raw)
        else:
            result.append(it.raw)
    logger.info(f"Done downloading IssueTypes! found {len(result)} Issue Types")
    return result


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_issuelinktypes(jira_connection: JIRA) -> list[dict]:
    """Download Jira Issue Link Types from the issueLinkType endpoint.

    Args:
        jira_connection (JIRA): A Jira connection, from the jira Python library

    Returns:
        list[dict]: A list of 'raw' JSON objects pulled directly from the issueLinkType endpoint
    """
    logger.info("Downloading IssueLinkTypes...")
    result = [
        lt.raw
        for lt in retry_for_status(
            jira_connection.issue_link_types,
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
    ]
    logger.info(f"Done downloading IssueLinkTypes! Found {len(result)} Issue Link Types")
    return result


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_priorities(jira_connection: JIRA) -> list[dict]:
    """Loads Jira Priorities from their API. Has 429 handling logic

    Args:
        jira_connection (JIRA): A Jira connection (with the provided Jira Library)

    Returns:
        list[dict]: A list of 'raw' JSON objects pulled from the 'priority' endpoint
    """
    logger.info("Downloading Jira Priorities...")
    result = [
        p.raw
        for p in retry_for_status(
            jira_connection.priorities,
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
    ]
    logger.info(f"Done downloading Jira Priorities! Found {len(result)} priorities")
    return result


def _board_active(board_id: int, jira_connection: JIRA) -> bool:
    """
    Determine if a board has had any activity in the past 30 days, implying that this board is
    actively used.
    """

    try:
        board_issues = retry_for_status(
            jira_connection._get_json,
            f'board/{board_id}/issue',
            params={'maxResults': 1, 'jql': 'updated > -30d'},
            base=jira_connection.AGILE_BASE_URL,
            statuses_to_retry=JIRA_SPRINT_ERRORS_TO_RETRY,
        )
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Got error trying to check {board_id=}. Not pulling it. Exception: {e}'
        )
        return False

    return bool(len(board_issues.get('issues', [])) >= 1)


def _download_board_sprints_helper(
    board: dict, jira_connection: JIRA, skip_inactive_board_sprints: bool = False
) -> tuple[dict, list[dict]]:
    """
    This downloads a board's sprints in a thread. This is used primarily when we don't know how many sprints
    we need to pull for a given board, only how many boards we need to pull from. This is used by the task
    download_board_sprints for threading.

    Args:
        board (dict): A dictionary of the board details
        jira_connection (JIRA): Jira Connection Object

    Returns:
        tuple[dict, list[dict]]: This function returns a tuple.
            The first value represents the provided board.
            The second value is a list of the returned sprints for the given board.
    """
    sprints_for_board = []

    start_at = 0
    batch_size = 50
    board_id = board["id"]

    if skip_inactive_board_sprints and not _board_active(board_id, jira_connection):
        logging_helper.send_to_agent_log_file(
            f'Board {board_id=} is not active, not pulling sprints.',
            level=logging.DEBUG,
        )
        return board, []

    while True:
        board_sprints_page = None
        try:
            board_sprints_page = retry_for_status(
                jira_connection.sprints,
                board_id=board_id,
                startAt=start_at,
                maxResults=batch_size,
                statuses_to_retry=JIRA_SPRINT_ERRORS_TO_RETRY,
            )
        except JIRAError as e:
            if e.status_code == 400:
                logging_helper.send_to_agent_log_file(
                    f"Board ID {board_id} (project {board['name']}) doesn't support sprints -- skipping",
                    level=logging.DEBUG,
                )
            else:
                # JIRA returns 500, 404, and 503s errors for various reasons: board is
                # misconfigured; "failed to execute search"; etc.  Just
                # skip and move on for all JIRAErrors
                logger.warning(
                    f"Couldn't get sprints for board {board_id} (HTTP Error Code {e.status_code})"
                )
        except RetryLimitExceeded as e:
            logger.warning(
                f'Retry limit exceeded when attempting to pull sprints for board {board_id}. Error: {e}'
            )

        if not board_sprints_page:
            break

        sprints_for_board.extend(board_sprints_page)
        start_at += len(board_sprints_page)

    return board, sprints_for_board


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_board_sprints(
    jira_connection: JIRA,
    all_jira_boards: list[dict],
    num_parallel_threads: int = 5,
    skip_inactive_board_sprints: bool = False,
) -> tuple[list[dict], list[dict]]:
    """
    Downloads sprints via paginated board sprint list (/boards/{board_id}/sprints) using threading.

    Args:
        jira_connection (JIRA): Jira Connection Object
        all_jira_boards (list[dict]): List of boards to fetch sprints against
        num_parallel_threads (Optional[int]): Number of workers to use when threading. Defaults to 5.

    Returns:
        tuple[list[dict], list[dict]]: This function returns two lists.
            The first list represents raw sprint data.
            The second list represents how sprints map to boards
    """
    all_sprints = []
    links = []

    # HACK(asm,2025-03-12): This looks a little silly, but because `_download_board_sprints_helper`
    # returns a two-element tuple, the tqdm bar has to have 2x the length to reflect reality.
    with ThreadPoolWithTqdm(
        desc=f"Pulling sprint data for {len(all_jira_boards)} boards (Thread Count: {num_parallel_threads})",
        total=len(all_jira_boards) * 2,
        max_workers=num_parallel_threads,
    ) as pool:
        for board in all_jira_boards:
            pool.submit(
                _download_board_sprints_helper,
                jira_connection=jira_connection,
                board=board,
                skip_inactive_board_sprints=skip_inactive_board_sprints,
            )

        for board, board_sprints in pool.get_results():
            all_sprints.extend(board_sprints)
            links.append({"board_id": board['id'], "sprint_ids": [s.id for s in board_sprints]})

    return all_sprints, links


def _download_sprints_by_id_helper(jira_connection: JIRA, sprint_id: int) -> Optional[dict]:
    """
    Pulls a sprint via id. Meant to be used with threads.
    """
    try:
        sprint: dict = retry_for_status(
            jira_connection.sprint,
            sprint_id,
            statuses_to_retry=JIRA_SPRINT_ERRORS_TO_RETRY,
        )
        return sprint
    except JIRAError as e:
        if e.status_code != 404:
            # We aren't guaranteed to get a sprint back per id. Skip any that don't come back (404), log others
            logging_helper.send_to_agent_log_file(
                f"Couldn't get sprint id {sprint_id} (HTTP Error Code {e.status_code}). Error: {e}",
                level=logging.WARNING,
            )
    except RetryLimitExceeded as e:
        logger.warning(f'Retry limit exceeded when attempting to pull sprints by id. Error: {e}')

    return None


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_sprints_by_id(
    jira_connection: JIRA, all_jira_boards: list[dict], num_parallel_threads: int = 5
) -> tuple[list[dict], list[dict]]:
    """
    Downloads sprints by id using the provided boards to determine limits.
    This works by fetching the maximum returned sprint ID per board, which uses the board sprint list.
    Once we know the largest id, individually pulling each sprint by id until reaching that maximum.
    This can be more performant for customers that have incredibly slow list responses for sprints.
    If Atlassian ever paginates via cursor or some form of cached response, this would be unnecessary.
        Atlassian currently paginates by index in the response, which means every list request has to crawl the entire
            available set and then return a subset of that based on the request.

    NOTE: THIS DOES NOT GENERATE SPRINT <-> BOARD LINKS.

    Downloads sprint ids via paginated board sprint list (/boards/{board_id}/sprints).
    Those ids are then used against the sprints detail view (/sprints/{sprint_id}).
    Args:
        jira_connection (JIRA): Jira Connection Object
        all_jira_boards (list[dict]): List of boards to fetch sprints against
        num_parallel_threads (Optional[int]): Number of workers to use when threading fetching issues by id.
            Defaults to 5.

    Returns:
        tuple[list[dict], list[dict]]: This function returns two lists.
            The first list represents raw sprint data.
            The second list represents how sprints map to boards. THIS WILL ALWAYS BE EMPTY.
    """
    all_sprints = []
    links: list[dict] = []
    max_id_to_fetch = 0

    for board in tqdm_to_logger(
        all_jira_boards,
        total=len(all_jira_boards),
        desc="Fetching sprint upper id limit via board sprints",
    ):
        board_id = board["id"]
        try:
            initial_response = retry_for_status(
                jira_connection.sprints,
                board_id=board_id,
                startAt=0,
                maxResults=1,
                statuses_to_retry=JIRA_SPRINT_ERRORS_TO_RETRY,
            )
            if initial_response.total:
                last_sprint = retry_for_status(
                    jira_connection.sprints,
                    board_id=board_id,
                    startAt=int(initial_response.total) - 1,
                    maxResults=1,
                    statuses_to_retry=JIRA_SPRINT_ERRORS_TO_RETRY,
                )
                if len(last_sprint):
                    max_id_to_fetch = max(max_id_to_fetch, last_sprint[0].id)
        except JIRAError as e:
            if e.status_code != 400:
                # JIRA returns 500, 404, and 503s errors for various reasons: board is
                # misconfigured; "failed to execute search"; etc.  Just
                # skip and move on for all JIRAErrors
                logger.warning(
                    f"Couldn't get sprints for board {board_id} (HTTP Error Code {e.status_code}). Error: {e}"
                )
        except RetryLimitExceeded as e:
            logger.warning(
                f'Retry limit exceeded when attempting to pull sprints for board {board_id}. Error: {e}'
            )

    with ThreadPoolWithTqdm(
        desc=f"Pulling sprint data through id {max_id_to_fetch} (Thread Count: {num_parallel_threads})",
        total=max_id_to_fetch,
        max_workers=num_parallel_threads,
    ) as pool:
        for i in range(1, max_id_to_fetch + 1):
            pool.submit(
                _download_sprints_by_id_helper,
                jira_connection=jira_connection,
                sprint_id=i,
            )

        for sprint in pool.get_results():
            if sprint:
                all_sprints.append(sprint)

    return all_sprints, links


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_boards_and_sprints(
    jira_connection: JIRA,
    download_sprints: bool,
    fetch_sprints_by_id: bool = False,
    board_max_threads: int = 5,
    sprint_ids_max_threads: int = 5,
    skip_inactive_board_sprints: bool = False,
    filter_boards_by_projects: Optional[set[str]] = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Downloads boards and sprints. This function is pretty inefficient, mostly due
    to limitations of JIRA. To fetch every sprint, we have to fetch every board. To do so,
    we fetch every board then hit another API to get the sprints related to that board (which
    potentially involves paging for sprints on one board, or fetching NO sprints for that board)

    Args:
        jira_connection (JIRA): Jira Connection Object
        download_sprints (bool): Boolean representing if we should skip pulling sprints or not
        fetch_sprints_by_id (Optional[bool]): Boolean representing if we should pull sprints by id instead of board
        board_max_threads (Optional[int]): Number of threads to use when fetching paginated sprints via boards.
            Defaults to 5.
        sprint_ids_max_threads (Optional[int]): Number of threads to use when fetching sprints individually by id.
            Defaults to 5.
        filter_boards_by_projects (Optional[set[str]]): List of project IDs to filter boards by. If None, all boards will be fetched.
            Defaults to None.

    Returns:
        tuple[list[dict], list[dict], list[dict]]: This function returns three lists. The first list represents
        raw board data. The second list represents raw sprint data. The last list represents how sprints map to boards
    """
    b_start_at = 0
    b_batch_size = 50
    all_jira_boards = []
    _project_ids = filter_boards_by_projects.copy() if filter_boards_by_projects else None
    with record_span('download_jira_boards'):
        logger.info(f"Downloading Boards...")
        project_key_or_id = _project_ids.pop() if _project_ids else None
        while True:
            kwargs = {
                'startAt': b_start_at,
                'maxResults': b_batch_size,
                'statuses_to_retry': JIRA_STATUSES_TO_RETRY,
            }
            if project_key_or_id:
                kwargs['projectKeyOrID'] = project_key_or_id
            jira_boards = retry_for_status(jira_connection.boards, **kwargs)  # type: ignore
            if not jira_boards:
                # If we are done fetching boards check if there are more
                # projects to fetch for. If there is, restart and continue
                # fetching boards.
                # If we are not filtering by projects, or we are out of
                # projects to fetch for, break out of the loop
                if _project_ids:
                    project_key_or_id = _project_ids.pop()
                    b_start_at = 0
                    continue
                else:
                    break
            b_start_at += len(jira_boards)
            all_jira_boards.extend([b.raw for b in jira_boards])

    # Dedup boards by id
    all_jira_boards = list({b['id']: b for b in all_jira_boards}.values())
    add_telemetry_fields({'jira_board_count': len(all_jira_boards)})
    logger.info(f"Done downloading Boards! Found {len(all_jira_boards)} boards")

    all_sprints = []
    links = []
    with record_span('download_sprints'):
        if download_sprints:
            if fetch_sprints_by_id:
                all_sprints, links = download_sprints_by_id(
                    jira_connection, all_jira_boards, sprint_ids_max_threads
                )
            else:
                all_sprints, links = download_board_sprints(
                    jira_connection, all_jira_boards, board_max_threads, skip_inactive_board_sprints
                )
        add_telemetry_fields({'jira_sprint_count': len(all_sprints)})

    return all_jira_boards, [s.raw for s in all_sprints], links


def get_jira_results_looped(
    jira_connection: JIRA,
    jql_query: str,
    batch_size: int,
    issue_count: int,
    expand_fields: list[str] = [],
    include_fields: list[JiraFieldIdentifier] = [],
    exclude_fields: list[JiraFieldIdentifier] = [],
    use_jql_enhanced_search: bool = False,
) -> list[dict]:
    """Get all issues from Jira using a JQL query. This function wraps _download_issue_page and loops until all pages have been fetched
    Args:
        jira_connection (JIRA): A JIRA connection object
        jql_query (str): A JQL query to fetch issues
        batch_size (int): The batch size to use when fetching issues
        issue_count (int): The total number of issues to fetch
        expand_fields (list[str]): A list of fields to expand
        include_fields (list[JiraFieldIdentifier]): A list of fields to include
        exclude_fields (list[JiraFieldIdentifier]): A list of fields to exclude
        use_jql_enhanced_search (bool, optional): Whether to use JQL Enhanced Search API (/search/jql) or legacy API (/search). Defaults to False.
    Returns:
        A list of raw issue objects
    """
    total_results: list[dict] = []
    logging_helper.send_to_agent_log_file(
        f"Fetching {issue_count} issues in batches of {batch_size} using jql {jql_query}",
        level=logging.DEBUG,
    )

    # Initialize pagination variables
    start_at = 0
    next_page_token = None
    first_iteration = True

    # Modified loop condition to handle both pagination types
    while (not use_jql_enhanced_search and start_at < issue_count) or (
        use_jql_enhanced_search and (next_page_token is not None or first_iteration)
    ):
        # Add conditional calling logic: call _download_issue_page with 3-value return when use_jql_enhanced_search=True, 2-value return otherwise
        if use_jql_enhanced_search:
            page_result = _download_issue_page(
                jira_connection=jira_connection,
                jql_query=jql_query,
                start_at=start_at,
                batch_size=batch_size,
                expand_fields=expand_fields,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                return_total=True,
                use_jql_enhanced_search=use_jql_enhanced_search,
                next_page_token=next_page_token,
                return_next_page_token=True,
            )
            results, total_to_fetch, next_page_token = page_result  # type: ignore
        else:
            page_result = _download_issue_page(
                jira_connection=jira_connection,
                jql_query=jql_query,
                start_at=start_at,
                batch_size=batch_size,
                expand_fields=expand_fields,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                return_total=True,
            )
            results, total_to_fetch = page_result  # type: ignore

        total_results.extend(results)

        # Update pagination variables: increment start_at for legacy API, use next_page_token for enhanced search
        if use_jql_enhanced_search:
            # For JQL Enhanced Search: continue if we have a next page token
            first_iteration = False  # Mark that we've completed the first iteration
        else:
            # For legacy API: increment start_at as before
            start_at += len(results)
            # if the total to fetch is different than what we expected, update the progress bar
            if total_to_fetch != issue_count:
                issue_count = total_to_fetch  # type: ignore

    logging_helper.send_to_agent_log_file(
        f"Done fetching {issue_count} issues in batches of {batch_size} using jql {jql_query}. {len(total_results)} results found",
        level=logging.DEBUG,
    )
    return total_results


def fetch_id_to_key_for_all_existing(
    jira_connection: JIRA,
    project_ids: List[str],
    pull_from: datetime,
    jql_filter: Optional[str] = None,
    use_jql_enhanced_search: bool = False,
) -> Dict[str, str]:
    """Given our local IssueMetadata, fetch all issues from Jira and return a dictionary of id to key
    Args:
        jira_connection (JIRA): A JIRA connection object
        project_ids (list[str]): A list of project IDs
        pull_from: the pull_from date
        jql_filter: an optional JQL filter to apply to the query
        use_jql_enhanced_search (bool): Whether to use JQL Enhanced Search API. Defaults to False.
    """

    id_to_key_on_remote = {}
    project_id_to_pull_from = {project_id: pull_from for project_id in project_ids}
    project_id_to_issue_count = _get_all_project_issue_counts(
        jira_connection=jira_connection,
        project_key_to_pull_from=project_id_to_pull_from,
        num_parallel_threads=10,
        jql_filter=jql_filter,
        use_jql_enhanced_search=use_jql_enhanced_search,
    )

    # Attempt to get maximum batch size for this "cheap" query. On Jira Cloud and most
    # Jira Servers we can go 10k at a time, but for some Jira Server's it limits us to 1000
    batch_size = get_jira_search_batch_size(
        jira_connection=jira_connection,
        optimistic_batch_size=10000,
        fields=['id', 'key'],
        use_jql_enhanced_search=use_jql_enhanced_search,
    )
    logging_helper.send_to_agent_log_file(
        f'Attempting to pull Key and ID from remote Jira Source for all issues, using batch_size of {batch_size}'
    )
    for proj_id, proj_issue_count in project_id_to_issue_count.items():
        jql_expression = generate_project_pull_from_jql(
            project_key=proj_id, pull_from=pull_from, jql_filter=jql_filter
        )
        logging_helper.send_to_agent_log_file(
            f"Fetching all IDs for {proj_id} (batch_size={batch_size}, jql={jql_expression})",
            level=logging.DEBUG,
        )
        issue_id_to_key = get_jira_results_looped(
            jira_connection=jira_connection,
            jql_query=jql_expression,
            batch_size=batch_size,
            issue_count=proj_issue_count,
            include_fields=[
                JiraFieldIdentifier(jira_field_id='id', jira_field_name='id'),
                JiraFieldIdentifier(jira_field_id='key', jira_field_name='key'),
            ],
            use_jql_enhanced_search=use_jql_enhanced_search,
        )
        id_to_key_on_remote.update({str(issue['id']): issue['key'] for issue in issue_id_to_key})

    return id_to_key_on_remote


def get_issue_ids_for_rekeys_and_deletes(
    jira_connection: JIRA,
    jellyfish_issue_metadata: list[IssueMetadata],
    project_key_to_id: dict[str, str],
    pull_from: datetime,
    jql_filter: Optional[str] = None,
    use_jql_enhanced_search: bool = False,
) -> IssueListDiff:
    """This is part of the "new sync" path, and this function is responsible for crawling
    over all remote Issue Key and IDs and detecting what has been deleted and what has been
    rekeyed. The subfunction that crawls over the API will query for 10k issues at a time.

    Args:
        jira_connection (JIRA): A valid Jira Connection
        jellyfish_issue_metadata (list[IssueMetadata]): A list of Issue meta data from Jellyfish
        project_key_to_id (dict[str, str]): A translation dictionary to get ID from Key (for Jira Projects)
        pull_from (datetime): The root pull from for this Jira Instance
        jql_filter (Optional[str]): An optional JQL filter to apply to the query
        use_jql_enhanced_search (bool): Whether to use JQL Enhanced Search API (/search/jql) instead of legacy API (/search)

    Returns:
        IssueListDiff: A named Tuple indicating what needs to get deleted and what needs to get downloaded
    """
    issue_ids_to_download: set[str] = set()

    logger.info("Processing projects and issues from remote")
    project_ids = list(project_key_to_id.values())

    if len(project_ids) == 0 and len(jellyfish_issue_metadata) > 0:
        logger.warning("No valid projects found in local metadata")

    logger.info(f"Fetching list of all jira issue ID/key from remote to match local")
    id_to_key_on_remote = fetch_id_to_key_for_all_existing(
        jira_connection, project_ids, pull_from, jql_filter, use_jql_enhanced_search
    )

    # Transform local issues to lookup table for ID to Key
    id_to_key_on_local = {str(issue.id): issue.key for issue in jellyfish_issue_metadata}

    # Get two unique sets for remote and local to compare to find things deleted in Jira
    ids_on_local = set([issue.id for issue in jellyfish_issue_metadata])
    ids_on_remote = set(id_to_key_on_remote.keys())

    # all deleted
    issue_ids_to_delete = ids_on_local.difference(ids_on_remote)
    logger.info(
        f"{len(id_to_key_on_local)} issues local, {len(id_to_key_on_remote)} issues remote, "
        f"{len(issue_ids_to_delete)} issues deleted"
    )

    # all changed key
    detected_rekey_count = 0
    for issue_id in id_to_key_on_local.keys():
        if (
            issue_id in id_to_key_on_remote
            and id_to_key_on_local[issue_id] != id_to_key_on_remote[issue_id]
        ):
            detected_rekey_count += 1
            issue_ids_to_download.add(issue_id)

    logger.info(
        f'{detected_rekey_count} issues have been detected as being rekeyed. These will be redownloaded'
    )

    # everything on remote in the pull_from window not on local is "new" but could have been deleted from local.
    issue_ids_to_create = ids_on_remote.difference(ids_on_local)
    logger.info(
        f"{len(issue_ids_to_create)} issues found on remote not found on local. These will be downloaded."
    )
    issue_ids_to_download.update(issue_ids_to_create)

    issue_list_for_download = IssueListDiff(
        ids_to_delete=issue_ids_to_delete, ids_to_download=issue_ids_to_download
    )

    add_telemetry_fields(
        {
            'jira_issue_ids_on_local': len(ids_on_local),
            'jira_issue_ids_on_remote': len(ids_on_remote),
            'jira_issue_ids_to_delete': len(issue_ids_to_delete),
            'jira_issue_ids_to_create': len(issue_ids_to_create),
            'jira_issue_ids_to_rekey': detected_rekey_count,
            'jira_issue_ids_to_download': len(issue_ids_to_download),
        }
    )

    return issue_list_for_download


def generate_project_pull_from_bulk_jql(
    project_keys: list[str],
    project_key_to_pull_from: dict[str, datetime],
    jql_filter: Optional[str] = None,
) -> str:
    """Generates a JQL for a batch of project keys, and the pull from for each specific project.
    We attempt to pull issues by date for multiple projects in an attempt to reduce the number
    of API calls we have to make

    Args:
        project_keys (list[str]): A list of Project keys to construct the JQL out of.
        project_key_to_pull_from (dict[str, datetime]): A lookup table, that has a pull from for each Project Key
        jql_filter (Optional[str], optional): An optional JQL filter to add to the query. Defaults to None.

    Returns:
        str: (project = {project_key_1} AND updated > 2024-01-01) OR (project = {project_key_2} AND updated > 2024-10-13) order by id asc
    """
    jql_substrings = [
        f'(project = {project_key} AND updated > {format_date_to_jql(project_key_to_pull_from[project_key])})'
        for project_key in project_keys
    ]
    jql_full_str = ' OR '.join(jql_substrings)
    if jql_filter:
        jql_full_str += f' AND ({jql_filter})'
    jql_full_str += ' order by id asc'
    return jql_full_str


def generate_project_pull_from_jql(
    project_key: str, pull_from: datetime, jql_filter: Optional[str] = None
) -> str:
    """Generates a JQL for a given project key and a pull from date

    Args:
        project_key (str): A project Key
        pull_from (datetime): A 'pull_from' date
        jql_filter (Optional[str]): An optional JQL filter to add to the query

    Returns:
        str: project = {project_key} AND updated > {format_date_to_jql(pull_from)} order by id asc
    """
    if jql_filter:
        logging_helper.send_to_agent_log_file(
            f"Using additional JQL issue filter from config: {jql_filter}",
            level=logging.DEBUG,
        )
        return f'(project = "{project_key}" AND updatedDate > {format_date_to_jql(pull_from)}) AND ({jql_filter}) order by id asc'
    else:
        return f'project = "{project_key}" AND updatedDate > {format_date_to_jql(pull_from)} order by id asc'


def _get_all_project_issue_counts(
    jira_connection: JIRA,
    project_key_to_pull_from: dict[str, datetime],
    num_parallel_threads: int,
    jql_filter: Optional[str] = None,
    use_jql_enhanced_search: bool = False,
) -> dict[str, int]:
    """A helper function for quickly getting issue counts for each
    provided project. Filters against pull_from in it's JQL,
    and runs concurrently up to the num_parallel_threads value.
    NOTE: When pulling project counts, we should ALWAYS go one by one
    to ensure we get a reliable and accurate count!

    Args:
        jira_connection (JIRA): A Jira Connection object
        project_key_to_pull_from (dict[str, datetime]): A dictionary of Project Keys to Pull From
        num_parallel_threads (int): The total size of the thread pool to use
        jql_filter (Optional[str]): An optional JQL filter to apply to the query

    Returns:
        dict[str, int]: A dictionary mapping the project key to it's issue count
    """
    project_key_to_issue_count: dict[str, int] = {}
    # Sanity check, do an early return if we don't have any project keys to pull from
    if len(project_key_to_pull_from) == 0:
        logging_helper.send_to_agent_log_file(
            msg='No project keys to pull from provided', level=logging.WARNING
        )
        return project_key_to_issue_count

    def _update_project_key_issue_count_dict(project_key: str, project_pull_from: datetime):
        project_key_to_issue_count[project_key] = _get_issue_count_for_jql(
            jira_connection=jira_connection,
            # NOTE: We should ALWAYS pull project counts one by one, to make
            # sure we get accurate counts for each project
            jql_query=generate_project_pull_from_jql(
                project_key=project_key,
                pull_from=project_pull_from,
                jql_filter=jql_filter,
            ),
            use_jql_enhanced_search=use_jql_enhanced_search,
        )

    total_projects = len(project_key_to_pull_from)
    with ThreadPoolWithTqdm(
        desc=f"Getting total issue counts for {total_projects} projects (Thread Count: {num_parallel_threads})",
        total=total_projects,
        max_workers=num_parallel_threads,
    ) as pool:
        for project_key, project_pull_from in project_key_to_pull_from.items():
            pool.submit(
                _update_project_key_issue_count_dict,
                project_key=project_key,
                project_pull_from=project_pull_from,
            )

    return project_key_to_issue_count


def get_jira_search_batch_size(
    jira_connection: JIRA,
    optimistic_batch_size: int = Constants.MAX_ISSUE_API_BATCH_SIZE,
    fields: Iterable[str] = ('*all',),
    use_jql_enhanced_search: bool = False,
) -> int:
    f"""A helper function that gives us the batch size that the
    JIRA provider wants to use. A lot of JIRA instances have their
    own batch sizes. Typically a JIRA SERVER will give us a batch size
    of 1000, but JIRA Cloud tends to limit us to 100. This function
    will attempt to get the highest reasonable batchsize possible.
    We've noticed some problems when querying for issues as high as
    1000, so we've limited the batch_size to be {Constants.MAX_ISSUE_API_BATCH_SIZE}

    Args:
        jira_connection (JIRA): A Jira Connection Object
        optimistic_batch_size (int, optional): An optimistic batch size. Defaults to {Constants.MAX_ISSUE_API_BATCH_SIZE}.
        fields ([Iterable[str]): A list of fields to include in the query. Defaults to ('*all',).
        use_jql_enhanced_search (bool, optional): Whether to use JQL Enhanced Search API. Defaults to False.

    Returns:
        int: The batchsize that JIRA is going to force us to use
    """
    if use_jql_enhanced_search:
        return _get_batch_size_with_jql_enhanced_search(fields, optimistic_batch_size)
    else:
        max_res: int = _post_raw_result(
            jira_connection,
            jql_query="",
            fields=list(fields),
            expand=[],
            start_at=0,
            max_results=optimistic_batch_size,
        )['maxResults']
        return max_res


def _get_issue_count_for_jql(
    jira_connection: JIRA, jql_query: str, use_jql_enhanced_search: bool = False
) -> int:
    """Returns the total number of issues that we have access to via a given JQL

    Args:
        jira_connection (JIRA): A Jira Connection Object
        jql_query (str): A given JQL string that we want to test
        use_jql_enhanced_search (bool): Whether to use JQL Enhanced Search API

    Returns:
        int: The total number of issues that the JQL will yield
    """
    # Simple if/else logic to call appropriate helper function
    if use_jql_enhanced_search:
        return _get_issue_count_with_jql_enhanced_search(jira_connection, jql_query)
    else:
        try:
            total_issue_count: int = retry_for_status(
                jira_connection.search_issues,
                jql_query,
                startAt=0,
                fields="id",
                maxResults=1,  # Weird JIRA behavior, when you set max results to 0 it attempts to grab all issues
                json_result=True,
                statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            )['total']
            return total_issue_count
        except JIRAError as e:
            if hasattr(e, "status_code") and 400 <= e.status_code < 500:
                logging_helper.send_to_agent_log_file(
                    f"Exception when querying for JQL: {jql_query} - (HTTP ERROR {e.status_code}):\n{e}\nskipping...",
                    level=logging.WARNING,
                    exc_info=True,
                )
                return 0
            else:
                raise


def _expand_changelog(
    jira_connection: JIRA, jira_issues: list[dict], batch_size: int
) -> list[dict]:
    """Expands the change log for a given list of issues. Each Jira Issues has a page
    of changelogs, which is limited to roughly 50 items. If there are more than 50 items
    in the Jira instance, than we will need to page on that issue for the rest of the
    changelogs. This function is that paging logic

    Args:
        jira_connection (JIRA): A Jira Connection Object
        jira_issues (list[dict]): A list of JIRA Issue objects
        batch_size (int): The batchsize JIRA is going to restrict us to for paging

    Returns:
        list[dict]: The jira_issues that we received, but with the change log expanded
    """
    # TODO: Move this to a more appropriate location and save the server_info.
    # We should not call this API for potentially every issue
    # HACK(asm,2024-07-25): The `issue/:issue_id/changelog` endpoint is only supported for Jira cloud
    server_info = retry_for_status(
        jira_connection.server_info,
        statuses_to_retry=JIRA_STATUSES_TO_RETRY,
    )
    if not server_info.get('deploymentType') == 'Cloud':
        return jira_issues

    for issue in jira_issues:
        changelog = issue.get("changelog")

        # If there is no changelog associated with the issue, there is nothing to expand
        if not changelog:
            continue

        # Happy path - we already have all changelog entries for this issue
        if changelog['total'] <= changelog['maxResults']:
            continue

        # If we have a changelog and there are more changelog entries to pull, grab them

        # NOTE(asm,2024-07-24): We discard the list of histories that are already on the issue
        # purposefully - the un-paginated list of histories are the most recent history entries, so
        # this loop repopulates them starting from the oldest history item.
        changelog['histories'] = list()

        # batch_size is usually defaulted to 250, which doesn't work properly with Jira cloud - use
        # whichever is smaller, the value the API tells us or the passed-in value.
        page_size = min(batch_size, changelog['maxResults'])
        for i in range(0, math.ceil(changelog['total'] / page_size)):
            more_changelogs = retry_for_status(
                jira_connection._get_json,
                f"issue/{issue['id']}/changelog",
                {"startAt": page_size * i, "maxResults": page_size},
                statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            )["values"]
            changelog["histories"].extend(i for i in more_changelogs)
    return jira_issues


def _filter_changelogs(
    issues: list[dict],
    include_fields: list[JiraFieldIdentifier],
    exclude_fields: list[JiraFieldIdentifier],
) -> list[dict]:
    """The JIRA API will respect our include and exclude fields for top level
    issues, but it will often NOT respect it in it's historic data (changelog data).
    This function crawls all the change logs and scrubs out fields we do or do not
    want to have. When fetching fields from the API endpoint, we use the fieldId.
    When scrubbing changelogs we try to use the fieldId, but for Jira Server we
    often have to fall back to the fieldName

    Args:
        issues (list[dict]): A list of JIRA issues
        include_fields (list[JiraFieldIdentifier]): A list of fields we exclusively want
        exclude_fields (list[JiraFieldIdentifier]): A list of fields we want to scrub out

    Returns:
        list[dict]: A list of JIRA issues with a scrubbed changelog history
    """
    cleaned_issues = []
    for issue in issues:
        if "changelog" in issue:
            changelog = issue["changelog"]
            if "histories" in changelog:
                histories = changelog["histories"]
                for history in histories:
                    cleaned_items = []
                    for item in history.get("items", []):
                        if include_fields:
                            if not any(
                                [field.matches_changelog_item(item) for field in include_fields]
                            ):
                                continue
                        if exclude_fields:
                            if any(
                                [field.matches_changelog_item(item) for field in exclude_fields]
                            ):
                                continue
                        cleaned_items.append(item)

                    history["items"] = cleaned_items

        cleaned_issues.append(issue)

    return cleaned_issues


def is_jql_enhanced_search_available(jira_connection: JIRA) -> bool:
    """
    Test if /search/jql endpoint is available with a minimal API call.

    The new /search/jql endpoint:
    - Uses nextPageToken instead of startAt for pagination
    - Has a 5,000 issue limit (vs 10,000 for legacy /search)
    - May not be available on older Jira instances

    Returns:
        bool: True if /search/jql is available, False if we should use legacy /search
    """
    try:
        payload = {
            'jql': 'updatedDate >= -1d order by id',
            'fields': ['id'],
            'maxResults': 1,
        }
        url = jira_connection._get_url('search/jql')

        response = jira_connection._session.post(
            url=url,
            json=payload,
        )

        # 200-299: Endpoint exists and works
        if 200 <= response.status_code < 300:
            logger.debug("JQL Enhanced Search API (/search/jql) is available")
            return True

        # 404: Endpoint doesn't exist (older Jira version)
        if response.status_code == 404:
            logger.info(
                "JQL Enhanced Search API (/search/jql) not available (404), using legacy /search API"
            )
            return False

        # Other errors (auth, permissions, etc.): Fallback to legacy API for safety
        # This is more conservative than the original design but safer for production
        logger.warning(
            f"JQL Enhanced Search API test returned status {response.status_code}, falling back to legacy /search API"
        )
        return False

    except Exception as e:
        # Network errors, connection issues, etc.: Fallback to legacy API
        logger.warning(
            f"Failed to test /search/jql endpoint availability: {e}, falling back to legacy /search API"
        )
        return False


def _post_raw_result(
    jira_connection: JIRA,
    jql_query: str,
    fields: list[str],
    expand: list[str],
    start_at: int,
    max_results: int,
) -> dict:
    """Helper function for sending a POST call to the Jira API.
    To get around batch_size limitations in the JIRA python library,
    we do a POST command directly against the API endpoint. This allows
    us to throttle Jira as much as possible.
    This function is shared between get_issues_with_post, and
    get_jira_batch_size.

    Args:
        jira_connection (JIRA): A Jira Connection Object
        jql_query (str): A JQL query to hit the endpoint with
        fields (list[str]): The fields to get back
        expand (list[str]): The fields to expand
        start_at (int): The start at index
        max_results (int): The batch size to request

    Returns:
        Dict: A JSON objects. Technically this could be a list, but in practice I don't think it ever is.
    """
    response: Response = retry_for_status(
        jira_connection._session.post,
        url=jira_connection._get_url('search'),
        data=json.dumps(
            {
                'jql': jql_query,
                'fields': fields,
                'expand': expand,
                'startAt': start_at,
                'maxResults': max_results,
            }
        ),
        statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        max_retries_for_retry_for_status=3,
    )
    r: dict = response.json()
    return r


def get_issues_with_post(
    jira_connection: JIRA,
    jql_query: str,
    fields: list[str],
    expand: list[str],
    start_at: int,
    max_results: int,
) -> tuple[list[dict], int]:
    """This is a helper function that hits the JIRA API Search (issues) endpoint
    using POST instead of the library provided GET method. We need to use POST
    because sometimes for JIRA server we can hang indefinitely when using GET
    instead of POST, particularly when we are ingesting a very large issue

    Args:
        jira_connection (JIRA): A Jira connection Object
        jql_query (str): The JQL query to hit the API with
        fields (list[str]): The list of fields we want from the API
        expand (list[str]): The list of fields to expand
        start_at (int): The index to start at
        max_results (int): The maximum batch size to return. If the returned max_results value
        DOES NOT MATCH the requested, this will raise an error. "returned max_results" does not
        mean the total number of returned items; Jira returns us an accurate max_results of the
        total results it could return us, based on our query. To get the proper max_results to
        request with, you should first get the maximum batchsize this jira instance will allow
        for this query using get_jira_search_batch_size()

    Raises:
        A potential exception will get raised if you request with a batch_size that is too
        high for the Jira server to handle. To avoid this, please first use the get_jira_search_batch_size
        function to find the optimum batch_size to use

    Returns:
        tuple containing;
        - list[dict]: A list of issues in raw dictionary form
        - str representing the number of total issues for the jql query
    """
    json_response = _post_raw_result(
        jira_connection=jira_connection,
        jql_query=jql_query,
        fields=fields,
        expand=expand,
        start_at=start_at,
        max_results=max_results,
    )
    returned_max_results = json_response['maxResults']
    issues = json_response['issues']
    total_issues = json_response['total']
    if returned_max_results != max_results:
        raise Exception(
            f'JIRA maxResults does not match the requested maxResults ({max_results} != {returned_max_results})! '
            'This means that we are requesting a batch size that is too large! '
            f'start_at: {start_at}, request_max_results: {max_results}, '
            f'returned_max_results={returned_max_results}, total_issues: {total_issues}.'
        )
    return issues, total_issues


def get_issues_with_post_enhanced(
    jira_connection: JIRA,
    jql_query: str,
    fields: list[str],
    expand: list[str],
    max_results: int,
    next_page_token: Optional[str] = None,
) -> tuple[list[dict], int, Optional[str]]:
    """Helper function for JQL Enhanced Search API that hits the /search/jql endpoint.
    This function is specifically designed for the new JQL Enhanced Search API and
    always returns a consistent 3-value tuple.

    Args:
        jira_connection (JIRA): A Jira connection Object
        jql_query (str): The JQL query to hit the API with
        fields (list[str]): The list of fields we want from the API
        expand (list[str]): The list of fields to expand
        max_results (int): The maximum batch size to return (max 5,000 for ID-only queries)
        next_page_token (Optional[str]): Token for pagination, None for first page

    Returns:
        tuple containing:
        - list[dict]: A list of issues in raw dictionary form
        - int: The number of issues returned in this batch (len(issues))
        - Optional[str]: The next page token for pagination, None if no more pages
    """
    json_response = _post_raw_result_jql_enhanced(
        jira_connection=jira_connection,
        jql_query=jql_query,
        fields=fields,
        expand=expand,
        max_results=max_results,
        next_page_token=next_page_token,
    )

    issues = json_response['issues']
    total = len(issues)  # JQL Enhanced Search doesn't provide total count, use batch size
    next_token = json_response.get('nextPageToken')

    return issues, total, next_token


def _download_issue_page(
    jira_connection: JIRA,
    jql_query: str,
    start_at: int,
    batch_size: int,
    expand_fields: list[str] = ["changelog"],
    include_fields: list[JiraFieldIdentifier] = [],
    exclude_fields: list[JiraFieldIdentifier] = [],
    return_total: bool = False,
    adaptive_throttler: Optional[AdaptiveThrottler] = None,
    use_jql_enhanced_search: bool = False,
    next_page_token: Optional[str] = None,
    return_next_page_token: bool = False,
) -> Union[
    list[dict],
    tuple[list[dict], int],
    tuple[list[dict], Optional[str]],
    tuple[list[dict], int, Optional[str]],
]:
    """Our main access point for getting JIRA issues. ALL functions responsible
    for fetching JIRA issues should leverage this helper function. This means
    that the function for fetching issues by date and issues by ID both funnel
    to this function

    This function leverages a bisecting search, to try to isolate problem issues
    in a given batch. It works by shrinking the batch size when we encounter an error,
    until we can isolate which JIRA issue(s) is giving us exceptions

    Args:
        jira_connection (JIRA): A JIRA connection object
        jql_query (str): The JQL we want to hit the API with
        start_at (int): The Start At value to use against the API
        batch_size (int): The batchsize that Jira forces us to use
        expand_fields (Optional[list[str]], optional): Fields we want to expand on the JIRA API. Defaults to ["changelog"].
        include_fields (list[JiraFieldIdentifier], optional): A list of fields we want to exclusively use on the API. Defaults to [].
        exclude_fields (list[JiraFieldIdentifier], optional): A list of fields we want to scrub out. Defaults to [].
        return_total: default False but if True also return the total number of issues for a jql query (ie response.json()['total'] after pulling a segment)
        adaptive_throttler (Optional[AdaptiveThrottler], optional): An adaptive throttler object to use for rate limiting. Defaults to None.
        use_jql_enhanced_search (bool, optional): If True, use JQL Enhanced Search API (/search/jql) with nextPageToken pagination. Defaults to False.
        next_page_token (Optional[str], optional): Token for JQL Enhanced Search pagination. Only used when use_jql_enhanced_search=True. Defaults to None.

    Returns:
        list[dict] | tuple[list[dict], int] | tuple[list[dict], int, Optional[str]]: One BATCH of issues, and potentially the total number of issues for a jql query. When use_jql_enhanced_search=True, also returns next_page_token.
    """
    changeable_batch_size = batch_size
    end_at = start_at + batch_size
    context_manager: Callable[..., AbstractContextManager]

    if adaptive_throttler:
        context_manager = adaptive_throttler.process_response_time
    else:
        context_manager = nullcontext

    while True:
        try:
            # Get Issues
            # NOTE: We use POST here because for some version of JIRA server
            # it is possible that it chokes up on large issues when using GET calls
            # (the jira library uses GET, so we need to interface with the session
            # object directly). See get_issues_with_post
            logging_helper.send_to_agent_log_file(
                f'{threading.get_native_id()} | started get_issues_with_post - {start_at=}',
                level=logging.DEBUG,
            )

            with context_manager():
                if use_jql_enhanced_search:
                    # Use JQL Enhanced Search API with nextPageToken pagination
                    issues, total, next_token = get_issues_with_post_enhanced(
                        jira_connection=jira_connection,
                        jql_query=jql_query,
                        fields=get_fields_spec(
                            include_fields=[f.jira_field_id for f in include_fields],
                            exclude_fields=[f.jira_field_id for f in exclude_fields],
                        ),
                        expand=expand_fields,
                        max_results=changeable_batch_size,
                        next_page_token=next_page_token,
                    )
                else:
                    # Use legacy API with startAt pagination
                    issues, total = get_issues_with_post(
                        jira_connection=jira_connection,
                        jql_query=jql_query,
                        # Note: we also rely on key, but the API 401s when
                        # asking for it explicitly, though it comes back anyway.
                        # So just ask for updated.
                        fields=get_fields_spec(
                            include_fields=[f.jira_field_id for f in include_fields],
                            exclude_fields=[f.jira_field_id for f in exclude_fields],
                        ),
                        expand=expand_fields,
                        start_at=start_at,
                        max_results=changeable_batch_size,
                    )
                    next_token = None

            logging_helper.send_to_agent_log_file(
                f'{threading.get_native_id()} | finished get_issues_with_post - {start_at=}',
                level=logging.DEBUG,
            )
            # Potentially expand the changelogs
            issues = _expand_changelog(jira_connection, issues, batch_size)

            # Filter the changelogs
            issues_with_changelogs = _filter_changelogs(
                issues=issues,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
            )

            # Build return tuple based on what's requested
            if use_jql_enhanced_search and return_next_page_token:
                if return_total:
                    return issues_with_changelogs, total, next_token
                else:
                    return issues_with_changelogs, next_token
            elif return_total:
                return issues_with_changelogs, total
            else:
                return issues_with_changelogs

        except Exception as e:
            logging_helper.send_to_agent_log_file(
                f'Exception encountered when attempting to get issue data. '
                f'start_at: {start_at}, end_at: {end_at}, batch_size: {batch_size}, error: {e}',
                level=logging.WARNING,
            )
            # DO NOT fail hard here. Attempt to shrink the batch size a few times (see blow)
            # and give up if we move the start_at cursor above the end_at marker
            if start_at > end_at:
                # Return empty results based on what's requested
                empty_issues: list[dict] = []
                if use_jql_enhanced_search and return_next_page_token:
                    if return_total:
                        return empty_issues, 0, None
                    else:
                        return empty_issues, None
                elif return_total:
                    return empty_issues, 0
                else:
                    return empty_issues
            # We have seen sporadic server-side flakiness here. Sometimes Jira Server (but not
            # Jira Cloud as far as we've seen) will return a 200 response with an empty JSON
            # object instead of a JSON object with an "issues" key, which results in the
            # `search_issues()` function in the Jira library throwing a KeyError.
            #
            # Sometimes both cloud and server will return a 5xx.
            #
            # In either case, reduce the maxResults parameter and try again, on the theory that
            # a smaller ask will prevent the server from choking.
            if changeable_batch_size > 0:
                changeable_batch_size = int(
                    changeable_batch_size / 2
                )  # This will eventually lead to a batch size of 0 ( int(1 / 2) == 0 )
                logging_helper.send_to_agent_log_file(
                    f"Caught {type(e)} from search_issues(), reducing batch size to {changeable_batch_size}",
                    level=logging.WARNING,
                )

                if changeable_batch_size <= 0:
                    # Might be a transient error I guess, or might happen every time we request this specific
                    # issue. Either way, seems fine to ignore it. If a), we'll be able to fetch it again the
                    # next time we perform issue metadata downloading. If b), we'll never fetch this issue, but
                    # what else can we do? -- the Jira API never seems to be able to provide it to us.
                    logging_helper.send_to_agent_log_file(
                        f"Caught {type(e)} from search_issues(), batch size is already 0, giving up on "
                        f"fetching this issue's metadata. Args: jql_query={jql_query}, start_at={start_at}",
                        level=logging.WARNING,
                    )
                    start_at += 1
                    changeable_batch_size = batch_size


def generate_jql_for_batch_of_ids(id_batch: list[str], pull_from: Optional[datetime] = None) -> str:
    """Generates a JQL to get a batch of IDs

    Args:
        id_batch (list[str]): A list of IDs
        pull_from (datetime): When provided, the datetime will be appended to the end of the JQL query. This ensures we don't download any issues before this pull from date. Defaults to None, meaning no pull_from filtering will be applied.

    Returns:
        str: A JQL of the following format: 'id in (1,2,3) [AND updated > yyyy-mm-dd] order by id asc'
    """
    try:
        jql = f'id in ({",".join(id_batch)})'
        if pull_from:
            jql = f'{jql} AND updated > {format_date_to_jql(pull_from)}'
        return f'{jql} order by id asc'
    except Exception as e:
        logger.error(f"Error generating JQL for batch of IDs: {id_batch}, got {e}")
        raise e


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def pull_jira_issues_by_jira_ids(
    jira_connection: JIRA,
    jira_ids: list[str] | set[str],
    num_parallel_threads: int,
    batch_size: int,
    expand_fields: Optional[list[str]] = [],
    include_fields: Optional[list[JiraFieldIdentifier]] = [],
    exclude_fields: Optional[list[JiraFieldIdentifier]] = [],
    hide_tqdm: Optional[bool] = False,
    adaptive_throttler: Optional[AdaptiveThrottler] = None,
    pull_from: Optional[datetime] = None,
    use_jql_enhanced_search: bool = False,
) -> Generator[dict[str, Any], None, None]:
    """Fetches Issues based on a set of Issue IDs that we want to pull.
    This function deals with all of the paging and concurrency stuff we
    want to do to optimize our JIRA Issue ingestion

    Args:
        jira_connection (JIRA): A JIRA Connection object
        jira_ids (list[str]): A list of JIRA IDs
        num_parallel_threads (int): The number of threads to use in the ThreadPoolExecutor object
        batch_size (int): The Batch Size that JIRA will limit us to
        expand_fields (Optional[list[str]], optional): A list of fields we want to expand. Defaults to [].
        include_fields (Optional[list[JiraFieldIdentifier]], optional): A list of fields we want to exclusively pull. Defaults to [].
        exclude_fields (Optional[list[JiraFieldIdentifier]], optional): A list of fields we want to exclude. Defaults to [].
        hide_tqdm (Optional[bool], optional): A flag to hide the tqdm progress bar. Defaults to False.
        adaptive_throttler (Optional[AdaptiveThrottler], optional): An adaptive throttler object to throttle requests.
        pull_from (Optional[datetime]): When provided, the datetime will be appended to the end of the JQL query. This ensures we don't download any issues before this pull from date. Defaults to None, meaning no pull_from filtering will be applied.
        use_jql_enhanced_search (bool, optional): Whether to use JQL Enhanced Search API (/search/jql) or legacy API (/search). Defaults to False.

    Returns:
        Generator[dict, None, None]: A generator of raw Issues, which should yield the number of jira_ids provided
    """
    encountered_issue_ids = set()
    if not jira_ids:
        return

    with ThreadPoolWithTqdm(
        desc=f"Pulling issue data for {len(jira_ids)} Jira Issue IDs (Thread Count: {num_parallel_threads})",
        total=len(jira_ids),
        max_workers=num_parallel_threads,
        hide_tqdm=hide_tqdm,
    ) as pool:
        for issue_batch in batch_iterable(jira_ids, batch_size=batch_size):
            jql_query = generate_jql_for_batch_of_ids(issue_batch, pull_from=pull_from)
            pool.submit(
                _download_issue_page,
                jira_connection=jira_connection,
                jql_query=jql_query,
                start_at=0,
                batch_size=batch_size,
                expand_fields=expand_fields,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                adaptive_throttler=adaptive_throttler,
                use_jql_enhanced_search=use_jql_enhanced_search,
            )

        for issue_batch in pool.get_results():
            for issue in issue_batch:
                issue_id = issue['id']
                if issue_id not in encountered_issue_ids:
                    encountered_issue_ids.add(issue_id)
                    yield issue


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def pull_all_jira_issues_by_date(
    jira_connection: JIRA,
    project_key_to_pull_from: dict[str, datetime],
    num_parallel_threads: int,
    batch_size: int,
    jql_project_batch_size: int,
    jql_filter: Optional[str] = None,
    expand_fields: list[str] = [],
    include_fields: list[JiraFieldIdentifier] = [],
    exclude_fields: list[JiraFieldIdentifier] = [],
    use_jql_enhanced_search: bool = False,
) -> Generator[dict, None, None]:
    """Fetch a list of IDs by searching for all issues in a given list of
    projects that have had their 'updated' field updated after the provided
    pull_from

    Args:
        jira_connection (JIRA): A Jira Connection object
        project_keys (list[str]): A list of project keys representing the projects we want to pull from
        pull_from (datetime): A 'pull_from' value, to pull issues that have their updated field as AFTER this argument
        num_parallel_threads (int): The number of thread we want to use in the ThreadPoolExecutor object
        batch_size (int): The batch size that JIRA is limiting us to
        jql_project_batch_size (int): The total number of projects to include in each JQL call
        jql_filter (Optional[str], optional): An optional JQL filter to apply to the query.
        expand_fields (Optional[list[str]], optional): A list of API fields that we want to expand. Defaults to [].
        include_fields (Optional[list[JiraFieldIdentifier]], optional): A list of fields we want to exclusively fetch. Defaults to [].
        exclude_fields (Optional[list[JiraFieldIdentifier]], optional): A list of fields we want to exclude. Defaults to [].

    Returns:
        list[dict]: A list of JIRA Issues that are within the requested projects that have been updated since the pull_from arg
    """
    # First, do a parallelized check across all projects to see
    # if they have issues or not
    project_issue_count_map = _get_all_project_issue_counts(
        jira_connection=jira_connection,
        project_key_to_pull_from=project_key_to_pull_from,
        num_parallel_threads=num_parallel_threads,
        jql_filter=jql_filter,
        use_jql_enhanced_search=use_jql_enhanced_search,
    )

    # Iterate across each project and fetch issue metadata based on
    # our date filtering
    total_expected_issues: int = sum([count for count in project_issue_count_map.values()])

    project_keys_with_issues_present = [
        project_key for project_key, count in project_issue_count_map.items() if count > 0
    ]

    if use_jql_enhanced_search:
        # Use dedicated JQL Enhanced Search implementation
        for issue in _pull_all_jira_issues_by_date_enhanced(
            jira_connection=jira_connection,
            project_key_to_pull_from=project_key_to_pull_from,
            project_keys_with_issues_present=project_keys_with_issues_present,
            project_issue_count_map=project_issue_count_map,
            batch_size=batch_size,
            jql_project_batch_size=jql_project_batch_size,
            jql_filter=jql_filter,
            expand_fields=expand_fields or [],
            include_fields=include_fields or [],
            exclude_fields=exclude_fields or [],
        ):
            yield issue
    else:
        # Legacy API can use threading with startAt pagination
        with ThreadPoolWithTqdm(
            desc=f"Pulling issue data across {len(project_issue_count_map)} projects by Date (Thread Count: {num_parallel_threads})",
            total=total_expected_issues,
            max_workers=num_parallel_threads,
        ) as pool:
            for project_key_batch in batch_iterable(
                project_keys_with_issues_present, batch_size=jql_project_batch_size
            ):
                count_for_projects_batch = sum(
                    [project_issue_count_map[pk] for pk in project_key_batch]
                )

                jql_query = generate_project_pull_from_bulk_jql(
                    project_keys=project_key_batch,
                    project_key_to_pull_from=project_key_to_pull_from,
                    jql_filter=jql_filter,
                )

                logging_helper.send_to_agent_log_file(
                    f'Attempting to query for {count_for_projects_batch} issues with batch size {batch_size} using legacy API: {jql_query}',
                    level=logging.INFO,
                )
                for start_at in range(0, count_for_projects_batch, batch_size):
                    pool.submit(
                        _download_issue_page,
                        jira_connection=jira_connection,
                        jql_query=jql_query,
                        start_at=start_at,
                        batch_size=batch_size,
                        expand_fields=expand_fields,
                        include_fields=include_fields,
                        exclude_fields=exclude_fields,
                        use_jql_enhanced_search=False,
                    )

                # Empty thread pool for each project, in attempt to keep
                # memory usage low in the threadpool
                for issue_batch in pool.get_results():
                    for issue in issue_batch:
                        yield issue


def _pull_all_jira_issues_by_date_enhanced(
    jira_connection: JIRA,
    project_key_to_pull_from: dict[str, datetime],
    project_keys_with_issues_present: list[str],
    project_issue_count_map: dict[str, int],
    batch_size: int,
    jql_project_batch_size: int,
    jql_filter: Optional[str],
    expand_fields: list[str],
    include_fields: list[JiraFieldIdentifier],
    exclude_fields: list[JiraFieldIdentifier],
) -> Generator[dict, None, None]:
    """
    JQL Enhanced Search implementation for pull_all_jira_issues_by_date.
    Handles sequential processing with nextPageToken pagination.

    Args:
        jira_connection (JIRA): A Jira Connection Object
        project_key_to_pull_from (dict[str, datetime]): Project keys mapped to their pull_from dates
        project_keys_with_issues_present (list[str]): List of project keys that have issues
        project_issue_count_map (dict[str, int]): Project keys mapped to their issue counts
        batch_size (int): The batch size for each API call
        jql_project_batch_size (int): Number of projects to include in each JQL query
        jql_filter (Optional[str]): Optional JQL filter to apply
        expand_fields (list[str]): Fields to expand
        include_fields (list[JiraFieldIdentifier]): Fields to include
        exclude_fields (list[JiraFieldIdentifier]): Fields to exclude

    Yields:
        dict: Individual issue dictionaries
    """
    # JQL Enhanced Search requires sequential processing due to nextPageToken pagination
    for project_key_batch in batch_iterable(
        project_keys_with_issues_present, batch_size=jql_project_batch_size
    ):
        jql_query = generate_project_pull_from_bulk_jql(
            project_keys=project_key_batch,
            project_key_to_pull_from=project_key_to_pull_from,
            jql_filter=jql_filter,
        )

        count_for_projects_batch = sum([project_issue_count_map[pk] for pk in project_key_batch])

        logging_helper.send_to_agent_log_file(
            f'Attempting to query for {count_for_projects_batch} issues with batch size {batch_size} using JQL Enhanced Search: {jql_query}',
            level=logging.INFO,
        )

        # Sequential pagination with nextPageToken for this project batch
        next_page_token = None

        while True:
            # Call _download_issue_page with return_next_page_token=True
            page_result = _download_issue_page(
                jira_connection=jira_connection,
                jql_query=jql_query,
                start_at=0,  # Not used for JQL Enhanced Search
                batch_size=batch_size,
                expand_fields=expand_fields,
                include_fields=include_fields,
                exclude_fields=exclude_fields,
                use_jql_enhanced_search=True,
                next_page_token=next_page_token,
                return_next_page_token=True,
            )
            issues, next_token = page_result  # type: ignore

            # Yield all issues from this page
            for issue in issues:
                yield issue

            # Check if there are more pages
            if not next_token or len(issues) == 0:
                break

            next_page_token = next_token


def get_fields_spec(include_fields: list[str] = [], exclude_fields: list[str] = []) -> list[str]:
    """A helper function to get a JIRA API friendly string for filtering against fields

    Args:
        include_fields (list[str], optional): A list of fields by their Field ID that we want to exclusively use. Defaults to [].
        exclude_fields (list[str], optional): A list of fields by their Field ID that we want to exclude. Defaults to [].

    Returns:
        list[str]: A list of fields to pull. If include_fields and exclude_fields are both empty,
        we will return ['*all'] (return all fields)
    """
    # This can occasionally get passed in as a set, so make sure that
    # we're casting to a `list`, so that we can `extend`.
    field_spec = list(include_fields) or ["*all"]
    field_spec.extend(f"-{field}" for field in exclude_fields)
    return field_spec


def _convert_datetime_to_worklog_timestamp(since: datetime) -> int:
    """Convert a datetime to a timestamp value, to be used for worklog querying

    Args:
        since (datetime): A datetime object

    Returns:
        int: An int, representing a unix timestamp that JIRA will accept on the worklogs API endpoint
    """
    try:
        timestamp = since.timestamp()
    except (AttributeError, ValueError):
        timestamp = 0
    updated_since = int(timestamp * 1000)
    return updated_since


# Returns a dict with two items: 'existing' gives a list of all worklogs
# that currently exist; 'deleted' gives the list of worklogs that
# existed at some point previously, but have since been deleted
@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit(logger)
def download_worklogs(
    jira_connection: JIRA, issue_ids: list[str], since: datetime
) -> dict[str, Union[list[dict], list[str]]]:
    """Returns a dict with two items: 'existing' give a list of all worklogs that currently
    exist; 'deleted' gives the list of worklog IDs that existed at some point previously, but
    have since been deleted

    Args:
        jira_connection (JIRA): A jira connection object
        issue_ids (list[str]): A list of issue IDs we are concerned with
        since (datetime): A datetime to 'pull from'

    Returns:
        dict[str, list]: Schema: {'updated': [...], 'deleted': [...]}
    """
    logger.info("Downloading Jira Worklogs...")
    updated: list[dict] = []
    deleted_ids: list[str] = []
    since_timestamp = _convert_datetime_to_worklog_timestamp(since)
    updated_since = since_timestamp
    deleted_since = since_timestamp

    logger.info("Fetching updated worklogs")
    while True:
        worklog_ids_json = retry_for_status(
            jira_connection._get_json,
            "worklog/updated",
            params={"since": updated_since},
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
        updated_worklog_ids = [v["worklogId"] for v in worklog_ids_json["values"]]

        # The provided JIRA library does not support a 'worklog list' wrapper function,
        # so we have to manually hit the worklog/list endpoint ourselves
        resp: Response = retry_for_status(
            jira_connection._session.post,
            url=jira_connection._get_url("worklog/list"),
            data=json.dumps({"ids": updated_worklog_ids}),
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
        try:
            worklog_list_json = resp.json()
        except ValueError:
            logger.error(f"Couldn't parse JIRA response as JSON: {resp.text}")
            raise

        updated.extend([wl for wl in worklog_list_json if int(wl["issueId"]) in issue_ids])
        if worklog_ids_json["lastPage"]:
            break
        updated_since = worklog_ids_json["until"]
    logger.info("Done fetching updated worklogs")

    logger.info("Fetching deleted worklogs")
    while True:
        try:
            worklog_ids_json = retry_for_status(
                jira_connection._get_json,
                "worklog/deleted",
                params={"since": deleted_since},
                statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            )

            deleted_ids.extend([v["worklogId"] for v in worklog_ids_json["values"]])

            if worklog_ids_json["lastPage"]:
                break
            deleted_since = worklog_ids_json["until"]
        except Exception as e:
            # Getting deleted worklogs is wildly under performant, for some Jira Server instances.
            # Most people, however, don't seem to need deleted work logs at all. Agent, for example,
            # has never ingest deleted work logs since it's inception. I think it's pretty safe to
            # not ingest delete work logs if we encounter a connection error here (which typically means)
            #
            # Jira ticket to improve deleted worklogs via the API: https://jira.atlassian.com/browse/JRASERVER-66180
            # Note that the submitted has given up on them fixing it, and posted work arounds for how to
            # ingest this data directly
            #
            logging_helper.send_to_agent_log_file(
                f'Error encountered when fetching deleted worklogs. Error message: {e}.',
                level=logging.ERROR,
                exc_info=True,
            )
            logging_helper.send_to_agent_log_file(
                f'This error WILL NOT be raised', level=logging.ERROR
            )
            break
    logger.info("Done fetching deleted worklogs")

    logger.info(
        f"Done downloading Worklogs! Found {len(updated)} worklogs and {len(deleted_ids)} deleted worklogs"
    )

    return {"existing": updated, "deleted": deleted_ids}


@jelly_trace
@diagnostics.capture_timing()
@logging_helper.log_entry_exit()
def download_statuses(jira_connection: JIRA) -> list[dict]:
    """Fetches a list of Jira Statuses returned from the Jira status API endpoint

    Args:
        jira_connection (JIRA): A Jira connection, through their jira Python module

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains a 'status_id' key and a 'raw_json' field
    """
    logger.info("Downloading Jira Statuses...")
    result = [
        {"status_id": status.id, "raw_json": status.raw}
        for status in retry_for_status(
            jira_connection.statuses,
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
        )
    ]
    logger.info(f"Done downloading Jira Statuses! Found {len(result)}")
    return result


def has_read_permissions(jira_connection: JIRA, project: Project) -> bool:
    """Given a project we know of, can we actually access it
        Some projects we have local no longer exist on remote or we no longer have access to
        other projects even come back from the api request (JIRA.projects()) but appear to be inaccessible
    Args:
        jira_connection (JIRA): A JIRA connection object
        project (JIRA.project): A JIRA project object
    Returns:
        bool: True if we have access to the project, False if we do not
    """
    if hasattr(project, 'isPrivate'):
        return not project.isPrivate
    project_perms_response = retry_for_status(
        jira_connection.my_permissions, project, statuses_to_retry=PROJECT_HTTP_CODES_TO_RETRY_ON
    )
    has_perms: bool = project_perms_response['permissions']['BROWSE']['havePermission']
    return has_perms


def _post_raw_result_jql_enhanced(
    jira_connection: JIRA,
    jql_query: str,
    fields: list[str],
    expand: list[str],
    max_results: int,
    next_page_token: Optional[str] = None,
) -> dict[str, Any]:
    """
    Helper function for sending a POST call to the JQL Enhanced Search API.
    Uses the new /search/jql endpoint with nextPageToken-based pagination.

    Args:
        jira_connection (JIRA): A Jira Connection Object
        jql_query (str): A JQL query to hit the endpoint with
        fields (list[str]): The fields to get back
        expand (list[str]): The fields to expand
        max_results (int): The batch size to request (max 5,000 for ID-only queries)
        next_page_token (Optional[str]): Token for pagination, None for first page

    Returns:
        dict: A JSON response from the JQL Enhanced Search API
    """
    try:
        payload = {
            'jql': jql_query,
            'fields': fields,
            'maxResults': max_results,
        }

        # Only include expand if it has values - convert list to comma-delimited string
        if expand:
            payload['expand'] = ','.join(expand)

        if next_page_token:
            payload['nextPageToken'] = next_page_token

        url = jira_connection._get_url('search/jql')
        response: Response = retry_for_status(
            jira_connection._session.post,
            url=url,
            json=payload,
            statuses_to_retry=JIRA_STATUSES_TO_RETRY,
            max_retries_for_retry_for_status=3,
        )
    except Exception as e:
        logger.error(
            f"Exception in _post_raw_result_jql_enhanced before API call: {type(e).__name__}: {e}"
        )
        raise

    if response.status_code >= 400:
        logger.error(f"JQL Enhanced Search API response - Error text: {response.text}")

    result: dict[str, Any] = response.json()
    return result


def _get_issue_count_with_jql_enhanced_search(jira_connection: JIRA, jql_query: str) -> int:
    """
    Get issue count using JQL Enhanced Search API with approximate count + fallback.

    Primary strategy: Use /search/approximate-count endpoint for fast estimates
    Fallback strategy: Use pagination-based exact counting when approximate count fails

    Args:
        jira_connection (JIRA): A Jira Connection Object
        jql_query (str): A JQL query to count issues for

    Returns:
        int: The approximate or exact number of issues matching the JQL query
    """
    try:
        # Try approximate count endpoint first - use POST with JSON payload
        payload = {'jql': jql_query}
        response = jira_connection._session.post(
            url=jira_connection._get_url('search/approximate-count'), json=payload
        )

        if 200 <= response.status_code < 300:
            result: dict[str, Any] = response.json()
            count: int = result.get('approximateCount', 0)
            return count

    except Exception as e:
        logger.debug(f"Approximate count failed, falling back to exact count: {e}")

    # Fallback to exact count via pagination
    return _get_exact_count_via_pagination(jira_connection, jql_query)


def _get_batch_size_with_jql_enhanced_search(
    fields: Iterable[str], optimistic_batch_size: int
) -> int:
    """Get batch size for JQL Enhanced Search API."""
    fields_list = list(fields)
    if fields_list == ['id', 'key'] or fields_list == ['id']:
        return 5000  # ID-only queries can use higher limit
    else:
        return min(optimistic_batch_size, 100)  # Full issue queries use lower limit


def _get_exact_count_via_pagination(jira_connection: JIRA, jql_query: str) -> int:
    """Get exact issue count by paginating through all results with ID-only queries."""

    total_count = 0
    next_page_token = None

    # Get appropriate batch size for ID-only queries using JQL Enhanced Search
    batch_size = _get_batch_size_with_jql_enhanced_search(['id'], 5000)

    logger.info(f"Getting exact count via pagination for JQL: {jql_query}")

    while True:
        # Use the encapsulated API call function
        response_data = _post_raw_result_jql_enhanced(
            jira_connection=jira_connection,
            jql_query=jql_query,
            fields=['id'],  # Minimal fields for fastest response
            expand=[],
            max_results=batch_size,
            next_page_token=next_page_token,
        )

        # Count issues in this batch
        issues = response_data.get('issues', [])
        total_count += len(issues)

        # Check for next page
        next_page_token = response_data.get('nextPageToken')
        if not next_page_token or len(issues) == 0:
            break

        logger.debug(f"Counted {total_count} issues so far, continuing pagination")

    logger.info(f"Exact count via pagination: {total_count} issues")
    return total_count
