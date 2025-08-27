import statistics
from unittest.mock import patch

import pytest

from jf_ingest.adaptive_throttler import AdaptiveThrottler


@pytest.fixture
def throttler():
    """Fixture for setting up the AdaptiveThrottler with test parameters."""
    return AdaptiveThrottler(
        max_rps=10.0,
        baseline_window_size=10,
        percentile_threshold=0.90,
        backoff_factor=0.8,
        reverse_backoff_factor=0.95,
    )


def _get_time_values(response_times: list[float]) -> tuple[list[float], float]:
    time_values = []
    cumulative_time = 1000.0

    for rt in response_times:
        time_values.append(cumulative_time)  # Start time
        cumulative_time += rt
        time_values.append(cumulative_time)  # End time

    return time_values, cumulative_time


def _get_threshold_time(response_times: list[float], throttler: AdaptiveThrottler) -> float:
    # Calculate expected percentile threshold time
    sorted_times: list[float] = sorted(response_times)
    percentile_index = int(len(sorted_times) * throttler._percentile_threshold)
    percentile_index = min(percentile_index, len(sorted_times) - 1)
    return sorted_times[percentile_index]


def test_baseline_collection(throttler):
    """Test if the baseline is properly calculated after collecting enough response times."""
    response_times = [0.1, 0.2, 0.15, 0.3, 0.25, 0.2, 0.18, 0.22, 0.2, 0.19]

    # Prepare time values for the baseline
    time_values, cumulative_time = _get_time_values(response_times)
    time_iter = iter(time_values)

    with patch('time.perf_counter', side_effect=lambda: next(time_iter)):
        for _ in response_times:
            with throttler.process_response_time():
                pass

    # Calculate expected 95th percentile time
    sorted_times = sorted(response_times)
    index = int(throttler._percentile_threshold * len(sorted_times))
    percentile_value = sorted_times[index]

    # Calculate standard deviation
    std_dev = statistics.stdev(response_times)

    # Calculate expected adjusted threshold (percentile + 2 * std_dev)
    expected_percentile_time = percentile_value + (2 * std_dev)

    # Calculate expected initial request rate
    average_time = sum(response_times) / len(response_times)
    expected_request_rate = min(1 / average_time, throttler.max_rps)

    # Assert that the adjusted percentile threshold is correct
    assert throttler._percentile_threshold_time == pytest.approx(expected_percentile_time), (
        f"Expected adjusted threshold time {expected_percentile_time}, "
        f"but got {throttler._percentile_threshold_time}"
    )

    # Assert that the initial request rate is correctly calculated
    assert throttler._initial_request_rate == pytest.approx(expected_request_rate), (
        f"Expected initial request rate {expected_request_rate}, "
        f"but got {throttler._initial_request_rate}"
    )


def test_throttling_when_above_threshold(throttler):
    """Test if throttling occurs when response times exceed the threshold."""
    # Initial response times to establish the baseline
    response_times = [0.1, 0.2, 0.15, 0.3, 0.25, 0.2, 0.18, 0.22, 0.2, 0.19]

    # Prepare time values for the baseline
    time_values, cumulative_time = _get_time_values(response_times)

    # Calculate expected percentile threshold time
    expected_percentile_time = _get_threshold_time(response_times, throttler)

    # Simulate a response time above the threshold
    response_above_threshold = expected_percentile_time + 0.15
    time_values.append(cumulative_time)  # Start time of the above-threshold response
    cumulative_time += response_above_threshold
    time_values.append(cumulative_time)  # End time

    time_iter = iter(time_values)

    with (
        patch('time.perf_counter', side_effect=lambda: next(time_iter)),
        patch('time.sleep') as mock_sleep,
    ):
        # Establish baseline
        for _ in response_times:
            with throttler.process_response_time():
                pass

        assert throttler._percentile_threshold_time > 0, "Percentile threshold time should be set."
        assert throttler._request_rate > 0, "Initial request rate should be calculated."

        # Capture initial rate
        initial_rate = throttler._request_rate
        expected_throttled_rate = initial_rate * throttler.backoff_factor
        expected_backoff_time = 1 / expected_throttled_rate

        # Simulate response time that exceeds the threshold
        with throttler.process_response_time():
            pass

        # Check that time.sleep was called with the expected backoff time
        mock_sleep.assert_called_with(expected_backoff_time)

        # Assertions with calculated expected values
        assert throttler._request_rate == expected_throttled_rate, (
            f"Expected throttled rate {expected_throttled_rate}, "
            f"but got {throttler._request_rate}"
        )


