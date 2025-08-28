import ast
import dataclasses
import functools
import json
import logging
import queue
import threading
import time
from collections import defaultdict
from math import ceil
from typing import Any, NamedTuple, Optional, Union

import requests
from opentelemetry import baggage, context, trace

from jf_ingest import logging_helper
from jf_ingest.adaptive_throttler import AdaptiveThrottler
from jf_ingest.config import IngestionConfig
from jf_ingest.jf_jira import (
    get_jira_connection,
    get_jira_search_batch_size,
    pull_jira_issues_by_jira_ids,
)
from jf_ingest.jf_jira.utils import JiraFieldIdentifier, get_jellyfish_jira_issues_count
from jf_ingest.telemetry.tracing import jelly_trace, record_span
from jf_ingest.utils import (
    ThreadPoolExecutorWithLogging,
    init_jf_ingest_run,
    retry_for_status,
    tqdm_to_logger,
)

JELLYFISH_CUSTOM_FIELDS_API_LIMIT = 1_000
JELLYFISH_API_TIMEOUT = 600.0
JELLYFISH_CUSTOM_FIELDS_ENDPOINT = 'endpoints/jira/issues/custom-fields'
JELLYFISH_MARK_FOR_REDOWNLOAD_ENDPOINT = 'endpoints/ingest/jira/issues/mark-for-redownload'
MAX_ISSUES_TO_MARK_FOR_REDOWNLOAD = 400_000

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class JCFVDBData:
    field_id: int
    field_key: str
    field_type: str
    value: str | dict | list


@dataclasses.dataclass
class IssueJCFVDBData:
    issue_jira_id: int
    custom_field_values: list[JCFVDBData]


@dataclasses.dataclass
class JCFVUpdate:
    jira_issue_id: str
    field_id: str
    field_key: str
    field_type: str
    value_old: Optional[dict]
    value_new: Optional[dict]


@functools.lru_cache(maxsize=4096)
def _literal_eval_memoized(value: str) -> dict | list:
    """ast.literal_eval is rather slow, and we expect a lot of duplicate values; memoize it."""
    le: dict = ast.literal_eval(value)
    return le


@functools.lru_cache(maxsize=4096)
def _json_loads_memoized(value: str) -> dict | list:
    """improve performance of JSON loads by memoizing the results."""
    d: dict = json.loads(value)
    return d


def attempt_load_json_or_literal(value: str) -> list[Any] | dict[str, Any] | str:
    """
    Attempt to load a string as JSON or a literal. Used to handle the case where we
    get a dictionary string back that's out of order.

    Args:
        value (str): The string to attempt to load.

    Raises:
    """
    if isinstance(value, str):
        if value.startswith('{') or value.startswith('['):
            try:
                return _json_loads_memoized(value)
            except Exception:
                try:
                    return _literal_eval_memoized(value)
                except Exception:
                    pass
    return value


@jelly_trace
def _annotate_results_from_jellyfish(data: dict) -> dict[str, IssueJCFVDBData]:
    """
    Unpacks the results from Jellyfish into a dict[str, IssueJCFVDBData] - where `str` is the jira_issue_id.
    Typically, the value being sent over is JSON, so we need to handle that here.
    """
    resp: dict[str, IssueJCFVDBData] = {}
    for issue in data['issues']:
        resp[str(issue['issue_jira_id'])] = IssueJCFVDBData(
            issue_jira_id=issue['issue_jira_id'], custom_field_values=[]
        )
        for jcfv_db_data in issue['custom_field_values']:
            value = attempt_load_json_or_literal(jcfv_db_data['value'])
            resp[str(issue['issue_jira_id'])].custom_field_values.append(
                JCFVDBData(
                    field_id=jcfv_db_data['field_id'],
                    field_key=jcfv_db_data['field_key'],
                    field_type=jcfv_db_data['field_type'],
                    value=value,
                )
            )
    return resp


