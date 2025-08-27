import dataclasses
import logging
from contextlib import contextmanager
from typing import Optional

import requests

from jf_ingest.events.models import EventState, IngestEvent
from jf_ingest.utils import get_jellyfish_api_base_url, get_jellyfish_api_token

logger = logging.getLogger(__name__)

# NOTE: This code is currently disabled, as we never followed through with the event emission system.


def emit_event_to_jellyfish(event: IngestEvent) -> Optional[requests.Response]:
    """
    Utility function for emitting events directly to Jellyfish, via the Jellyfish app API.

    Args:
        event_name (str): The event name to emit.
        event_state (Optional[EventState], optional): An event state enum to add to the event payload. Defaults to None.
        event_extras (Optional[dict], optional): A dictionary of extra even key/values to join to the event payload. Defaults to None.
        exception (Optional[Exception], optional): An exception object, to mark if this event is related to an exception. Defaults to None.

    Returns:
        Response: This returns what ever the wrapped _func function will return
    """
    if True:
        # TODO: We don't have a good method of getting "global" feature flags in JF Ingest;
        # we currently only have git or jira specific feature flags. We should introduce
        # an endpoint on Jellyfish that can pass forward global feature flags (and also maybe
        # we should redesign git and jira feature flags to do that as well). Feature flags
        # could be cached once they reach JF Ingest, so we don't have to hit the API everytime
        logger.debug(f'Jellyfish Ingest Event Emission is currently disabled')
        return None

    if not get_jellyfish_api_token() or not get_jellyfish_api_base_url():
        logger.error(
            f'emit_event_to_jellyfish was called without jellyfish_api_token or without jellyfish_api_base_url. An event will not be emitted'
        )
        return

    try:
        headers = {"Jellyfish-API-Token": get_jellyfish_api_token()}
        payload = dataclasses.asdict(event)
        response = requests.post(
            f"{get_jellyfish_api_base_url()}/endpoints/ingest/publish-event",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response
    except Exception as e:
        logger.error(f'Exception {e} encountered when attempting to emit status to Jellyfish')


@contextmanager
def emit_event_to_jellyfish_context_manager(ingest_event: IngestEvent):
    """NOTE: This is deprecated for now. This was originally supposed to be used
    as part of a status emitting system to monitor ingest as it runs. That idea got
    scrapped, however. For now I'm leaving this code in even though it's not referenced anywhere.

    Context Manager for wrapping up logic with a "START" and "END" event emission

    Args:
        event_name (str): The event name to call this logical block of code
        event_extras (Optional[dict], optional): Optional information to submit to the event payload. Defaults to None.
    """
    _exception = None
    try:
        start_event = dataclasses.replace(ingest_event, event_state=EventState.START)
        emit_event_to_jellyfish(start_event)
        yield
    except Exception as e:
        _exception = e
        raise
    finally:
        end_event = dataclasses.replace(
            ingest_event,
            event_state=EventState.ERROR if _exception else EventState.SUCCESS,
            error_message=str(_exception) if _exception else '',
        )
        emit_event_to_jellyfish(end_event)
