import datetime
import json
import string
from contextlib import contextmanager

import pytest
import requests_mock

from jf_ingest.jf_jira.downloaders import (
    _get_all_users_for_gdpr_active_instance,
    _scrub_jira_users,
    _search_users_by_letter,
    _should_augment_email,
    augment_jira_users_with_email,
    download_users,
    get_searchable_jira_letters,
    search_users,
)
from jf_ingest.jf_jira.exceptions import NoJiraUsersFoundException
from jf_ingest.utils import batch_iterable
from tests.jf_jira.utils import _register_jira_uri, get_jira_mock_connection

DEFAULT_PAGE_SIZE = 1000


def _generate_spoofed_user_data(user_count: int, char: str = "default", gdpr_active: bool = True):
    return [
        {
            f"{'accountId' if gdpr_active else 'key'}": f"{char}_{x}",
            "emailAddress": f"{char}_email_{x}@emailAddress.com",
        }
        for x in range(0, user_count)
    ]


@contextmanager
def _spoof_gdpr_server(page_size: int, total_users: int, server_page_size: int = DEFAULT_PAGE_SIZE):
    # Test with incremental paging
    with requests_mock.Mocker() as m:
        # SET UP MOCKED USER DATA
        lower_index = 0
        user_chunk = []
        user_data = _generate_spoofed_user_data(total_users)
        for user_chunk in batch_iterable(user_data, batch_size=page_size):
            _register_jira_uri(
                m,
                f"users/search?startAt={lower_index}&maxResults={page_size}",
                json.dumps(user_chunk),
            )
            lower_index += len(user_chunk)
        # Get last page of data
        _register_jira_uri(
            m,
            f"users/search?startAt={total_users}&maxResults={page_size}",
            json.dumps([]),
        )
        yield user_data


@contextmanager
def _mock_search_by_user_api_that_can_page(
    test_data: dict, page_size: int, returned_server_page_size: int = DEFAULT_PAGE_SIZE
):
    with requests_mock.Mocker() as m:
        for letter in get_searchable_jira_letters():
            # Load up empty values for every letter as a baseline
            _register_jira_uri(
                m,
                f"user/search?startAt=0&maxResults={page_size}&includeActive=True&includeInactive=True&username={letter}",
                "[]",
            )

        for char, data in test_data.items():
            # Overwrite the letter a to return results
            start_at = 0
            for user_batch in batch_iterable(data, returned_server_page_size):
                _register_jira_uri(
                    m,
                    f"user/search?startAt={start_at}&maxResults={page_size}&includeActive=True&includeInactive=True&username={char}",
                    json.dumps(user_batch),
                )
                start_at += len(user_batch)
            _register_jira_uri(
                m,
                f"user/search?startAt={start_at}&maxResults={page_size}&includeActive=True&includeInactive=True&username={char}",
                json.dumps([]),
            )

            for letter in get_searchable_jira_letters():
                # For the use case where we have exactly a pages worth of data, we
                # will iterate on the second character. To make this wrapper cover all
                # cases, set a baseline that sets every endpoint for a recursive depth of one (aa, ab, ac, ...)
                _register_jira_uri(
                    m,
                    f"user/search?startAt=0&maxResults={page_size}&includeActive=True&includeInactive=True&username={char}{letter}",
                    "[]",
                )
        yield


def test_search_users_data_less_than_page_size():
    test_data = {
        "a": _generate_spoofed_user_data(
            char="a", user_count=DEFAULT_PAGE_SIZE // 2, gdpr_active=False
        )
    }
    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )
        assert type(users) == list
        assert users == test_data["a"]


def test_search_users_data_exact_page_size():
    test_data = {
        "a": _generate_spoofed_user_data(char="a", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False)
    }
    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )
        assert type(users) == list
        assert users == test_data["a"]


def test_search_users_data_larger_than_page_size():
    test_data = {
        "a": _generate_spoofed_user_data(
            char="a",
            user_count=DEFAULT_PAGE_SIZE + (DEFAULT_PAGE_SIZE * 2 + 523),
            gdpr_active=False,
        )
    }
    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )
        assert type(users) == list
        assert len(users) == len(test_data["a"])
        assert users == test_data["a"]


def test_search_users_data_using_numeric():
    test_data = {
        "7": _generate_spoofed_user_data(
            char="7",
            user_count=DEFAULT_PAGE_SIZE - DEFAULT_PAGE_SIZE // 3,
            gdpr_active=False,
        )
    }
    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )
        assert type(users) == list
        assert len(users) == len(test_data["7"])
        assert users == test_data["7"]


