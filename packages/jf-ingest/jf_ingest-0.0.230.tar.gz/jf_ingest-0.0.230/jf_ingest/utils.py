import contextvars
import dataclasses
import hashlib
import inspect
import io
import json
import logging
import re
import sys
import time
import traceback
from collections import namedtuple
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime
from enum import Enum
from types import TracebackType
from typing import Any, Callable, Generator, Iterable, Optional, Type, cast

import gitlab
import requests
import urllib3
from dateutil import parser as date_parser
from jira.exceptions import JIRAError
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar, cookiejar_from_dict
from tqdm import tqdm
from urllib3 import Retry

from jf_ingest import logging_helper
from jf_ingest.telemetry.metrics import JellyCounter

RETRY_FOR_STATUS_CALL_COUNTER: Optional[JellyCounter] = None


def setup_retry_counter() -> JellyCounter:
    return JellyCounter(
        name="jf_ingest_retry_for_status",
        description="Total number of calls attempted by retry_for_status, includes retry and non retry events",
    )


logger = logging.getLogger(__name__)

# Exponent base of 4 gives more reasonable
# max timeout of 4m16 rather than 10m25s for
# 5 retries
RETRY_EXPONENT_BASE = 4
DEFAULT_HTTP_CODES_TO_RETRY_ON = (429, 500, 502, 503, 504)

# For some Jira Servers, we can get fed a 401 error that is actually
# transient and totally retryable. Although retrying on all 401s will
# slightly slowdown raising actual authentication errors, the retry
# logic here is worth it. Gavin, December 2024
JIRA_STATUSES_TO_RETRY = tuple(list(DEFAULT_HTTP_CODES_TO_RETRY_ON) + [401])
# 500 errors are ignorable, and typically mean that the board is not configured for sprints.
# We are safe to log and ignore 500 level errors
JIRA_SPRINT_ERRORS_TO_RETRY = tuple(
    [status_code for status_code in JIRA_STATUSES_TO_RETRY if status_code != 500]
)
GITLAB_STATUSES_TO_RETRY = tuple(
    list(DEFAULT_HTTP_CODES_TO_RETRY_ON) + [522]
)  # We can get these transient Cloudflare Timeouts, attempt a retry

# There appears to be intermittent 404s that get thrown for versions and components.
# When we retry, the 404 goes away.
# NOTE - elheureux 2024-11-01: Adding 500 to the list of codes to retry on, as we are seeing
# intermittent 500 internal server errors when trying to access project components
# Additional context: OJ-39786
PROJECT_HTTP_CODES_TO_RETRY_ON = tuple(list(JIRA_STATUSES_TO_RETRY) + [404])

DEFAULT_EXCEPTIONS_TO_RETRY_ON = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ChunkedEncodingError,
    urllib3.exceptions.ConnectTimeoutError,
    urllib3.exceptions.ProtocolError,
)


class GitLabGidObjectMapping(Enum):
    PROJECT = 'Project'
    MERGE_REQUEST = 'MergeRequest'
    USER = 'User'
    GROUP = 'Group'


class RetryLimitExceeded(Exception):
    pass


class StrDefaultEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return str(o)


