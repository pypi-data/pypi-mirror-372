import atexit
import logging
import threading
import time
from typing import Mapping, Optional, Sequence, Union

from opentelemetry.metrics import (
    CallbackOptions,
    Histogram,
    NoOpMeterProvider,
    ObservableGauge,
    Observation,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    MetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.util.types import Attributes

logger = logging.getLogger(__name__)

_METRIC_EXPORTER: Optional[MetricExporter] = None


def init_opentelemetry_metrics_exporter(exporter: MetricExporter):
    """
    Initializes the OpenTelemetry metrics exporter to be used across various metric classes in this module.
    This is meant to be called once at initialization time. If no exporter is provided, all metric implementations will be NoOps.
    """
    global _METRIC_EXPORTER
    _METRIC_EXPORTER = exporter


class SuppressShutdownWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "Can't shutdown multiple times" not in record.getMessage()


class JellyMetricBase:
    """
    Base class for all Jelly metrics, handling common setup and ensuring metrics are flushed at exit.
    Uses singleton metric provider and reader to avoid conflicts between multiple instances.
    """

    _meter_provider: Optional[MeterProvider] = None
    _reader: Optional[PeriodicExportingMetricReader] = None

    def __init__(self):
        self._instrument_lock = threading.RLock()
        self._reader_lock = threading.RLock()

        if not _METRIC_EXPORTER:
            logger.info("No exporter configured. Using NoOpMetricProvider.")
            if not JellyMetricBase._meter_provider:
                JellyMetricBase._reader = None
                JellyMetricBase._meter_provider = NoOpMeterProvider()
        else:
            if not JellyMetricBase._meter_provider:
                JellyMetricBase._reader = PeriodicExportingMetricReader(_METRIC_EXPORTER)
                JellyMetricBase._meter_provider = MeterProvider(
                    metric_readers=[JellyMetricBase._reader]
                )

        self._reader = JellyMetricBase._reader
        self._provider = JellyMetricBase._meter_provider

        self._suppress_warnings()
        atexit.register(self.shutdown_reader)

    def _get_meter(self):
        return self._provider.get_meter(__name__)

    def shutdown_reader(self):
        """Ensures the reader is flushed and shutdown at exit."""
        if not self._reader:
            return

        with self._reader_lock:
            self._reader.force_flush()
            self._reader.shutdown()

    def safe_collect(self):
        """Safely collects metrics if a reader is configured and registered."""
        if self._reader:
            with self._instrument_lock:
                try:
                    self._reader.collect()
                except Exception as e:
                    logger.warning(f"Failed to collect metrics: {e}")

    @staticmethod
    def _suppress_warnings():
        """Suppress specific warnings from OpenTelemetry loggers."""
        otel_logger = logging.getLogger("opentelemetry.sdk.metrics._internal.export")

        # Check if the filter is already added
        for f in otel_logger.filters:
            if isinstance(f, SuppressShutdownWarningFilter):
                return

        otel_logger.addFilter(SuppressShutdownWarningFilter())


class JellyGauge(JellyMetricBase):
    """
    nt 6/2023. This is a workaround for the annoying current limitation preventing synchronous gauges/settable up/down counters.
    Just for consistency purposes it would be nice to move away from this once this is closed: https://github.com/open-telemetry/opentelemetry-specification/issues/2318
    See: which I think is a work-in-progress solution to this that may merge soon: https://github.com/open-telemetry/opentelemetry-specification/pull/3540

    Heavily influenced by this solution in the thread: https://github.com/open-telemetry/opentelemetry-specification/issues/2318#issuecomment-1450929833
    """

    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._meter = self._get_meter()
        self._internal_gauge: Optional[ObservableGauge] = None
        self._observations: list[Observation] = []

    def measure(
        self,
        value: Union[int, float],
        attributes: Optional[
            Mapping[
                str,
                Union[
                    str,
                    bool,
                    int,
                    float,
                    Sequence[str],
                    Sequence[bool],
                    Sequence[int],
                    Sequence[float],
                ],
            ]
        ],
        record_immediate: bool = False,
    ) -> None:
        """
        Sending up a single measurement of the gauge with the given attributes.
        Set record_immediate to be true if you want to immediately flush the reader after this metric is collected -- should only
        be used in short-lived process situations.
        """
        logger.debug(
            f"Received measure call for {self._name}, reporting measurement {value}, {attributes}"
        )

        with self._instrument_lock:
            self._observations.append(Observation(value=value, attributes=attributes))

            if not self._internal_gauge:
                self._internal_gauge = self._meter.create_observable_gauge(
                    name=self._name, callbacks=[self._callback]
                )

        if record_immediate:
            self.safe_collect()

    def _callback(self, _options: CallbackOptions) -> list[Observation]:
        """
        Callback function for async gauge. Clears the observations as they're reported.
        """
        logger.debug(
            f"Received callback function call for {self._name}, reporting observations {self._observations}"
        )

        with self._instrument_lock:
            obs = self._observations
            self._observations = []

        return obs


class JellyHistogram(JellyMetricBase):
    """
    Creates an OTLP histogram that is safe to use in a forked process.
    The reason this is fork-safe is because it is safe for code that is ephemeral,
    since it is possible to call reader.record() after every recording, with record_immediate=True
    This avoids the PeriodicExportingMetricReader's downside which that it by definition
    it exports periodically, which removes the issue of losing metrics when a process exits before
    the reader can record.

    "buckets" may optionally be provided as a list of integers or floats to specify the bucket boundaries,
    otherwise the defaults of
    """

    def __init__(
        self,
        name: str,
        unit: str = "",
        description: str = "",
        buckets: Optional[list[Union[int, float]]] = None,
    ):
        super().__init__()
        self._name = name

        if buckets:
            self._provider = MeterProvider(
                metric_readers=[self._reader],
                views=[
                    View(
                        instrument_name=name,
                        instrument_type=Histogram,
                        aggregation=ExplicitBucketHistogramAggregation(boundaries=buckets),
                    )
                ],
            )

        self._meter = self._get_meter()
        self._internal_histogram = self._meter.create_histogram(
            name=name, unit=unit, description=description
        )

    def measure(
        self, value: int | float, attributes: Attributes = {}, record_immediate: bool = False
    ):
        logger.debug(
            f"Received Histogram Measurement for histogram {self._name}, reporting {value} with attributes {attributes}"
        )

        with self._instrument_lock:
            self._internal_histogram.record(amount=value, attributes=attributes)

        if record_immediate:
            self.safe_collect()


class JellyHistogramWithTimer(JellyHistogram):
    """
    Same as JellyHistogram but with a managed timer. The timer is started whenever the class
    is instantiated, and can be reset with the `reset_timer` method or by calling `record_time`.

    Use `record_time` instead of `measure` for recording to the histogram.
    """

    def __init__(self, *args, **kwargs):
        kwargs['unit'] = 's'  # override this value if passed in
        super().__init__(*args, **kwargs)
        self._timer = time.perf_counter()

    def reset_timer(self) -> None:
        self._timer = time.perf_counter()

    def record_time(
        self, attributes: Optional[Attributes] = None, record_immediate: bool = False
    ) -> None:
        """
        Records the time since the internal timer was last reset to
        the histogram object and resets the internal timer.
        """
        with self._instrument_lock:
            if attributes is None:
                attributes = {}

            super().measure(
                value=time.perf_counter() - self._timer,
                attributes=attributes,
                record_immediate=record_immediate,
            )
            self.reset_timer()


class JellyCounter(JellyMetricBase):
    """
    Creates an OTLP counter that is safe to use in a forked process.
    The reason this is fork-safe is because it is safe for code that is ephemeral,
    since it is possible to call reader.record() after every recording, with record_immediate=True
    This avoids the PeriodicExportingMetricReader's downside which that it by definition
    it exports periodically, which removes the issue of losing metrics when a process exits before
    the reader can record.
    """

    def __init__(self, name: str, unit: str = "", description: str = ""):
        super().__init__()
        meter = self._get_meter()
        self._internal_counter = meter.create_counter(name=name, unit=unit, description=description)
        self._name = name

    def add(
        self, amount: int | float, attributes: Attributes = {}, record_immediate: bool = False
    ) -> None:
        """
        Adds to the counter by the specified amount with the specified attributes.
        """
        with self._instrument_lock:
            self._internal_counter.add(amount=amount, attributes=attributes)

        if record_immediate:
            self.safe_collect()
