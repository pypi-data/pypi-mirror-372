import json
import logging
import math
import sys
from ast import parse
from datetime import datetime
from unittest.mock import patch

import pytest
import requests
from jira import JIRAError
import requests_mock

from jf_ingest.config import IssueMetadata
from jf_ingest.utils import (
    RETRY_EXPONENT_BASE,
    RetryLimitExceeded,
    batch_iterable,
    batch_iterable_by_bytes_size,
    format_date_to_jql,
    get_object_bytes_size,
    get_wait_time,
    hash_filename,
    parse_gitlab_api_version,
    retry_for_status,
)

logger = logging.getLogger(__name__)

MOCK_RETRY_AFTER_TIME = 12345


class MockJiraErrorResponseWithRetryAfterAsInt:
    headers = {"Retry-After": MOCK_RETRY_AFTER_TIME}


class MockJiraErrorResponseWithRetryAfterAsStr:
    headers = {"Retry-After": str(MOCK_RETRY_AFTER_TIME)}


class MockJiraErrorResponseWithZeroRetryAfter:
    headers = {"Retry-After": 0}


class MockJiraErrorResponseWithNonIntRetryAfter:
    headers = {"Retry-After": "CAT"}


MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_INT = JIRAError(
    status_code=429,
    text="This is a spoofed Jira Error",
    response=MockJiraErrorResponseWithRetryAfterAsInt(),
)
MOCKED_504_JIRA_ERROR_WITH_RETRY_AS_INT = JIRAError(
    status_code=504,
    text="This is a spoofed Jira Error",
    response=MockJiraErrorResponseWithRetryAfterAsInt(),
)
MOCKED_404_JIRA_ERROR_WITH_RETRY_AS_INT = JIRAError(
    status_code=404,
    text="This is a spoofed Jira Error",
    response=MockJiraErrorResponseWithRetryAfterAsInt(),
)
MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_STR = JIRAError(
    status_code=429,
    text="This is a spoofed Jira Error",
    response=MockJiraErrorResponseWithRetryAfterAsStr(),
)

MOCKED_429_JIRA_ERROR_RETRY_AFTER_IS_ZERO = JIRAError(
    status_code=429,
    text="This is a spoofed Jira Error with Retry After set to 0",
    response=MockJiraErrorResponseWithZeroRetryAfter(),
)

MOCKED_429_JIRA_ERROR_RETRY_AFTER_IS_NOT_INT = JIRAError(
    status_code=429,
    text="This is a spoofed Jira Error with Retry After set to a non int",
    response=MockJiraErrorResponseWithNonIntRetryAfter(),
)


def test_get_default_wait_time():
    # Get Default Wait Times
    for retry_num in range(0, 10):
        assert get_wait_time(e=None, retries=retry_num) == RETRY_EXPONENT_BASE**retry_num


def test_get_wait_times_for_retry_error():
    # Test when we have a valid Error
    mock_error = MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_INT

    for retry_num in range(0, 5):
        logger.info(f"Retry number {retry_num}...")
        assert get_wait_time(mock_error, retries=retry_num) == MOCK_RETRY_AFTER_TIME


def test_get_wait_times_for_retry_error_when_retry_is_str():
    # Test when we have a valid Error
    mock_error = MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_STR

    for retry_num in range(0, 5):
        logger.info(f"Retry number {retry_num}...")
        assert get_wait_time(mock_error, retries=retry_num) == MOCK_RETRY_AFTER_TIME


def test_get_wait_times_for_retry_error_zero():
    # Test when we have a valid Error
    mock_error = MOCKED_429_JIRA_ERROR_RETRY_AFTER_IS_ZERO

    for retry_num in range(0, 10):
        logger.info(f"Retry number {retry_num}...")
        expected_wait_time = RETRY_EXPONENT_BASE**retry_num
        # Retry times SHOULD NEVER be zero
        assert get_wait_time(mock_error, retries=retry_num) != 0
        assert get_wait_time(mock_error, retries=retry_num) == expected_wait_time


def test_get_wait_times_for_retry_error_non_zero():
    # Test when we have a valid Error
    mock_error = MOCKED_429_JIRA_ERROR_RETRY_AFTER_IS_NOT_INT

    for retry_num in range(0, 10):
        logger.info(f"Retry number {retry_num}...")
        expected_wait_time = RETRY_EXPONENT_BASE**retry_num
        # Retry times SHOULD NEVER be zero
        assert get_wait_time(mock_error, retries=retry_num) != 0
        assert get_wait_time(mock_error, retries=retry_num) == expected_wait_time


def test_get_wait_time_for_non_retry_error():
    mock_non_retry_exception = Exception()
    retries = 5
    assert get_wait_time(mock_non_retry_exception, retries=retries) == RETRY_EXPONENT_BASE**retries


