import inspect
import logging
import time
import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Any, Optional

logger = logging.getLogger(__name__)

AGENT_LOG_TAG = 'agent_log_file_only'
LOG_FILE_NAME = "jf_agent.log"


def _get_logger_from_parent() -> logging.Logger:
    """
    Retrieves a logger instance, inheriting the parent's logger if available.
    """
    name = None
    current_frame = inspect.currentframe()

    # Grab the frame two levels up to get the calling module's name
    # I don't think we need excessive null checking here like this but I am paranoid
    if current_frame and current_frame.f_back and current_frame.f_back.f_back:
        frame = current_frame.f_back.f_back
        name = frame.f_globals.get('__name__', 'root')

    if name:
        return logging.getLogger(name)
    else:
        return logger


def log_entry_exit(*args, **kwargs):
    logger = _get_logger_from_parent()

    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            start_time = time.time()
            logger.debug(f"{func_name}: Starting")

            ret = func(*args, **kwargs)

            logger.debug(f"{func_name}: Ending")
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug(f"{func_name}: Execution took {elapsed_time:.4f} seconds")
            return ret

        return wrapper

    return actual_decorator


@contextmanager
def log_loop_iters(loop_desc, this_iternum, log_every_n_iters, log_entry=True, log_exit=True):
    logger = _get_logger_from_parent()
    if (this_iternum - 1) % log_every_n_iters == 0:
        if log_entry:
            logger.debug(f'Loop "{loop_desc}", iter {this_iternum}: Starting')
        yield
        if log_exit:
            logger.debug(f'Loop "{loop_desc}", iter {this_iternum}: Ending')
    else:
        yield


# Mapping of error/warning codes to templated error messages to be called by
# log_standard_error(). This allows for Jellyfish to better categorize errors/warnings.
ERROR_MESSAGES = {
    0000: "An unknown error has occurred. Error message: {}",
    3000: "Failed to upload file {} to S3 bucket",
    3001: "Connection to bucket was disconnected while uploading: {} with the following error: {}. Retrying...",
    3010: "Rate limiter: thought we were operating within our limit (made {}/{} calls for {}), but got HTTP 429 anyway!",
    3020: "Next available time to make call is after the timeout of {} seconds. Giving up.",
    3030: "ERROR: Could not parse response with status code {}. Contact an administrator for help.",
    3011: "Error normalizing PR {} from repo {}. Skipping...",
    3021: "Error getting PRs for repo {}. Skipping...",
    3031: "Unable to parse the diff For PR {} in repo {}; proceeding as though no files were changed.",
    3041: "For PR {} in repo {}, caught HTTPError (HTTP 401) when attempting to retrieve changes; "
    "proceeding as though no files were changed",
    3051: "For PR {} in repo {}, caught UnicodeDecodeError when attempting to decode changes; proceeding as though no files were changed",
    3061: "Failed to download {} data:\n{}",
    3071: "Received retryable requests error ({}), retry {} / {}.  Trying again in {}...",
    3081: "Got unexpected HTTP 403 for repo {}.  Skipping...",
    3091: "Github rate limit exceeded.  Trying again in {}...",
    3101: "Request to {} has failed {} times -- giving up!",
    3121: 'Got HTTP {} when fetching commit {} for "{}", this likely means you are trying to fetch an invalid re',
    3131: "Got {} {} when {} ({})",
    3141: "Got {} {} when {}",
    3151: "Getting HTTP 429s for over an hour; giving up!",
    3002: "Failed to download jira data:\n{}",
    3012: "Caught KeyError from search_issues(), reducing batch size to {}",
    3022: "Caught KeyError from search_issues(), batch size is already 0, bailing out",
    3032: "Exception encountered in thread {}\n{}",
    3042: "[Thread {}] Jira issue downloader FAILED",
    3052: "JIRAError ({}), reducing batch size to {}",
    3062: "Apparently unable to fetch issue based on search_params {}",
    3082: "OJ-9084: Changelog history item with no 'fieldId' or 'field' key: {}",
    3092: (
        "OJ-22511: server side 500, batch size reduced to 0, "
        "last error was: {} with jql: {}, start_at: {}, and batch_size: {}. Skipping one issue ahead..."
    ),
    2101: "Failed to connect to {}:\n{}",
    2102: "Unable to access project {}, may be a Jira misconfiguration. Skipping...",
    2112: "Failed to connect to Jira for project ID: {}",
    2122: "you do not have the required 'development field' permissions in jira required to scan for missing repos",
    2132: (
        "Missing recommended jira_fields! For the best possible experience, "
        "please add the following to `include_fields` in the "
        "configuration file: {}"
    ),
    2142: (
        "Excluding recommended jira_fields! For the best possible experience, "
        "please remove the following from `exclude_fields` in the "
        "configuration file: {}",
    ),
    2201: (
        "\nERROR: Failed to download ({}) repo(s) from the group {}. "
        "Please check that the appropriate permissions are set for the following repos... ({})"
    ),
    2202: "You do not have the required permissions in jira required to fetch boards for the project {}",
    2203: "ERROR: Failed downloading sprints for Jira board: {} with s_start_at={}.\nReceived 400 response:\n{}",
}


def generate_standard_error_msg(error_code, msg_args=[]):
    return f"[{error_code}] {ERROR_MESSAGES.get(error_code).format(*msg_args)}"


def log_standard_error(level, error_code, msg_args=[], extra=None, exc_info=False):
    """
    For a failure that should be sent to the logger with an error_code, and also written
    to stdout (for user visibility)
    """
    logger = _get_logger_from_parent()
    assert level >= logging.WARNING
    msg = generate_standard_error_msg(error_code=error_code, msg_args=msg_args)
    logger.log(level=level, msg=msg, extra=extra)
    if exc_info:
        logger.log(level=level, msg=traceback.format_exc())


def send_to_agent_log_file(
    msg: str,
    level: int = logging.INFO,
    extra: Optional[dict] = None,
    exc_info: Optional[bool] = False,
):
    """Helper function for logging things to debug or INFO. Agent relies heavily on logging things to
    debug to send extra info to the agent.log file. For Direct Connect we'd like to get all the debug
    info as well, but due to prefect weirdness we have to do this work around.

    All logs submitted via this wrapper will be tagged as 'agent_log_file_only': True in the log records
    'extra' field

    Args:
        msg (str): Message to log
        level (int): The level of the log to log. Defaults to logging.INFO
        extra (dict): A dictionary of extra things to tag this log with. Defaults to {}
        exc_info (bool): Whether to log exception info. Defaults to False
    """
    log_extras: dict[str, Any] = {}
    logger = _get_logger_from_parent()

    if extra:
        log_extras.update(extra)

    log_extras[AGENT_LOG_TAG] = True
    logger.log(level=level, msg=msg, extra=log_extras, exc_info=exc_info)