def test_search_users_data_all_test_cases():
    test_data = {
        "a": _generate_spoofed_user_data(
            char="a", user_count=DEFAULT_PAGE_SIZE // 2, gdpr_active=False
        ),
        "f": _generate_spoofed_user_data(char="f", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False),
        "g": _generate_spoofed_user_data(
            char="g",
            user_count=DEFAULT_PAGE_SIZE + (DEFAULT_PAGE_SIZE * 2 + 523),
            gdpr_active=False,
        ),
        "7": _generate_spoofed_user_data(
            char="7", user_count=DEFAULT_PAGE_SIZE + 685, gdpr_active=False
        ),
    }

    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )

        assert type(users) == list

        flattened_test_data = []
        for data in test_data.values():
            flattened_test_data.extend(data)
        assert len(users) == len(flattened_test_data)
        assert users == flattened_test_data


def test_search_users_data_all_test_cases_and_special_server_batching():
    test_data = {
        "a": _generate_spoofed_user_data(
            char="a", user_count=DEFAULT_PAGE_SIZE // 2, gdpr_active=False
        ),
        "f": _generate_spoofed_user_data(char="f", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False),
        "g": _generate_spoofed_user_data(
            char="g",
            user_count=DEFAULT_PAGE_SIZE + (DEFAULT_PAGE_SIZE * 2 + 523),
            gdpr_active=False,
        ),
        "7": _generate_spoofed_user_data(
            char="7", user_count=DEFAULT_PAGE_SIZE + 685, gdpr_active=False
        ),
    }

    with _mock_search_by_user_api_that_can_page(
        test_data=test_data, page_size=DEFAULT_PAGE_SIZE, returned_server_page_size=100
    ):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )

        assert type(users) == list

        flattened_test_data = []
        for data in test_data.values():
            flattened_test_data.extend(data)
        assert len(users) == len(flattened_test_data)
        assert users == flattened_test_data


def test_search_users_data_recursive_case():
    test_data = {
        # exactly page size and nothing more
        "a": _generate_spoofed_user_data(char="a", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False),
        # Page size with some extra
        "b": _generate_spoofed_user_data(char="b", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False),
        "ba": _generate_spoofed_user_data(
            char="ba", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False
        ),
        "bar": _generate_spoofed_user_data(
            char="bar", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False
        ),
        "barb": _generate_spoofed_user_data(
            char="barb", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False
        ),
        # Test some numbers
        "4": _generate_spoofed_user_data(char="4", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False),
        "42": _generate_spoofed_user_data(
            char="42", user_count=DEFAULT_PAGE_SIZE, gdpr_active=False
        ),
        "426": _generate_spoofed_user_data(
            char="426",
            user_count=DEFAULT_PAGE_SIZE // 2,
            gdpr_active=False,
        ),
        "429": _generate_spoofed_user_data(
            char="4267",
            user_count=DEFAULT_PAGE_SIZE // 3,
            gdpr_active=False,
        ),
        "8": _generate_spoofed_user_data(
            char="8", user_count=DEFAULT_PAGE_SIZE // 4, gdpr_active=False
        ),
    }

    with _mock_search_by_user_api_that_can_page(test_data=test_data, page_size=DEFAULT_PAGE_SIZE):
        users = _search_users_by_letter(
            get_jira_mock_connection(),
            False,
            search_users_by_letter_email_domain=None,
            page_size=DEFAULT_PAGE_SIZE,
        )

        assert type(users) == list

        flattened_test_data = []
        for data in test_data.values():
            flattened_test_data.extend(data)
        assert len(users) == len(flattened_test_data)
        assert users == flattened_test_data


def test_get_all_users_for_gdpr_active_instance():
    page_size = DEFAULT_PAGE_SIZE
    total_users = 1668
    with _spoof_gdpr_server(page_size=page_size, total_users=total_users) as yielded_user_data:
        # Test 'base level' paging
        user_data = _get_all_users_for_gdpr_active_instance(
            get_jira_mock_connection(), page_size=page_size
        )
        assert len(user_data) == total_users

        # test wrapper function
        users_full_test = search_users(
            jira_connection=get_jira_mock_connection(),
            gdpr_active=True,
            page_size=page_size,
        )
        assert len(users_full_test) == total_users

        assert users_full_test == yielded_user_data

        users_check_augmentation = download_users(
            jira_basic_connection=get_jira_mock_connection(),
            jira_atlas_connect_connection=None,
            gdpr_active=True,
        )

        for user in users_check_augmentation:
            assert "email_pulled" in user