class ReauthSession(requests.Session):
    """
    A requests session that will re-authenticate on 401s
    """

    # Redefining this for mypy to get type. This is identical to `requests.Session`.
    cookies: RequestsCookieJar = cookiejar_from_dict({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def request(self, method, url, **kwargs) -> requests.Response:
        """
        Run a request, and if we get a 401, re-authenticate and try again.
        @:param: method: The HTTP method to use
        @:param: url: The URL to request
        @:param: kwargs: Any additional kwargs to pass to the request
        (a reauth session is usually instantiated with just ReauthSession(**kwargs))
        @:return: The response object from calling request()
        """
        # If we get HTTP 401, re-authenticate and try again
        response = super().request(method, url, **kwargs)
        if response.status_code == 401:
            # Use print instead of logger.log, as URL could be considered sensitive data
            logger.warn(f"Received 401 for the request [{method}] {url} - resetting client session")

            # Clear cookies and re-auth
            self.cookies.clear()
            response = super().request(method, url, **kwargs)
            self.cookies = response.cookies
        return response


def get_attribute(object, property, default=None):
    """
    Obtain a class attribute safely
    """
    try:
        value = getattr(object, property)
        return value if value else default
    except AttributeError:
        return default


def retry_session(**kwargs) -> requests.Session:
    """
    Obtains a requests session with retry settings.
    :return: session: Session
    """

    session = ReauthSession(**kwargs)

    retries = 3
    backoff_factor = 0.5
    status_forcelist = (500, 502, 503, 504, 104)

    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def get_wait_time(e: Optional[Exception], retries: int) -> int:
    """
    This function attempts to standardize determination of a wait time on a retryable failure.
    If the exception's response included a Retry-After header, respect it.
    If it does not, we do an exponential backoff - 1s, 4s, 16s, 64s, 256s.

    A possible future addition would be to add a jitter factor.
    This is a fairly standard practice but not clearly required for our situation.
    """
    # getattr with a default works on _any_ object, even None.
    # We expect that almost always e will be a JIRAError or a RequestException, so we will have a
    # response and it will have headers.
    # So I'm choosing to use the getattr call to handle the valid but infrequent possibility
    # that it may not (None or another Exception type that doesn't have a response), rather tha
    # preemptively checking.
    response = getattr(e, "response", None)
    headers = getattr(response, "headers", {})
    retry_after = headers.get("Retry-After")

    # Normalize retry after if it is a string
    if isinstance(retry_after, str) and retry_after.isnumeric():
        retry_after = int(retry_after)
    # Don't do anything if we have a valid int for retry after
    elif isinstance(retry_after, int):
        pass
    else:
        # Null out any invalid retry after values
        retry_after = None

    if retry_after:
        return retry_after
    else:
        return int(RETRY_EXPONENT_BASE**retries)


def called_from_module(module: str) -> bool:
    """
    Helper function to determine if the current function is being called from a specific module
    :param module: The module name to check against
    :return: True if the current function is being called from the specified module
    """
    stack = inspect.stack()
    for frame in stack:
        module_name = frame.frame.f_globals.get('__name__')
        if module_name and module in module_name:
            return True
    return False


def get_caller_module() -> str:
    """hellper function to determine the module that called the current function

    Returns:
        str: The Module name that called the current function
    """
    stack = inspect.stack()
    for frame in stack:
        module_name: str = frame.frame.f_globals.get('__name__', '')
        if module_name and 'jf_ingest' in module_name:
            return module_name

    return RequestModuleSource.UNKNOWN.value


class RequestModuleSource(Enum):
    """Enum to help us determine where requests are coming from
    when using the retry_for_status helper function
    """

    JIRA = 'JIRA'
    AZURE_DEVOPS = 'AZURE_DEVOPS'
    GITLAB = 'GITLAB'
    GITHUB = 'GITHUB'
    UNKNOWN = 'UNKNOWN'


def get_request_source() -> RequestModuleSource:
    """Determines the module source of the caller

    Returns:
        RequestModuleSource: Returns a RequestModuleSource enum type
    """
    if called_from_module('jf_ingest.jf_jira'):
        return RequestModuleSource.JIRA
    elif called_from_module('jf_ingest.jf_git.clients.azure_devops'):
        return RequestModuleSource.AZURE_DEVOPS
    elif called_from_module('jf_ingest.jf_git.clients.gitlab'):
        return RequestModuleSource.GITLAB
    elif called_from_module('jf_ingest.jf_git.clients.github'):
        return RequestModuleSource.GITHUB
    else:
        return RequestModuleSource.UNKNOWN


# Specific Jira Retry headers to try to grab
JiraRetryHeaders = namedtuple(
    'JiraRetryHeaders',
    (
        'X_RateLimit_Limit',
        'X_RateLimit_Remaining',
        'RateLimit_Reason',
        'X_RateLimit_NearLimit',
        'Beta_Retry_After',
        'X_Beta_RateLimit_NearLimit',
        'X_Beta_RateLimit_Reason',
        'X_Beta_RateLimit_Reset',
    ),
)


def get_jira_headers(resp: requests.Response) -> JiraRetryHeaders:
    """Generates a named tuple JiraRetryHeaders object from a requests.Response object,
    containing the Jira Rate Limit Headers. It is likely that Jira didn't supply us these
    headers, but it's worth attempting to grab.
    Headers are stated to be present in the Jira API documentation, here:
    https://developer.atlassian.com/cloud/jira/platform/rate-limiting/#rate-limit-related-headers

    Args:
        resp (requests.Response): A requests.Reponse object returned from any API call, not gaurenteed
        to have been a call for Jira

    Returns:
        JiraRetryHeaders: A named tuple object representing the headers present in the Jira API response
    """
    return JiraRetryHeaders(
        X_RateLimit_Limit=resp.headers.get('X-RateLimit-Limit'),
        X_RateLimit_Remaining=resp.headers.get('X-RateLimit-Remaining'),
        RateLimit_Reason=resp.headers.get('RateLimit-Reason'),
        X_RateLimit_NearLimit=resp.headers.get('X-RateLimit-NearLimit'),
        Beta_Retry_After=resp.headers.get('Beta-Retry-After'),
        X_Beta_RateLimit_NearLimit=resp.headers.get('X-Beta-RateLimit-Reset'),
        X_Beta_RateLimit_Reason=resp.headers.get('X-Beta-RateLimit-Reason'),
        X_Beta_RateLimit_Reset=resp.headers.get('X-Beta-RateLimit-Reset'),
    )


def retry_for_status(
    f: Callable[..., Any],
    *args,
    max_retries_for_retry_for_status: int = 5,
    statuses_to_retry: Iterable[int] = DEFAULT_HTTP_CODES_TO_RETRY_ON,
    exceptions_to_retry: Iterable[Type[Exception]] = DEFAULT_EXCEPTIONS_TO_RETRY_ON,
    retry_on_any_exception: bool = False,
    **kwargs,
) -> Any:
    """
    This function allows for us to retry for a variety of retryable errors from Jira.
    There are much more elegant ways of accomplishing this, but this is a quick and
    reasonable approach to doing so.

    Default statuses are 429 (rate limit exceeded) and 5xx errors (server errors).

    Note:
        - max_retries=5 will give us a maximum wait time of 4m16s.
    """
    global RETRY_FOR_STATUS_CALL_COUNTER
    if not RETRY_FOR_STATUS_CALL_COUNTER:
        RETRY_FOR_STATUS_CALL_COUNTER = setup_retry_counter()

    request_source = get_request_source().value
    function_name = getattr(f, '__name__', 'Unknown_Function')
    if request_source == RequestModuleSource.UNKNOWN.value:
        request_source = get_caller_module()

    for retry in range(max_retries_for_retry_for_status + 1):

        jelly_counter_attributes: dict[str, Any] = {
            "function_name": function_name,
            "max_retries": max_retries_for_retry_for_status,
            "request_source": request_source,
            "retry_attempt": retry,
            "company_slug": get_jellyfish_company_slug() or 'unknown',
        }

        # Init None Return value
        return_val = None
        try:
            return_val = f(*args, **kwargs)
            # If we pass in a session.get or session.post call to this function,
            # an error is not immediately raised because you need to call this
            # raise_for_status class method on the Response object first
            if isinstance(return_val, requests.Response):
                jelly_counter_attributes['status_code'] = return_val.status_code
                # Raise the Error
                return_val.raise_for_status()

                # If error wasn't raised, log the specific jira headers (if present)
                jira_retry_headers = get_jira_headers(return_val)
                if jira_retry_headers.X_Beta_RateLimit_NearLimit != None:
                    jelly_counter_attributes['near_beta_jira_limit'] = (
                        jira_retry_headers.X_Beta_RateLimit_NearLimit
                    )

                if jira_retry_headers.Beta_Retry_After != None:
                    jelly_counter_attributes['over_beta_jira_limit'] = bool(
                        jira_retry_headers.Beta_Retry_After
                    )

                if jira_retry_headers.X_RateLimit_NearLimit != None:
                    jelly_counter_attributes['near_current_jira_limit'] = bool(
                        jira_retry_headers.X_RateLimit_NearLimit
                    )

            jelly_counter_attributes['is_retry'] = False
            RETRY_FOR_STATUS_CALL_COUNTER.add(1, attributes=jelly_counter_attributes)
            return return_val
        except Exception as e:
            if retry >= max_retries_for_retry_for_status:
                logging_helper.send_to_agent_log_file(
                    f'Retry Limit reached when running function {function_name} from {request_source=}. Raising error:',
                    level=logging.ERROR,
                )
                # Raise any non-429 related errors
                logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
                raise RetryLimitExceeded(e)
            is_handled_exception = any(
                isinstance(e, exception) for exception in exceptions_to_retry
            )

            # Get the status code from the exception, if it exists
            if isinstance(e, requests.exceptions.HTTPError) and hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', None)
            # Special case for Gitlab errors, where status code is hidden as response code
            elif isinstance(e, gitlab.exceptions.GitlabError):
                status_code = getattr(e, 'response_code', None)
            else:
                status_code = getattr(e, "status_code", None)

            # Ignoring for mypy, since statuses_to_retry and status_code are mixed.
            if not (is_handled_exception or status_code in statuses_to_retry) and not retry_on_any_exception:  # type: ignore[operator]
                raise e

            # Otherwise, retry

            # Get Wait Time
            wait_time = get_wait_time(e, retries=retry)

            # Log Error
            error_code = 3071
            exception_name = getattr(e.__class__, '__name__', 'Exception')
            msg_args = [
                (
                    f"err={exception_name},module={request_source},status={status_code}"
                    if status_code
                    else f"err={exception_name},module={request_source}"
                ),
                retry + 1,
                max_retries_for_retry_for_status,
                wait_time,
            ]
            logging_helper.log_standard_error(
                logging.WARNING,
                msg_args=msg_args,
                error_code=error_code,
            )

            # Increment Counter
            if status_code:
                jelly_counter_attributes['status_code'] = status_code
            jelly_counter_attributes['exception'] = exception_name
            jelly_counter_attributes['is_retry'] = True
            RETRY_FOR_STATUS_CALL_COUNTER.add(
                1,
                attributes=jelly_counter_attributes,
            )

            # Sleep
            time.sleep(wait_time)
            continue


def test_jira_or_git_object_access(
    f: Callable[..., Any],
    *args,
    is_sprint: bool = False,
    return_objs: bool = True,
    return_attr: Optional[str] = None,
    **kwargs,
) -> tuple[bool, list[Any]]:
    """
    Determines whether we can access a particular class of objects within jira or git. In general, this returns True
    if no errors are thrown and False otherwise. Sprints are a special case. Boards may not support sprints,
    the board could be misconfigured, etc. If we are looking for a sprint and get a 400, 404, or 500 error
    response, assume that everything is ok and we're not missing any access.

    Args:
        f (Callable[..., Any]): JIRA.<function>
        is_sprint (bool, optional): whether we are looking for sprint data. Defaults to False. Only applicable to Jira
        return_obj (bool, optional): whether we want to return some data from the accessed objects. Returns an empty list if False. Defaults to True.
        return_attr (Any): attribute to return in a list from the accessed objects.

    Returns:
        bool: whether access to the specified object type is available.
    """

    return_attr = return_attr or 'name'

    def _get_return_list(objs: Iterable) -> list:
        objs = list(objs)  # put generator items into memory if we're dealing with git
        if not return_objs or not objs:
            return []
        if isinstance(objs[0], dict):
            return [d.get(return_attr) for d in objs]
        if not hasattr(objs[0], return_attr):
            return []
        return [getattr(obj, return_attr) for obj in objs]

    try:
        objs = retry_for_status(f, *args, **kwargs)
        return True, _get_return_list(objs)
    except JIRAError as e:
        if is_sprint:
            return e.status_code in [400, 404, 500], []
        logger.debug(
            f'Jira Error ({e.status_code}) encountered when attempting to hit function {f.__name__}. Error: {e}'
        )
        return False, []
    except Exception as e:
        logger.debug(f'Error encountered when attempting to hit function {f.__name__}. Error: {e}')
        return False, []


def batch_iterable(iterable: Iterable, batch_size: int) -> Generator[list[Any], None, None]:
    """Helper function used for batching a given iterable into equally sized batches

    Args:
        iterable (Iterable): An iterable you want to split into batches
        batch_size (int): The size of the batches you want

    Yields:
        Generator[list[Any], None, None]: This generator yields a list of equal size batches, plus a potential final batch that is less than the batch_size arg
    """
    chunk = []
    i = 0
    for item in iterable:
        chunk.append(item)
        i += 1
        if i == batch_size:
            yield chunk
            chunk = []
            i = 0

    if chunk:
        yield chunk


def get_object_bytes_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = 0
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_object_bytes_size(v, seen) for v in obj.values()])
        size += sum([get_object_bytes_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_object_bytes_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_object_bytes_size(i, seen) for i in obj])
    else:
        size += sys.getsizeof(obj)
    return size


