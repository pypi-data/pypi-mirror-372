import logging

from jf_ingest import logging_helper

logger = logging.getLogger(__name__)


def _count_log_records_by_message(records):
    record_message_counts = {r.message: 0 for r in records}
    for record in records:
        record_message_counts[record.message] += 1

    return record_message_counts


def test_log_entry_exit_log_level(caplog):
    informational_log_message = "This is a test log"

    @logging_helper.log_entry_exit()
    def _test_function_for_wrapper():
        logging.info(informational_log_message)

    ########################################################################
    # TEST WITH LEVEL SET AT INFO (NO DEBUG MESSAGES SHOULD SHOW)
    ########################################################################
    caplog.set_level(level=logging.INFO)
    _test_function_for_wrapper()

    record_message_counts = _count_log_records_by_message(caplog.records)

    # Assert that the starting and ending log got called exactly once
    assert f"{_test_function_for_wrapper.__name__}: Starting" not in record_message_counts.keys()
    assert f"{_test_function_for_wrapper.__name__}: Ending" not in record_message_counts.keys()
    # Assert that the informational message appeared twice
    assert record_message_counts[informational_log_message] == 1
    assert len(caplog.records) == 1

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG
    ########################################################################
    # Reset caplog
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)
    _test_function_for_wrapper()

    record_message_counts = _count_log_records_by_message(caplog.records)

    # Assert that the starting and ending log got called exactly once
    assert record_message_counts[f"{_test_function_for_wrapper.__name__}: Starting"] == 1
    assert record_message_counts[f"{_test_function_for_wrapper.__name__}: Ending"] == 1
    # Assert that the informational message appeared twice
    assert record_message_counts[informational_log_message] == 1

    # Assert that duration log is present
    assert len([r for r in caplog.records if "Execution took" in r.message]) == 1

    # Assert total number of logs
    assert len(caplog.records) == 4


def test_log_for_loop_iters_info_level(caplog):
    total_iters = 10
    log_every = 1

    ########################################################################
    # TEST WITH LEVEL SET AT INFO (NO DEBUG MESSAGES SHOULD SHOW)
    ########################################################################
    caplog.set_level(level=logging.INFO)
    logged_information_messages = []

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    assert len(record_message_counts.keys()) == total_iters

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG
    ########################################################################
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    # For every iter, we should have an additional 2
    assert len(record_message_counts.keys()) == (total_iters + (total_iters * 2))

    ########################################################################
    # TEST WITH LEVEL SET AT DEBUG (log every iter set to 2)
    ########################################################################
    log_every = 2
    caplog.clear()
    caplog.set_level(level=logging.DEBUG)

    for i in range(10):
        with logging_helper.log_loop_iters("test_log_loop_iters", i, log_every):
            info_message = f"Iter {i}"
            logger.info(info_message)
            logged_information_messages.append(info_message)

    record_message_counts = _count_log_records_by_message(caplog.records)

    # For every 2 iters, we should have an additional 2 debug logs
    assert len(record_message_counts.keys()) == (total_iters + (total_iters))


def test_log_standard_error_smoke_test(caplog):
    caplog.set_level(logging.WARNING)
    msg_args = ["TEST MESSAGE"]
    error_code = 0000
    logging_helper.log_standard_error(
        level=logging.WARNING, error_code=error_code, msg_args=msg_args
    )
    assert len(caplog.records) == 1
    assert caplog.records[0].message == logging_helper.generate_standard_error_msg(
        error_code=error_code, msg_args=msg_args
    )


def test_send_to_agent_log_basic(caplog):
    caplog.set_level(logging.DEBUG)
    info_log_message_for_agent_log = 'This is a normal INFO message for only the Agent log'
    info_log_message_for_not_agent_log = 'This is a normal INFO message not just for agent log'
    logging_helper.send_to_agent_log_file(info_log_message_for_agent_log)
    logger.info(info_log_message_for_not_agent_log)

    # Sanity check
    assert len(caplog.records) == 2
    # Assert that the log that is tagged as an agent log file log should be one
    assert caplog.records[0].message == info_log_message_for_agent_log
    assert caplog.records[0].__dict__[logging_helper.AGENT_LOG_TAG] == True
    assert caplog.records[0].levelno == logging.INFO  # Assert default level is INFO
    # Assert that the log that should not be tagged as an agent log file log is not tagged as one
    assert caplog.records[1].message == info_log_message_for_not_agent_log
    assert logging_helper.AGENT_LOG_TAG not in caplog.records[1].__dict__


def test_send_to_agent_log_with_varying_level(caplog):
    caplog.set_level(logging.DEBUG)
    logging_level = logging.ERROR
    info_log_message_for_agent_log = (
        f'This is a normal {logging_level} message for only the Agent log'
    )
    info_log_message_for_not_agent_log = (
        f'This is a normal {logging_level} message not just for agent log'
    )
    logging_helper.send_to_agent_log_file(info_log_message_for_agent_log, level=logging_level)
    logger.error(info_log_message_for_not_agent_log)

    # Sanity check
    assert len(caplog.records) == 2
    # Assert that the log that is tagged as an agent log file log should be one
    assert caplog.records[0].message == info_log_message_for_agent_log
    assert caplog.records[0].__dict__[logging_helper.AGENT_LOG_TAG] == True
    assert caplog.records[0].levelno == logging_level  # Assert we retain level
    # Assert that the log that should not be tagged as an agent log file log is not tagged as one
    assert caplog.records[1].message == info_log_message_for_not_agent_log
    assert logging_helper.AGENT_LOG_TAG not in caplog.records[1].__dict__


def test_send_to_agent_log_with_extra_data(caplog):
    caplog.set_level(logging.DEBUG)
    logging_level = logging.DEBUG
    extra_field_key = 'foo'
    extra_field_value = 'bar'
    extra_field_key_two = 10000
    extra_field_value_two = 1234
    extras = {extra_field_key: extra_field_value, extra_field_key_two: extra_field_value_two}
    info_log_message_for_agent_log = 'TEST LOG WITH EXTRAS'

    # EXECUTE FUNCTION
    logging_helper.send_to_agent_log_file(
        info_log_message_for_agent_log, level=logging_level, extra=extras
    )

    # Sanity check
    assert len(caplog.records) == 1
    agent_record = caplog.records[0]
    # Assert that the log that is tagged as an agent log file log should be one
    assert agent_record.message == info_log_message_for_agent_log
    assert agent_record.levelno == logging_level  # Assert we retain level
    # Assert extras are there
    log_extras = agent_record.__dict__
    assert (
        log_extras[logging_helper.AGENT_LOG_TAG] == True
    )  # ALWAYS RETAIN THAT THIS IS AN AGENT LOG RECORD
    # Assert we also have the extra extra data
    assert log_extras[extra_field_key] == extra_field_value
    assert log_extras[extra_field_key_two] == extra_field_value_two