def test_get_all_users_for_gdpr_active_instance_with_non_max_results_paging():
    page_size = DEFAULT_PAGE_SIZE
    total_users = 1668
    with _spoof_gdpr_server(
        page_size=page_size, total_users=total_users, server_page_size=23
    ) as yielded_user_data:
        # Test 'base level' paging
        user_data = _get_all_users_for_gdpr_active_instance(
            get_jira_mock_connection(), page_size=page_size
        )
        assert len(user_data) == total_users

        # test wrapper function
        users_full_test = search_users(
            jira_connection=get_jira_mock_connection(),
            gdpr_active=True,
            page_size=page_size,
        )
        assert len(users_full_test) == total_users

        assert users_full_test == yielded_user_data

        users_check_augmentation = download_users(
            jira_basic_connection=get_jira_mock_connection(),
            jira_atlas_connect_connection=None,
            gdpr_active=True,
        )

        for user in users_check_augmentation:
            assert "email_pulled" in user


def test_get_searchable_jira_letters():
    # Due to some Jira API weirdness, we NEVER want to hit the API endpoint
    # with non letter or non digit characters.
    for letter in get_searchable_jira_letters():
        assert letter not in string.punctuation
        assert letter not in string.whitespace


def test_download_users():
    page_size = DEFAULT_PAGE_SIZE
    total_users = 1668
    with _spoof_gdpr_server(page_size=page_size, total_users=total_users) as yielded_user_data:
        # Test 'base level' paging
        user_data = download_users(
            jira_basic_connection=get_jira_mock_connection(),
            jira_atlas_connect_connection=None,
            gdpr_active=True,
            search_users_by_letter_email_domain=None,
            required_email_domains=[],
            is_email_required=False,
        )

        assert len(user_data) == total_users

        for user in user_data:
            assert "email_pulled" in user


def test_download_users_filter_by_required_email_domains():
    page_size = DEFAULT_PAGE_SIZE
    total_users = 1668
    with _spoof_gdpr_server(page_size=page_size, total_users=total_users):
        # Test 'base level' paging
        with pytest.raises(NoJiraUsersFoundException):
            user_data = download_users(
                jira_basic_connection=get_jira_mock_connection(),
                jira_atlas_connect_connection=None,
                gdpr_active=True,
                search_users_by_letter_email_domain=None,
                required_email_domains=["donotinclude.com"],
                is_email_required=False,
            )

        user_data = download_users(
            jira_basic_connection=get_jira_mock_connection(),
            jira_atlas_connect_connection=None,
            gdpr_active=True,
            search_users_by_letter_email_domain=None,
            required_email_domains=["emailAddress.com"],
            is_email_required=False,
        )
        assert len(user_data) == total_users


def test_scrub_users():
    mocked_users = [
        {"emailAddress": "test@domainOne.com"},
        {"emailAddress": "test@domainTwo.com"},
        {"emailAddress": "test@domainThree.com"},
    ]

    scrubbed_users = _scrub_jira_users(
        mocked_users,
        required_email_domains=["NoDomainFound.com"],
        is_email_required=False,
    )
    assert len(scrubbed_users) == 0

    scrubbed_users = _scrub_jira_users(
        mocked_users, required_email_domains=["domainOne.com"], is_email_required=False
    )
    assert len(scrubbed_users) == 1

    scrubbed_users = _scrub_jira_users(
        mocked_users,
        required_email_domains=["domainOne.com", "domainTwo.com"],
        is_email_required=False,
    )
    assert len(scrubbed_users) == 2

    scrubbed_users = _scrub_jira_users(
        mocked_users,
        required_email_domains=["domainOne.com", "domainTwo.com", "domainThree.com"],
        is_email_required=False,
    )
    assert len(scrubbed_users) == 3

    scrubbed_users = _scrub_jira_users(
        mocked_users, required_email_domains=[], is_email_required=False
    )
    assert len(scrubbed_users) == 3


def test_augment_with_email():
    # Test with incremental paging
    with requests_mock.Mocker() as m:
        jira_users = _generate_spoofed_user_data(55)
        augmented_users = set()
        for user in jira_users:
            account_id = user["accountId"]
            if _should_augment_email(user):
                _register_jira_uri(
                    m,
                    f"user/email?accountId={account_id}",
                    f'{{"accountId": "{account_id}", "email": "dummy@email.com"}}',
                )
                augmented_users.add(account_id)

        augment_jira_users_with_email(get_jira_mock_connection(), jira_users)
        for user in jira_users:
            if user["accountId"] in augmented_users:
                assert user["emailAddress"] == "dummy@email.com"
                assert "email_pulled" in user
                assert isinstance(user["email_pulled"], datetime.datetime)