def test_retry_for_status_timeout():
    def always_raise_429():
        raise MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_INT

    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        with pytest.raises(RetryLimitExceeded):
            retry_for_status(always_raise_429)

        try:
            retry_for_status(always_raise_429)
        except RetryLimitExceeded:
            m.assert_called_with(MOCK_RETRY_AFTER_TIME)


def test_retry_for_status_retry_works_429():
    arg_dict = {"retry_count": 0}
    success_message = "Success!"

    def raise_429_three_times():
        if arg_dict["retry_count"] == 3:
            return success_message
        else:
            arg_dict["retry_count"] += 1
            raise MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_INT

    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        assert retry_for_status(raise_429_three_times) == success_message
        m.assert_called_with(MOCK_RETRY_AFTER_TIME)
        
def test_session_get_with_retry_for_status(requests_mock: requests_mock.Mocker):
    fake_url = 'https://a-fake-url.com'
    retry_count = 10
    requests_mock.get(url=fake_url, status_code=429)
    
    with patch("jf_ingest.utils.time.sleep", return_value=0):
        session = requests.Session()
        f = session.get
        with pytest.raises(RetryLimitExceeded):
            retry_for_status(f, url=fake_url, max_retries_for_retry_for_status=retry_count)
            assert requests_mock.call_count == retry_count
        
def test_session_post_with_retry_for_status(requests_mock: requests_mock.Mocker):
    fake_url = 'https://a-fake-url.com'
    retry_count = 10
    test_body = {'fake': 'data'}
    requests_mock.post(url=fake_url, json=test_body, status_code=429)
    
    with patch("jf_ingest.utils.time.sleep", return_value=0):
        session = requests.Session()
        f = session.post
        with pytest.raises(RetryLimitExceeded):
            retry_for_status(f, url=fake_url, json=test_body, max_retries_for_retry_for_status=retry_count)
            assert requests_mock.call_count == retry_count
            

def test_session_get_with_retry_for_status_for_non_retryable(requests_mock: requests_mock.Mocker):
    fake_url = 'https://a-fake-url.com'
    retry_count = 10
    requests_mock.get(url=fake_url, status_code=401)
    
    with patch("jf_ingest.utils.time.sleep", return_value=0):
        session = requests.Session()
        f = session.get
        with pytest.raises(requests.exceptions.HTTPError):
            retry_for_status(f, url=fake_url, max_retries_for_retry_for_status=retry_count)
            assert requests_mock.call_count == 1


def test_retry_for_status_retry_works_504():
    arg_dict = {"retry_count": 0}
    success_message = "Success!"

    def raise_504_three_times():
        if arg_dict["retry_count"] == 3:
            return success_message
        else:
            arg_dict["retry_count"] += 1
            raise MOCKED_504_JIRA_ERROR_WITH_RETRY_AS_INT

    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        assert retry_for_status(raise_504_three_times) == success_message
        m.assert_called_with(MOCK_RETRY_AFTER_TIME)


def test_retry_for_status_retry_works_custom_error_code_list():
    def always_raise_429():
        raise MOCKED_429_JIRA_ERROR_WITH_RETRY_AS_INT

    arg_dict = {"retry_count": 0}
    success_message = "Success!"

    some_error_codes = []
    some_error_codes.extend([400, 500])
    some_error_codes.append(404)

    def raise_404_three_times(test_arg: str):
        assert bool(test_arg)
        if arg_dict["retry_count"] == 3:
            return success_message
        else:
            arg_dict["retry_count"] += 1
            raise MOCKED_404_JIRA_ERROR_WITH_RETRY_AS_INT

    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        assert (
            retry_for_status(
                raise_404_three_times, 'test_input', statuses_to_retry=some_error_codes
            )
            == success_message
        )
        m.assert_called_with(MOCK_RETRY_AFTER_TIME)

    with pytest.raises(JIRAError):
        # Assert that we raise codes that are not included
        retry_for_status(always_raise_429, statuses_to_retry=some_error_codes)


def test_retry_for_status_with_generic_error():
    def raise_non_429():
        raise Exception("Generic Error Testing")

    with pytest.raises(Exception):
        retry_for_status(raise_non_429)


def test_retry_for_status_retry_works_readtimeout():
    arg_dict = {"retry_count": 0}
    success_message = "Success!"

    def raise_readtimeout_three_times():
        if arg_dict["retry_count"] == 3:
            return success_message
        else:
            arg_dict["retry_count"] += 1
            raise requests.exceptions.ReadTimeout()

    expected_wait_time = get_wait_time(None, retries=2)
    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        assert retry_for_status(raise_readtimeout_three_times) == success_message
        m.assert_called_with(expected_wait_time)