def batch_iterable_by_bytes_size(
    iterable: Iterable, batch_byte_size: int
) -> Generator[list[Any], None, None]:
    """Helper function that batches an iterable by it's total size in bytes

    Args:
        iterable (Iterable): An iterable type object that you want batched
        batch_byte_size (int): The total size of each batch size, in bytes

    Yields:
        Generator[list[Any], None, None]: A generator that returns roughly equal sized batches of data (in byte size)
    """
    chunk = []
    current_chunk_size = 0
    for item in iterable:
        chunk.append(item)
        current_chunk_size += get_object_bytes_size(item)

        if current_chunk_size >= batch_byte_size:
            yield chunk
            # Reset batch information
            chunk = []
            current_chunk_size = 0

    # Write the final batch, if applicable
    if chunk:
        yield chunk


def format_date_to_jql(_datetime: datetime) -> str:
    """Formats a python datetime to a str in this format: YYYY-MM-DD, which is JQL friendly

    Args:
        datetime (datetime): A valid Python Datetime

    Returns:
        str: Returns a formatted datetime str in this format (with padded 0s, if needed): YYYY-MM-DD
    """
    # Special case: if we've got date.min, always return year 1, month 1, day 1.
    # This value should really never be provided, but for legacy reasons we used
    # to mark issues needing redownload as having an updated value as datetime.min
    if _datetime == datetime.min:
        return f'"0001-01-01"'

    return f'"{_datetime.year:04}-{_datetime.month:02}-{_datetime.day:02}"'


