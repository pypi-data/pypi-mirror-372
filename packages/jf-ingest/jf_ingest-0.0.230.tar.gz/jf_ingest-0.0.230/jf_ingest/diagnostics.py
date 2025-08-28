import json
import logging
import os
import shutil
import subprocess
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from functools import wraps
from io import TextIOWrapper
from typing import NamedTuple, Optional

import psutil
import pytz
import requests

from jf_ingest import logging_helper

_DIAGNOSTICS_FILE: Optional[TextIOWrapper] = None


def _diagnostics_file_closed():
    return isinstance(_DIAGNOSTICS_FILE, TextIOWrapper) and _DIAGNOSTICS_FILE.closed


"""
The diagnostics module is used to capture diagnostics data
for agent runs. When running for Managed Ingest we do not
need to use any of this logic. For unity's sake we will
run the shared functions (so far only capture_timing),
but output nothing
"""

logger = logging.getLogger(__name__)


def _write_diagnostic(obj):
    # If there is no diagnostics file to write to, do nothing
    if not _DIAGNOSTICS_FILE:
        logger.debug(f"No diagnostics file is set")
        return

    json.dump(obj, _DIAGNOSTICS_FILE)
    _DIAGNOSTICS_FILE.write("\n")  # facilitate parsing
    _DIAGNOSTICS_FILE.flush()


def capture_agent_version():
    git_head_hash = os.getenv("SHA")
    build_timestamp = os.getenv("BUILDTIME")
    _write_diagnostic({"type": "agent_version", "sha": git_head_hash, "timestamp": build_timestamp})


# NOTE: This is the only function that is called from within the jf_ingest module!
# (as of 8/2/2023 -Gavin)
def capture_timing(*args, **kwargs):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = pytz.utc.localize(datetime.utcnow()).isoformat()
            if "func_name_override" in kwargs:
                func_name = kwargs.pop("func_name_override")
            else:
                func_name = func.__name__
            ret = func(*args, **kwargs)
            end_time = pytz.utc.localize(datetime.utcnow()).isoformat()
            diag_obj = {
                "type": "func_timing",
                "name": func_name,
                "start": start_time,
                "end": end_time,
            }
            if ret is not None:
                try:
                    diag_obj["num_items"] = len(ret)
                except TypeError:
                    if type(ret) is int:
                        diag_obj["num_items"] = ret
            _write_diagnostic(diag_obj)
            return ret

        return wrapper

    return actual_decorator


def capture_run_args(run_mode: str, config_file: str, outdir: str, prev_output_dir: str):
    _write_diagnostic(
        {
            "type": "run_args",
            "run_mode": run_mode,
            "config_file": config_file,
            "outdir": outdir,
            "prev_output_dir": prev_output_dir,
        }
    )


def capture_outdir_size(outdir: str):
    _write_diagnostic(
        {
            "type": "outdir_size",
            "size_kb": int(
                subprocess.check_output(["du", "-sk", outdir]).split()[0].decode("utf-8")
            ),
        }
    )


class HeartBeatStart(NamedTuple):
    timestamp_key: str
    time: str  # This is an ISO timestamp
    memory_allocated_in_gb: float
    run_git: bool
    run_jira: bool
    will_send: bool


class SysReading(NamedTuple):
    """This is used as the diagnostic 'heartbeat'"""

    timestamp_key: str
    time: str  # This is an ISO timestamp
    cpu_pct: float
    memory_used_gb: float
    memory_pct: float
    disk_used_gb: float
    disk_pct: float


class HeartBeatEnd(NamedTuple):
    timestamp_key: str
    time: str  # This is an ISO timestamp
    git_success: bool  # NOTE / TODO: You can have multiple git instances, but this boolean reflects all or nothing success
    jira_success: bool


def post_to_agent_monitor(url: str, jellyfish_api_token: str, data: NamedTuple):
    try:
        headers = {'X-JF-API-Token': jellyfish_api_token}

        r = requests.post(
            url,
            headers=headers,
            json=data._asdict(),
        )

        r.raise_for_status()
    except Exception as e:
        logging_helper.send_to_agent_log_file(
            f'Failed to send initial Diagnostic heart beat to Jellyfish. Error: {e}'
        )
        logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)


def send_diagnostic_start_reading(
    jellyfish_webhook_base: str,
    jellyfish_api_token: str,
    timestamp_key: str,
    will_run_git: bool,
    will_run_jira: bool,
    will_send: bool,
):
    heart_beat_start = HeartBeatStart(
        memory_allocated_in_gb=psutil.virtual_memory().total / (1024**3),
        timestamp_key=timestamp_key,
        time=datetime.now(timezone.utc).isoformat(),
        run_git=will_run_git,
        run_jira=will_run_jira,
        will_send=will_send,
    )
    post_to_agent_monitor(
        url=f'{jellyfish_webhook_base}/agent-monitor/start',
        jellyfish_api_token=jellyfish_api_token,
        data=heart_beat_start,
    )