def _fetch_custom_fields_from_jellyfish(
    base_url: str, headers: dict[str, str], cursor: int, limit: int
) -> requests.Response:
    try:
        response = requests.get(
            f"{base_url}/{JELLYFISH_CUSTOM_FIELDS_ENDPOINT}?cursor={cursor}&limit={limit}",
            headers=headers,
            timeout=JELLYFISH_API_TIMEOUT,
        )
        response.raise_for_status()
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Error when attempting to pull custom fields from Jellyfish',
            exc_info=True,
            level=logging.ERROR,
        )
        raise e

    return response


@jelly_trace
def _retrieve_custom_fields_from_jellyfish(
    ingest_config: IngestionConfig,
    output_queue: queue.Queue,
    max_issues_to_process: Optional[int] = None,
    limit: int = JELLYFISH_CUSTOM_FIELDS_API_LIMIT,
    exit_event: threading.Event = threading.Event(),
) -> None:
    """
    Retrieve all custom fields from Jellyfish.
    Note: 1K is the API hard limit.
    """
    if max_issues_to_process == 0:
        return

    cursor = 0
    total_fetched_issues = 0
    limit = min((limit, max_issues_to_process)) if max_issues_to_process else limit

    base_url = ingest_config.jellyfish_api_base
    headers = {"Jellyfish-API-Token": ingest_config.jellyfish_api_token}

    while True:
        if exit_event.is_set():
            while not output_queue.empty():
                try:
                    output_queue.get_nowait()
                except queue.Empty:
                    break

            return None

        st = time.perf_counter()

        # Sometimes we'll see 504 from Jellyfish (e.g. if pulling a large amount of data) so we'll retry for status here
        r = retry_for_status(_fetch_custom_fields_from_jellyfish, base_url, headers, cursor, limit)
        data = r.json()

        # Catch if the API changes the maximum allowed limit compared to what was provided
        limit = min((limit, data['max_records']))

        # If we get 0 for cursor, there is no more data to fetch, otherwise we fetched the limit
        cursor = int(data['next_cursor'])

        if not cursor:
            fetched_count = len(data['issues'])
        else:
            fetched_count = limit
        total_fetched_issues += fetched_count

        # We should only queue responses that have data.
        if fetched_count:
            # Annotate data to be put into the output queue.
            output_queue.put(_annotate_results_from_jellyfish(data))

        if not data['issues']:
            logging_helper.send_to_agent_log_file(
                f'No more issues found when attempting to pull custom fields from Jellyfish. {total_fetched_issues} issues retrieved.',
            )
            break

        if max_issues_to_process is not None and total_fetched_issues >= max_issues_to_process:
            logging_helper.send_to_agent_log_file(
                f'Finished pulling custom fields from Jellyfish - reached max_issues_to_process. {total_fetched_issues} issues retrieved.'
            )
            break

        if not cursor:
            logging_helper.send_to_agent_log_file(
                f'Finished pulling custom fields from Jellyfish - reached end of data. {total_fetched_issues} issues retrieved.'
            )
            break

        logging_helper.send_to_agent_log_file(
            f'Pulled {total_fetched_issues} issues from Jellyfish, {fetched_count} records in {time.perf_counter() - st:.2f}s,'
            f' continuing...',
            level=logging.DEBUG,
        )


class JCFVUpdateFullPayload(NamedTuple):
    missing_from_db_jcfv: list[JCFVUpdate]
    missing_from_jira_jcfv: list[JCFVUpdate]
    out_of_sync_jcfv: list[JCFVUpdate]


def _send_marked_for_redownload_to_jellyfish(base_url, headers, data) -> requests.Response:
    try:
        response = requests.post(
            f"{base_url}/{JELLYFISH_MARK_FOR_REDOWNLOAD_ENDPOINT}",
            headers=headers,
            json=data,
            timeout=JELLYFISH_API_TIMEOUT,
        )
        response.raise_for_status()
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Error when attempting to mark Jira issues for redownload via Jellyfish',
            exc_info=True,
            level=logging.ERROR,
        )
        raise e

    return response