def format_datetime_to_ingest_timestamp(datetime: datetime):
    return datetime.strftime("%Y%m%d_%H%M%S")


class TqdmToLogger(io.StringIO):
    """
    Output stream for TQDM which will output to logger module instead of
    the StdOut.
    """

    logger = None
    level = None
    buf = ''

    def __init__(self, logger, level=None):
        super(TqdmToLogger, self).__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)


def tqdm_to_logger(*args, **kwargs) -> tqdm:
    """HACK helper function to wrap up the TQDM progress bar to extend it's functionality.
    If you use this helper function in place of the normal tqdm() call it will behave differently
    in Agent and in Direct Connect. In Agent, TQDM will act as if you called it directly.
    If you call this function in a DIRECT_CONNECT context, it will print each TQDM progress
    update to our logger wrapper (at the INFO level), which will get caught up in Prefect.

    Returns:
        tqdm: A TQDM object
    """
    from jf_ingest.config import IngestionType

    ingestion_type = get_ingestion_type()
    if ingestion_type == IngestionType.DIRECT_CONNECT:
        tqdm_out = TqdmToLogger(logger, level=logging.INFO)
        # Log progress bar every 10 minutes (minimum) in prefect
        mininterval = kwargs.get('mininterval', 60 * 10)
        return tqdm(file=tqdm_out, mininterval=mininterval, ascii=False, *args, **kwargs)
    return tqdm(*args, **kwargs)