def test_retry_for_status_retry_works_custom_exception():
    arg_dict = {"retry_count": 0}
    success_message = "Success!"

    class CustomException(Exception):
        pass

    def raise_readtimeout_three_times():
        if arg_dict["retry_count"] == 1:
            return success_message
        else:
            arg_dict["retry_count"] += 1
            raise CustomException()

    expected_wait_time = get_wait_time(None, retries=0)
    with patch("jf_ingest.utils.time.sleep", return_value=0) as m:
        assert (
            retry_for_status(raise_readtimeout_three_times, exceptions_to_retry=(CustomException,))
            == success_message
        )
        m.assert_called_with(expected_wait_time)


def test_retry_for_status_with_jira_non_caught_error():
    def raise_401():
        raise JIRAError(text="Generic Error Testing", status_code=401)

    def raise_429():
        raise JIRAError(text="Generic Error Testing", status_code=429)

    with pytest.raises(JIRAError):
        retry_for_status(raise_401)

    with pytest.raises(JIRAError):
        retry_for_status(raise_429(), status_codes_to_retry=[])

def test_retry_for_status_with_generic_error_raise_or_not():
    class NewExceptionType(Exception):
        pass
    def raise_generic_exception():
        raise NewExceptionType("Generic Error Testing")

    with pytest.raises(NewExceptionType), patch('time.sleep', return_value=0):
        retry_for_status(raise_generic_exception, retry_on_any_exception=False)
    
    
    with pytest.raises(RetryLimitExceeded), patch('time.sleep', return_value=0):
        retry_for_status(raise_generic_exception, retry_on_any_exception=True)


def test_batch_iterable():
    total_data_size = 85926
    batch_size = 62
    data = [i for i in range(total_data_size)]

    recompiled_batches = []
    for batch in batch_iterable(data, batch_size=batch_size):
        # Assert we are getting proper batch sizes
        assert len(batch) <= batch_size
        recompiled_batches.extend(batch)

    # Assert we got ALL the data
    assert len(recompiled_batches) == total_data_size

    # Assert that data is returned matching and in order
    for i in range(total_data_size):
        assert data[i] == recompiled_batches[i]


def test_batch_iterable_by_bytes_size():
    number_of_chars = 41234
    data = ['a' for i in range(number_of_chars)]
    total_data_size_in_bytes = sum(sys.getsizeof(i) for i in data)

    # NOTE: This values should be greater than 50
    batch_bytes_size = 500

    batch_numbers = 0
    recompiled_batches = []
    for batch in batch_iterable_by_bytes_size(data, batch_byte_size=batch_bytes_size):
        # Assert we are getting proper batch sizes
        assert sys.getsizeof(batch) > 0
        assert sys.getsizeof(batch) <= batch_bytes_size
        batch_numbers += 1
        recompiled_batches.extend(batch)

    # Assert we got ALL the data
    assert len(recompiled_batches) == len(data)
    assert batch_numbers == math.ceil(total_data_size_in_bytes / batch_bytes_size)


def test_get_object_bytes_size():
    test_object = {'a': 1, 'b': 2, 'c': 3}

    object_size = get_object_bytes_size(test_object)

    manually_derived_size = 0
    for key in test_object.keys():
        manually_derived_size += sys.getsizeof(key)
        manually_derived_size += sys.getsizeof(test_object[key])
    assert manually_derived_size == object_size


def test_get_object_bytes_size_nested_object():
    test_object = {'a': 1, 'b': 2, 'c': {'d': 4}}

    object_size = get_object_bytes_size(test_object)

    manually_derived_size = 0
    for key in test_object.keys():
        manually_derived_size += sys.getsizeof(key)
        value = test_object[key]
        if type(value) == dict:
            for _key in value.keys():
                manually_derived_size += sys.getsizeof(_key)
                _value = value[_key]
                manually_derived_size += sys.getsizeof(_value)
        else:
            manually_derived_size += sys.getsizeof(value)

    assert manually_derived_size == object_size


def test_format_date_to_jql():
    min_datetime = datetime.min
    assert format_date_to_jql(min_datetime) == '"0001-01-01"'

    _american_revolution_datetime = datetime(1776, 7, 4)
    assert format_date_to_jql(_american_revolution_datetime) == '"1776-07-04"'

    _datetime_pre_unix_epoch_time = datetime(1969, 12, 31)
    assert format_date_to_jql(_datetime_pre_unix_epoch_time) == '"1969-12-31"'

    _datetime_after_unix_epoch_time = datetime(2003, 3, 12)
    assert format_date_to_jql(_datetime_after_unix_epoch_time) == '"2003-03-12"'

    _datetime_after_unix_epoch_time = datetime(2024, 12, 18)
    assert format_date_to_jql(_datetime_after_unix_epoch_time) == '"2024-12-18"'

    _future_datetime = datetime(3333, 1, 4)
    assert format_date_to_jql(_future_datetime) == '"3333-01-04"'


