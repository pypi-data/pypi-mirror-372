import asyncio
import functools
import inspect
import logging
import sys
from contextlib import contextmanager
from functools import partial
from typing import Generator, Optional

from opentelemetry import baggage, context, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

logger = logging.getLogger(__name__)


def init_opentelemetry_tracer(exporter: SpanExporter) -> None:

    trace_provider = TracerProvider()
    processor = BatchSpanProcessor(exporter)
    trace_provider.add_span_processor(processor)

    # Sets the global default tracer provider
    trace.set_tracer_provider(trace_provider)


def add_telemetry_fields(fields) -> None:
    for key, val in fields.items():
        add_telemetry_span_field(key, val)
        add_telemetry_trace_field(key, val)


def add_telemetry_trace_field(key: str, value) -> None:
    """
    Adds the given key and value to OTel Baggage.

    Use this function when you want to add a context field/attribute
    to the entire trace (not just the current span.)
    """

    # NOTE(asm,2023-06-07): the opentelemetry documentation claims that you need to keep track of
    # the token returned from `context.attach` and call `detach` at the conclusion of the span. This
    # is difficult to wrangle, particularly in the case of decorated functions. Throwing caution to
    # the wind, we're going to just call `context.attach` and not `detach`. This doesn't _seem_ to
    # be causing any problems at the time of writing, but if we start getting incoherent-looking
    # tracing data, this may be why. A better solution might be to create our own decorator for
    # tracing functions, but at that point we'd basically be writing our own telemetry library and
    # I'd like to avoid that (for now, at least).
    # See: https://docs.honeycomb.io/getting-data-in/opentelemetry/python-distro/#multi-span-attributes
    context.attach(baggage.set_baggage(key, value))


def add_telemetry_span_field(key, value):
    """
    Adds the given key and value to both the OTel attribute
    for the current span.

    Use this function when you want to add a context field/attribute
    to the current span, but not the whole trace.

    """
    set_current_span_attribute(key=key, value=value)


def add_telemetry_span_fields(fields: dict):
    """
    Adds the given key/value pairs to the OTel attribute for the current span.

    Use this function when you want to add context fields/attributes
    to the current span, but not the whole trace.
    """
    for key, val in fields.items():
        add_telemetry_span_field(key=key, value=val)


def set_current_span_attribute(key: str, value):
    """
    Sets an attribute  with a key value for the current span.
    """

    span = trace.get_current_span()
    span.set_attribute(key, value)


@contextmanager
def record_span(name: str, attributes: Optional[dict] = None) -> Generator[None, None, None]:
    """
    Start a new span with the given attributes. This is a convenience function that wraps
    the start_span and finish_span/end functions from OTel.
    The span will be automatically finished/ended when the context manager exits.
    We use a convention where the calling module's name is used as the tracer name.
    The given name will be used as the span name.
    """
    try:
        # Get the current frame and check if it's not None
        current_frame = inspect.currentframe()
        if current_frame is None or current_frame.f_back is None:
            raise AttributeError("Could not get the previous frame for tracing")

        # Get the module of the calling function and check if it's not None
        module = inspect.getmodule(current_frame.f_back)
        if module is None:
            raise AttributeError(
                f"Could not get module name for tracing (name={name}, attributes={attributes})"
            )

        tracer = trace.get_tracer(module.__name__)
        attributes = attributes or {}

        with tracer.start_as_current_span(name=name, attributes=attributes):
            yield
    except AttributeError as e:
        logger.error(str(e))


def jelly_trace(func=None, *, span_name=None):
    """
    Decorator for tracing a function with Jellyfish's telemetry libraries.
    We use a convention where the decorated function's module's name is used as the tracer name.
    """

    # While name is optional, this decorator will not execute unless all parameters are provided.
    if func is None:
        return partial(jelly_trace, span_name=span_name)

    # Use the module name of the calling function as the tracer name.
    module = sys.modules[func.__module__]
    tracer = trace.get_tracer(module.__name__)

    # If the span name is not provided, use the function name.
    span_name = span_name or func.__name__

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            otel_span = tracer.start_span(name=span_name)
            try:
                return await func(*args, **kwargs)
            finally:
                otel_span.end()

        return async_wrapper

    otel_trace = tracer.start_as_current_span(name=span_name)

    return otel_trace(func)