class ThreadPoolExecutorWithLogging(ThreadPoolExecutor):
    def submit(self, fn, *args, **kwargs):
        ctx = contextvars.copy_context()

        def _wrapped_fn(*args_inner, **kwargs_inner):
            return ctx.run(fn, *args_inner, **kwargs_inner)

        future = super().submit(_wrapped_fn, *args, **kwargs)
        return future


class ThreadPoolWithTqdm(ThreadPoolExecutorWithLogging):
    """THIS CLASS MUST BE USED AS A CONTEXT MANAGER ONLY!!!!

    This is a custom class that extends the ThreadPoolExecutor class,
    and combines it with some TQDM (progress bar) functionality. This
    should help reduce the number of repeated code around jf_ingest

    Yes, I know there is a concurrency extension for TQDM (tqdm.contrib.concurrent)
    BUT this library only has .map style functions, and it does NOT have a submit style
    function. There are instances where using submit is preferred, and often it lends itself
    to simpler code. That is what this library is for

    Args:
        ThreadPoolExecutor (ThreadPoolExecutor): The parent class that this extends

    Returns:
        ThreadPoolWithTqdm: ThreadPoolWithTqdm
    """

    desc: str
    total: int
    futures: set[Future]
    raise_exceptions: bool
    prog_bar: tqdm
    hide_tqdm: bool

    def __init__(
        self,
        desc: Optional[str] = None,
        total: int = 0,
        max_workers: int | None = None,
        raise_exceptions: bool = False,
        thread_name_prefix: str = "",
        initializer: Callable[..., object] | None = None,
        initargs: tuple[Any, ...] = (...,),
        hide_tqdm: Optional[bool] = False,
    ) -> None:
        """Custom Constructor, to allow us to set the progress bar values

        Args:
            desc (str, optional): The description field on the TQDM progress bar. Defaults to None.
            total (int, optional): The total value to set on the TQDM progress bar. Defaults to 0.
            max_workers: The maximum number of threads that can be used to execute the given calls.
            thread_name_prefix: An optional name prefix to give our threads.
            initializer: A callable used to initialize worker threads.
            initargs: A tuple of arguments to pass to the initializer.

        """

        self.desc = desc or ''
        self.total = total
        self.futures = set()
        self.raise_exceptions = raise_exceptions
        self.hide_tqdm = bool(hide_tqdm)
        super().__init__(max_workers, thread_name_prefix, initializer, initargs)

    def __enter__(self):
        """Override the __enter__ function to instantiate a progress bar (TQDM)
        when using this as a context manager.
        """
        self.prog_bar = tqdm_to_logger(desc=self.desc, total=self.total, disable=self.hide_tqdm)
        return super().__enter__()

    def submit(self, fn: Callable, *args, **kwargs) -> Future:  # type: ignore[override]
        future: Future = super().submit(fn, *args, **kwargs)
        self.futures.add(future)
        return future

    def get_results(self) -> Generator[Any, None, None]:
        while self.futures:
            done_futures, _ = wait(self.futures, return_when=FIRST_COMPLETED)
            for done_future in done_futures:
                # Update the progress bar each time we get a future back
                try:
                    self.update_progress_bar(done_future)
                    yield done_future.result()
                except Exception as e:
                    logging_helper.send_to_agent_log_file(
                        f'Exception encountered in ThreadPoolExecutor: {e}',
                        level=logging.ERROR,
                        exc_info=True,
                    )
                    if self.raise_exceptions:
                        raise
                finally:
                    # Remove the future from the pool, for memory performance management
                    self.futures.remove(done_future)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        """Override the __exit__ function to tear down a progress bar (TQDM)
        when using this as a context manager.
        Progress bar .close() call MUST BE AFTER THE THREADPOOLEXECUTOR TEARDOWN.

        Also raises any exceptions we encountered
        """

        # Always empty the thread pool before exiting, so that the progress bar increments
        # even if nobody ever called the get_results function
        if self.futures:
            for _ in self.get_results():
                # Iterate through the get_results generate to force progress bar load
                pass
        retval = super().__exit__(exc_type, exc_val, exc_tb)

        # Progress bar must be close AFTER the parent __exit__ call,
        # because the parent __exit__ call is blocking
        self.prog_bar.close()

        return retval

    def update_progress_bar(self, future: Future):
        """A custom callback function that iterates on the progress bar by
        default. Does some guessing to see how much we should updated the
        progress bar by

        Args:
            future (Future): A ThreadPoolExecutor Future object
        """
        if future.exception():
            return

        result = future.result()

        with tqdm.get_lock():
            if isinstance(result, Iterable):
                self.prog_bar.update(len(list(result)))
            else:
                self.prog_bar.update(1)