def send_diagnostic_end_reading(
    jellyfish_webhook_base: str,
    jellyfish_api_token: str,
    timestamp_key: str,
    git_success: bool,
    jira_success: bool,
):
    heart_beat_end = HeartBeatEnd(
        timestamp_key=timestamp_key,
        time=datetime.now(timezone.utc).isoformat(),
        git_success=git_success,
        jira_success=jira_success,
    )
    post_to_agent_monitor(
        url=f'{jellyfish_webhook_base}/agent-monitor/stop',
        jellyfish_api_token=jellyfish_api_token,
        data=heart_beat_end,
    )


def continually_gather_system_diagnostics(
    kill_event: threading.Event,
    outdir: str,
    jellyfish_webhook_base: str,
    jellyfish_api_token: str,
    send_to_jf_endpoint: bool = True,
    cycle_period_in_seconds: int = 60,
):
    def _flush_cached_readings(cached_readings: list[SysReading]):
        if not cached_readings:
            return
        _write_diagnostic(
            {
                "type": "sys_resources_60s",
                "start": cached_readings[0].time,
                "end": cached_readings[-1].time,
                "cpu_pct": ["%.2f" % r.cpu_pct for r in cached_readings],
                "mem_used_gb": ["%.2f" % r.memory_used_gb for r in cached_readings],
                "mem_pct": ["%.2f" % r.memory_pct for r in cached_readings],
                "disk_used_gb": ["%.2f" % r.disk_used_gb for r in cached_readings],
                "disk_pct": ["%.2f" % r.disk_pct for r in cached_readings],
            }
        )

    readings = threading.local()
    readings.cached_readings = []
    readings.last_reading_time = None
    readings.last_flush_time = datetime.now(timezone.utc)

    while True:
        if kill_event.is_set():
            _flush_cached_readings(readings.cached_readings)
            readings.cached_readings = []
            return
        else:
            now = datetime.now(timezone.utc)
            if not readings.last_reading_time or (now - readings.last_reading_time) > timedelta(
                seconds=cycle_period_in_seconds
            ):
                # First, gather diagnostics data
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = shutil.disk_usage(outdir)
                _, timestamp_key = os.path.split(outdir)
                sys_reading = SysReading(
                    timestamp_key,
                    now.isoformat(),
                    cpu / 100,
                    (memory.total - memory.available) / (1024**3),
                    (memory.total - memory.available) / memory.total,
                    disk.used / (1024**3),
                    disk.used / disk.total,
                )
                # Next submit diagnostics data to the local cache to eventually
                # flush to the diagnostics.json
                readings.cached_readings.append(sys_reading)
                readings.last_reading_time = now

                # Finally, send this snapshot of diagnostics reading to the jellyfish
                # server as a 'heartbeat' diagnostics update if enabled
                if send_to_jf_endpoint:
                    post_to_agent_monitor(
                        url=f'{jellyfish_webhook_base}/agent-monitor/heartbeat',
                        jellyfish_api_token=jellyfish_api_token,
                        data=sys_reading,
                    )

            if now - readings.last_flush_time > timedelta(seconds=300):
                _flush_cached_readings(readings.cached_readings)
                readings.cached_readings = []
                readings.last_flush_time = now

            # Keep the sleep short so that the thread's responsive to the kill_event
            time.sleep(1)


def open_file(outdir: str):
    global _DIAGNOSTICS_FILE
    try:
        if _DIAGNOSTICS_FILE is None:
            _DIAGNOSTICS_FILE = open(os.path.join(outdir, "diagnostics.json"), "a")
        elif _diagnostics_file_closed():
            _DIAGNOSTICS_FILE = open(os.path.join(outdir, "diagnostics.json"), "a")
        else:
            logger.debug(f"Diagnostics file is already open")
    except Exception as e:
        # These messages are left at the DEBUG level for a better UX in agent
        logger.debug(f"Error opening Diagnostics file. Diagnostics will not be written. Error: {e}")


def close_file():
    try:
        global _DIAGNOSTICS_FILE
        if _DIAGNOSTICS_FILE is None:
            logger.debug("Diagnostics file is already closed")
        elif _diagnostics_file_closed():
            logger.debug("Diagnostics file is already closed")
        else:
            logger.debug("Closing diagnostics file")
            _DIAGNOSTICS_FILE.close()
        _DIAGNOSTICS_FILE = None
    except Exception as e:
        # These messages are left at the DEBUG level for a better UX in agent
        logger.debug(f"Error closing Diagnostics file. Diagnostics will not be written. Error: {e}")