def test_recovery_when_below_threshold(throttler):
    """Test if recovery occurs incrementally when response times are below the threshold."""
    # Initial response times to establish the baseline
    response_times = [0.1, 0.2, 0.15, 0.2, 0.18, 0.22, 0.19, 0.2, 0.25, 0.24]

    # Prepare time values for the baseline
    time_values, cumulative_time = _get_time_values(response_times)

    # Calculate expected percentile threshold time
    expected_percentile_time = _get_threshold_time(response_times, throttler)

    # Simulate a response above the threshold
    response_above_threshold = expected_percentile_time + 0.1
    time_values.append(cumulative_time)  # Start time of the above-threshold response
    cumulative_time += response_above_threshold
    time_values.append(cumulative_time)  # End time

    # Simulate recovery responses
    total_cycles = 2
    for _ in range(total_cycles * throttler.reverse_backoff_counter):
        response_below_threshold = expected_percentile_time - 0.05
        time_values.append(cumulative_time)
        cumulative_time += response_below_threshold
        time_values.append(cumulative_time)

    time_iter = iter(time_values)

    with patch('time.perf_counter', side_effect=lambda: next(time_iter)), patch('time.sleep'):
        # Establish baseline
        for _ in response_times:
            with throttler.process_response_time():
                pass

        # Trigger throttling
        with throttler.process_response_time():
            pass

        # Simulate recovery with consecutive below-threshold responses
        for cycle in range(1, total_cycles + 1):
            request_rate_before_recovery = throttler._request_rate

            for _ in range(throttler.reverse_backoff_counter):
                with throttler.process_response_time():
                    pass

            expected_recovered_rate = min(
                request_rate_before_recovery / throttler.reverse_backoff_factor,
                throttler._initial_request_rate,
            )

            assert throttler._request_rate == pytest.approx(expected_recovered_rate, rel=1e-5), (
                f"Cycle {cycle}: Expected recovered rate {expected_recovered_rate}, "
                f"but got {throttler._request_rate}"
            )


def test_no_recovery_if_not_enough_consecutive_responses(throttler):
    """
    Test if recovery does not occur if fewer than reverse_backoff_counter
    consecutive responses are within threshold.
    """
    # Initial response times to establish the baseline
    response_times = [0.1, 0.2, 0.15, 0.2, 0.18, 0.22, 0.19, 0.2, 0.25, 0.24]

    # Prepare time values for the baseline
    time_values, cumulative_time = _get_time_values(response_times)

    # Calculate expected percentile threshold time
    expected_percentile_time = _get_threshold_time(response_times, throttler)

    # Simulate a response above the threshold
    response_above_threshold = expected_percentile_time + 0.1
    time_values.append(cumulative_time)  # Start time of the above-threshold response
    cumulative_time += response_above_threshold
    time_values.append(cumulative_time)  # End time

    # Simulate fewer than reverse_backoff_counter consecutive below-threshold responses
    insufficient_responses = throttler.reverse_backoff_counter - 5

    for _ in range(insufficient_responses):
        response_below_threshold = expected_percentile_time - 0.05
        time_values.append(cumulative_time)
        cumulative_time += response_below_threshold
        time_values.append(cumulative_time)

    time_iter = iter(time_values)

    with patch('time.perf_counter', side_effect=lambda: next(time_iter)), patch('time.sleep'):
        # Establish baseline
        for _ in response_times:
            with throttler.process_response_time():
                pass

        # Trigger throttling
        with throttler.process_response_time():
            pass

        initial_rate = throttler._request_rate

        # Simulate responses below threshold but fewer than reverse_backoff_counter
        for _ in range(insufficient_responses):
            with throttler.process_response_time():
                pass

        assert throttler._request_rate == initial_rate, (
            f"Expected rate to remain at {initial_rate} due to insufficient consecutive responses, "
            f"but got {throttler._request_rate}"
        )