def get_s3_base_path(company_slug: str, timestamp: str):
    return f"{company_slug}/{timestamp}"


class RewriteJiraSessionHeaders(object):
    """
    This context manager will temporarily rewrite the headers of the JIRA session to
    only use the Accept: application/json header, no other additional value. This gets around
    the incident where resolutions endpoint failed with HTTP 406 errors
    https://jelly-ai.atlassian.net/browse/OJ-31563
    """

    saved_old_accept_headers = ""
    jira_connection = None

    def __init__(self, jira_connection):
        self.jira_connection = jira_connection

    def __enter__(self):
        self.old_headers = self.jira_connection._session.headers
        self.saved_old_accept_headers = self.jira_connection._session.headers["Accept"]
        self.jira_connection._session.headers["Accept"] = "Application/json"

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.jira_connection._session.headers["Accept"] = self.saved_old_accept_headers


def chunk_iterator_in_lists(n, iterable) -> list[list]:
    """
    :param n: The size of the chunks
    :param iterable: The iterable to chunk
    :return: A list of lists where each inner list is of size n with the final inner list having size len(iterable) % n
    if n == 0 then return [[], [<all elements>]] as it produces a chunk of size 0, and then all remainders
    """
    parent_list = []
    counter = 0
    while counter + n <= len(iterable):
        parent_list.append(iterable[counter : counter + n])
        counter += n
    if counter < len(iterable):
        parent_list.append(iterable[counter : len(iterable)])
    return parent_list