def make_hash(o: Union[set, list, tuple, dict, Any]) -> Union[int, tuple, None]:
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """

    if isinstance(o, (set, tuple, list)):
        return tuple(sorted([make_hash(e) for e in o]))

    elif not isinstance(o, dict):
        return hash(o)
    o_new = dict()
    for k, v in o.items():
        o_new[k] = make_hash(v)

    return hash(tuple(frozenset(sorted(o_new.items()))))


@jelly_trace
def identify_custom_field_mismatches(
    ingest_config: IngestionConfig,
    use_jql_enhanced_search: bool = False,
    nthreads: int = 10,
    max_issues_to_process: Optional[int] = None,
    mark_for_redownload: Optional[int] = None,
    use_throttler: bool = False,
) -> JCFVUpdateFullPayload:
    """
    At a high level:
    - Get all of the fields that are used to define critical components in Jellyfish. We use a Jellyfish
        endpoint to get this data, in order to support using this sync path from both the agent and internally.
    - Create one thread that retrieves (issue.id, issue.jira_id, *custom_field_values) of all issues
        and puts that into a queue. This is done in a separate thread to allow us to download issues from Jira
        in parallel, as downloading issues from Jira is the primary bottleneck.
    - In our main thread, read from the queue that's being stuffed by the _retrieve_custom_fields_from_jellyfish
        thread, and query Jira to get up-to-date issue data. If there is any data mismatch in custom
        fields, save that into an "updates" NamedTuple, which we can POST to Jellyfish to update the data.

    :param ingest_config: IngestionConfig object
    :param use_jql_enhanced_search: Whether to use JQL Enhanced Search API (/search/jql) instead of legacy API (/search)
    :param nthreads: Number of threads to use for downloading issues from Jira
    :param max_issues_to_process: Maximum number of issues to process. If None, all issues will be processed.
    :param mark_for_redownload: Send jira issue ids to mark them for redownload in Jellyfish.
    :param use_throttler: Whether to use the adaptive throttler for Jira API requests.
    :return: Tuple of (missing_from_db_jcfv, missing_from_jira_jcfv, out_of_sync_jcfv)
    """
    init_jf_ingest_run(ingestion_config=ingest_config)
    logger.info(f'Attempting to identify custom field mismatches between Jira and Jellyfish')
    total_issue_count = get_jellyfish_jira_issues_count(
        jellyfish_api_base_url=ingest_config.jellyfish_api_base,
        jellyfish_api_token=ingest_config.jellyfish_api_token,
    )
    output_queue: queue.Queue = queue.Queue()
    exit_event = threading.Event()

    # Use ThreadPoolExecutor here so that we can capture
    # any exceptions raised within the thread.
    executor = ThreadPoolExecutorWithLogging(max_workers=1)
    retrieval_thread = executor.submit(
        _retrieve_custom_fields_from_jellyfish,
        ingest_config,
        output_queue,
        max_issues_to_process=max_issues_to_process,
        limit=JELLYFISH_CUSTOM_FIELDS_API_LIMIT,
        exit_event=exit_event,
    )

    # We _are_ downloading issues but not doing a full download, so for_download=False
    # is fine here and is faster.
    if not (jira_config := ingest_config.jira_config):
        raise Exception(f'Ingest config was provided without a Jira Configuration!')
    jira_connection = get_jira_connection(
        config=jira_config, use_jql_enhanced_search=use_jql_enhanced_search
    )

    # We store the custom field values that are missing from the DB, missing from Jira,
    # and out of sync in separate lists - this allows for easier processing on the
    # update side.
    update_payload = JCFVUpdateFullPayload([], [], [])

    # Use the adaptive throttler for Jira server/dc requests if enabled
    jira_request_throttler = (
        AdaptiveThrottler(logging_extra={'company_slug': ingest_config.company_slug})
        if use_throttler
        else None
    )

    st = time.perf_counter()
    total_issues_scanned = 0
    progress_bar = tqdm_to_logger(
        desc=f'Detecting changes to custom fields in Jira...', total=total_issue_count
    )
    while retrieval_thread.running() or not output_queue.empty():
        if exit_event.is_set():
            break

        try:
            db_issue_batch: dict[str, IssueJCFVDBData] = output_queue.get(timeout=60.0)
        except queue.Empty:
            logging_helper.send_to_agent_log_file(
                'Didn\'t get any issues from the queue in 60 seconds, retrying...'
            )
            continue

        total_issues_scanned += len(db_issue_batch)

        # Get all the field keys from the DB data, so we can request them from Jira.
        field_map: dict[str, tuple[int, str, str]] = {}
        for issue in db_issue_batch.values():
            for jcfv in issue.custom_field_values:
                field_map[jcfv.field_key] = (jcfv.field_id, jcfv.field_key, jcfv.field_type)

        # If we don't have any fields to query, we can skip the Jira query.
        if not field_map:
            continue

        # Likely won't change the batch size vs. doing this without "fields", but
        # it's possible we'll be able to use a larger batch size if querying a subset
        # of fields.
        batch_size = get_jira_search_batch_size(
            jira_connection,
            fields=['key'] + list(field_map.keys()),
            use_jql_enhanced_search=use_jql_enhanced_search,
        )

        # Note: this is parallelized and returns a generator, so we're
        # able to process issues while downloading from Jira simultaneously.
        jira_ids_to_search = list(db_issue_batch.keys())
        include_fields = [
            JiraFieldIdentifier(jira_field_id=key, jira_field_name='')
            for key in ['key'] + list(field_map.keys())
        ]
        with record_span('jira_issues_download'):
            jira_issue_batch = pull_jira_issues_by_jira_ids(
                jira_connection=jira_connection,
                jira_ids=jira_ids_to_search,
                num_parallel_threads=nthreads,
                batch_size=batch_size,
                include_fields=include_fields,
                hide_tqdm=True,
                adaptive_throttler=jira_request_throttler,
                use_jql_enhanced_search=use_jql_enhanced_search,
            )

        # Now we need to compare the custom field values from the DB with the actual issue data from Jira.
        tracer = trace.get_tracer(__name__)
        compare_issues_to_db_span = tracer.start_span(name='compare_issues_to_db')
        for issue_jira in jira_issue_batch:
            issue_db = db_issue_batch[str(issue_jira['id'])]
            jcfv_db_dict = {jcfv.field_key: jcfv for jcfv in issue_db.custom_field_values}

            for field_id, field_key, field_type in field_map.values():
                # Attempt to get the custom field value from the DB.
                # This may not be present, in the case that the field was
                # added to the issue, but we haven't yet pulled the data.
                db_value = getattr(jcfv_db_dict.get(field_key), 'value', None)

                # Occasionally, an issue may not have any of the fields we
                # requested, (e.g. if we're looking for just one field which is
                # no longer present on the issue present) so we need to handle this case.
                jira_value = issue_jira.get('fields', {}).get(field_key, None)
                hash_db_value = make_hash(db_value)
                hash_jira_value = make_hash(jira_value)
                if hash_db_value != hash_jira_value:
                    if db_value is None:
                        list_to_append = update_payload.missing_from_db_jcfv
                    elif jira_value is None:
                        list_to_append = update_payload.missing_from_jira_jcfv
                    else:
                        list_to_append = update_payload.out_of_sync_jcfv
                    list_to_append.append(
                        JCFVUpdate(
                            field_id=str(field_id),
                            field_key=field_key,
                            field_type=field_type,
                            jira_issue_id=str(issue_db.issue_jira_id),
                            value_old=db_value,
                            value_new=jira_value,
                        )
                    )
        compare_issues_to_db_span.end()

        total_fields_out_of_sync = sum(map(len, update_payload))
        logging_helper.send_to_agent_log_file(
            f'Downloaded {total_issues_scanned} issues from Jira. '
            f'{total_fields_out_of_sync} out of sync field values found '
            f'so far in {time.perf_counter() - st} seconds.'
        )
        st = time.perf_counter()
        progress_bar.update(len(jira_ids_to_search))

        if total_fields_out_of_sync >= MAX_ISSUES_TO_MARK_FOR_REDOWNLOAD:
            logging_helper.send_to_agent_log_file(
                f'Exceeded the maximum number of issues to mark for redownload. Exiting early. '
                f'{total_fields_out_of_sync} out of sync field values found in total. '
                f'Max issues to mark for redownload: {MAX_ISSUES_TO_MARK_FOR_REDOWNLOAD}'
            )
            exit_event.set()

    # Run here in case we get no issues back from Jellyfish
    total_fields_out_of_sync = sum(map(len, update_payload))
    logging_helper.send_to_agent_log_file(
        f'Finished processing all issues from the DB. {total_fields_out_of_sync} '
        f'out of sync field values found in total.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.out_of_sync_jcfv)} custom field values to update.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.missing_from_jira_jcfv)} custom field values to delete.'
    )
    logging_helper.send_to_agent_log_file(
        f'{len(update_payload.missing_from_db_jcfv)} custom field values to insert.'
    )
    logging_helper.send_to_agent_log_file(f'{total_issues_scanned} issues scanned in total.')

    # Retrieval thread is already finished, as guaranteed by the while loop above.
    # We can safely call result() here, which will raise any exceptions we might have seen.
    retrieval_thread.result()

    # Logging
    update_counts: defaultdict[Any, int] = defaultdict(int)
    for update in (
        update_payload.out_of_sync_jcfv
        + update_payload.missing_from_db_jcfv
        + update_payload.missing_from_jira_jcfv
    ):
        update_counts[f'{update.value_old} -> {update.value_new}'] += 1
    for value_change, update_count in sorted(
        update_counts.items(), key=lambda x: x[1], reverse=True
    ):
        if value_change.startswith('None -> '):
            prefix = 'INSERT'
        elif value_change.endswith(' -> None'):
            prefix = 'DELETE'
        else:
            prefix = 'UPDATE'
        logging_helper.send_to_agent_log_file(f'{update_count: >6d} | {prefix} | {value_change }')

    if mark_for_redownload:
        base_url = ingest_config.jellyfish_api_base
        headers = {"Jellyfish-API-Token": ingest_config.jellyfish_api_token}

        # These need to be cast to strings, since the endpoint only accepts issue ids as string values
        missing_db_ids = [str(jcfv.jira_issue_id) for jcfv in update_payload.missing_from_db_jcfv]
        missing_jira_ids = [
            str(jcfv.jira_issue_id) for jcfv in update_payload.missing_from_jira_jcfv
        ]
        missing_out_of_sync_ids = [
            str(jcfv.jira_issue_id) for jcfv in update_payload.out_of_sync_jcfv
        ]
        all_ids = set(missing_db_ids + missing_jira_ids + missing_out_of_sync_ids)

        if len(all_ids) >= MAX_ISSUES_TO_MARK_FOR_REDOWNLOAD:
            all_ids = set(list(all_ids)[:MAX_ISSUES_TO_MARK_FOR_REDOWNLOAD])

        if all_ids:
            logging_helper.send_to_agent_log_file(
                f'Submitting {len(all_ids)} issue IDs to Jellyfish that were marked for redownload'
            )

            batch_size = 10_000
            total_batches = ceil(len(all_ids) / batch_size)
            id_list = list(all_ids)

            for i in range(total_batches):
                end_idx = min((i + 1) * batch_size, len(all_ids))
                data = {'issue_ids': id_list[i * batch_size : end_idx]}
                retry_for_status(_send_marked_for_redownload_to_jellyfish, base_url, headers, data)
                logging_helper.send_to_agent_log_file(
                    f'Batch {i} of {total_batches} submitted for redownload'
                )

            logging_helper.send_to_agent_log_file(
                f'Done submitting issues for repair. {len(all_ids)} issues were marked for redownload'
            )
        else:
            logging_helper.send_to_agent_log_file(
                'No Jira Issues were marked as needing their custom fields repaired'
            )

    return update_payload