def test_issue_metadata_serializer_single_object():
    # Create an IssueMetadata Object with values we can
    # verify after we do a "round trip" of serializing
    # and deserializing
    id = "1"
    key = "PROJ-1"
    _datetime = datetime(2023, 12, 29)
    epic_link_field_issue_key = "EPIC_LINK_FIELD_ISSUE_KEY"
    parent_field_issue_key = "PARENT_FIELD_ISSUE_KEY"
    issue_metadata = IssueMetadata(
        id=id,
        key=key,
        updated=_datetime,
        epic_link_field_issue_key=epic_link_field_issue_key,
        parent_field_issue_key=parent_field_issue_key,
    )

    # Serialize the object to a string
    serialized_issue_metadata = IssueMetadata.to_json_str(issue_metadata)
    assert type(serialized_issue_metadata) == str

    # Deserialize it back to memory, verify that it is the proper type
    deserialized_issue_metadata = IssueMetadata.from_json(serialized_issue_metadata)
    assert type(deserialized_issue_metadata) == IssueMetadata

    # Assert that all the data is the same after a serialization/deserialization round trip
    assert deserialized_issue_metadata.id == id
    assert deserialized_issue_metadata.key == key
    assert deserialized_issue_metadata.updated == _datetime
    assert deserialized_issue_metadata.epic_link_field_issue_key == epic_link_field_issue_key
    assert deserialized_issue_metadata.parent_field_issue_key == parent_field_issue_key


def test_issue_metadata_serializer_list_of_objects():
    # Generate a list of IssueMetadata to serialize/deserialize
    issue_metadata_list: list[IssueMetadata] = []
    lower_bound_day = 1
    upper_bound_day = 30
    for day in range(lower_bound_day, upper_bound_day):
        id = f"{day}"
        key = f"PROJ-{day}"
        _datetime = datetime(2023, 12, day)
        epic_link_field_issue_key = f"EPIC_LINK_FIELD_ISSUE_KEY_{day}"
        parent_field_issue_key = f"PARENT_FIELD_ISSUE_KEY_{day}"

        issue_metadata_list.append(
            IssueMetadata(
                id=id,
                key=key,
                updated=_datetime,
                epic_link_field_issue_key=epic_link_field_issue_key,
                parent_field_issue_key=parent_field_issue_key,
            )
        )

    # Verify we can serialize it as a list
    serialized_issue_metadata_list = IssueMetadata.to_json_str(issue_metadata_list)
    assert type(serialized_issue_metadata_list) == str

    # Verify that we can deserialize it as a list of the same size and of the same type
    deserialized_issue_metadata_list = IssueMetadata.from_json(serialized_issue_metadata_list)
    assert type(deserialized_issue_metadata_list) == list
    assert len(deserialized_issue_metadata_list) == len(issue_metadata_list)
    for item in deserialized_issue_metadata_list:
        assert type(item) == IssueMetadata

    for i in range(len(issue_metadata_list)):
        issue_metadata_pre = issue_metadata_list[i]
        issue_metadata_post = deserialized_issue_metadata_list[i]

        assert issue_metadata_pre.id == issue_metadata_post.id
        assert issue_metadata_pre.key == issue_metadata_post.key
        assert issue_metadata_pre.updated == issue_metadata_post.updated
        assert (
            issue_metadata_pre.epic_link_field_issue_key
            == issue_metadata_post.epic_link_field_issue_key
        )
        assert (
            issue_metadata_pre.parent_field_issue_key == issue_metadata_post.parent_field_issue_key
        )


def test_hash_files():
    filepath = 'a/path/to/a/file.py'
    hashed_filepath = hash_filename(filepath)
    assert hashed_filepath == '0cc175b9c0f1/d6fe1d0be634/01b6e20344b6/0cc175b9c0f1/02b202aa0962.py'

    # Test when file has additional . in it
    filepath = 'a/path/to.a/file.py'
    hashed_filepath = hash_filename(filepath)
    assert hashed_filepath == '0cc175b9c0f1/d6fe1d0be634/18449aad14e9/02b202aa0962.py'

    # Test when file has a bunch of additional . in it
    filepath = 'a.path/to.a/file.py'
    hashed_filepath = hash_filename(filepath)
    assert hashed_filepath == '8bd1e22aeb9f/18449aad14e9/02b202aa0962.py'

def test_parse_gitlab_api_version():
    versions_to_test = ['17.4.0', '17.4.0-pre', '17.4.0-ee', '17-stuff.4-random.0-things']
    for version_to_test in versions_to_test:
        assert parse_gitlab_api_version(version_to_test) == '17.4.0'