def hash_filename(filepath: str):
    """
    Helper function for files. Hashes a filepath, tokenized by '/'.
    :param filepath: Input filepath.
    """

    def _compute_hash(string):
        return hashlib.md5(string.encode('utf-8'), usedforsecurity=False).hexdigest()[:12]

    extension = filepath.split(".")[-1]
    paths_list = filepath.split("/")

    # Check if a file extension (.) exists
    if len(extension) == len(filepath):
        return _compute_hash(filepath)
    return "/".join([_compute_hash(path) for path in paths_list]) + f".{extension}"


def set_ingestion_type(ingestion_type):
    """Helper function used to setting the global INGESTION_TYPE variable in this module

    Args:
        ingestion_type (_type_): The Ingestion Type we are doing (Agent or Direct Connect). Accepts the ENUM from the config.py file!
    """
    global INGESTION_TYPE
    INGESTION_TYPE = ingestion_type
    logger.debug(f'Set global value INGESTION_TYPE to {ingestion_type}')


def get_ingestion_type():
    from jf_ingest.config import IngestionType

    if 'INGESTION_TYPE' in globals():
        global INGESTION_TYPE
        return INGESTION_TYPE
    else:
        default_ingestion_type = IngestionType.AGENT
        logging_helper.send_to_agent_log_file(
            f'Ingestion type not set. This may affect the logging of this run. Defaulting to ingestion type of {default_ingestion_type}',
            level=logging.WARNING,
        )
        return default_ingestion_type


# Defined globals outside of functions for mypy
COMPANY_SLUG = ''
global JELLYFISH_API_BASE_URL
global JELLYFISH_API_TOKEN


def set_jellyfish_company_slug(company_slug: str):
    """Helper function used to setting the global COMPANY_SLUG variable in this module

    Args:
        jellyfish_api_base_url (str): The company_slug
    """
    global COMPANY_SLUG
    COMPANY_SLUG = company_slug
    logger.debug(f'Setting company slug to {company_slug}')


def get_jellyfish_company_slug():
    if 'COMPANY_SLUG' in globals():
        global COMPANY_SLUG
        return COMPANY_SLUG
    else:
        return None


def set_jellyfish_api_base_url(jellyfish_api_base_url: str):
    """Helper function used to setting the global JELLYFISH_API_BASE_URL variable in this module

    Args:
        jellyfish_api_base_url (str): The Jellyfish API Base URL
    """
    JELLYFISH_API_BASE_URL = jellyfish_api_base_url
    logger.debug('Setting Jellyfish API Base URL.')


def get_jellyfish_api_base_url():
    if 'JELLYFISH_API_BASE_URL' in globals():
        global JELLYFISH_API_BASE_URL
        return JELLYFISH_API_BASE_URL
    else:
        return None


def set_jellyfish_api_token(jellyfish_api_token: str):
    """Helper function used to setting the global JELLYFISH_API_TOKEN variable in this module

    Args:
        jellyfish_api_token (str): The Jellyfish API token
    """
    JELLYFISH_API_TOKEN = jellyfish_api_token
    logger.debug('Setting Jellyfish API token')


def get_jellyfish_api_token():
    if 'JELLYFISH_API_TOKEN' in globals():
        global JELLYFISH_API_TOKEN
        return JELLYFISH_API_TOKEN
    else:
        return None


def init_jf_ingest_run(ingestion_config: Any) -> None:
    from jf_ingest.config import IngestionConfig

    # Cast for mypy
    cast(IngestionConfig, ingestion_config)
    # Set Jellyfish API variables
    if not get_jellyfish_api_base_url():
        set_jellyfish_api_base_url(ingestion_config.jellyfish_api_base)
    if not get_jellyfish_api_token():
        set_jellyfish_api_token(ingestion_config.jellyfish_api_token)
    if not get_jellyfish_company_slug():
        set_jellyfish_company_slug(ingestion_config.company_slug)
    # Set Ingestion Type (has to do with logging)
    set_ingestion_type(ingestion_config.ingest_type)


def parse_gitlab_date(date):
    if date is None:
        return None

    return date_parser.parse(date)


def parse_gitlab_api_version(api_version: str) -> str:
    """Helper function
    Strips everything except integers and periods to get the semver of the provided gitlab version.

    For example, one version we've seen is 17.9.0-pre, but we're only interested in the major and minor version.

    Examples:
    17.9.0-pre -> 17.9.0
    17.9.0 -> 17.9.0
    """
    return re.sub(r'[^\d\.]', '', api_version)


def get_id_from_gid(gitlab_gid: str, object_name: str) -> str:
    """Helper function.
    The Gitlab GQL returns many IDs with this weird GID format.
    All we care about is the number trailing at the end.
    Objects are capitalized (Group, Project, MergeRequest, User, etc...)
    Gitlab Format: gid://gitlab/{object_name}/{ID_NUMBER}
    """
    return gitlab_gid.split(f'gid://gitlab/{object_name}/')[1]
