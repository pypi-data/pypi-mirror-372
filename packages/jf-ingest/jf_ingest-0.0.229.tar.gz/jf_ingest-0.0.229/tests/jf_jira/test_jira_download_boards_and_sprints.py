import json
from contextlib import contextmanager
from typing import Optional
from unittest.mock import patch

import requests_mock

from jf_ingest.jf_jira.downloaders import download_boards_and_sprints
from tests.jf_jira.utils import (
    _register_jira_uri,
    get_fixture_file_data,
    get_jira_mock_connection,
)

# NOTE: Boards and Sprints DO NOT hit the normal API, they hit the /rest/agile/1.0/ endpoint


# Dummy data for testing
PROJECT_IDS = {'12','51','1001'}
PROJECT_ID_TO_BOARDS_MAP = {
    '12': [1, 2],
    '51': [3],
    '1001': [],
}

def _mock_board_or_sprint_endpoint(
    m: requests_mock.Mocker,
    fixture_file_path: str,
    is_sprint_endpoint: bool,
    board_id: Optional[int] = None,
    project_ids: Optional[list[int]] = None,
):
    data_str = get_fixture_file_data(f"api_responses/{fixture_file_path}")
    data = json.loads(data_str)
    values = data["values"]
    total = data["total"]
    max_results = data["maxResults"]

    if total != len(values):
        # Fact check that we have good fixture data
        raise Exception(
            f"Inputted data error! Fixture {fixture_file_path} has a reported total size of {total}, but there are {len(values)} in the values payload!"
        )

    terminator_payload_str = get_fixture_file_data("api_responses/boards_empty_agile_payload.json")

    if is_sprint_endpoint:
        if board_id == None:
            raise Exception(
                f"When using the is_sprint_endpoint endpoint, board_id is a required argument!"
            )
        endpoint_base = f"board/{board_id}/sprint"
    else:
        endpoint_base = "board"
    _register_jira_uri(
        m,
        endpoint=f"{endpoint_base}?maxResults={max_results}",
        return_value=data_str,
        use_agile_endpoint=True,
    )
    _register_jira_uri(
        m,
        endpoint=f"{endpoint_base}?maxResults={max_results}&startAt={total}",
        return_value=terminator_payload_str,
        use_agile_endpoint=True,
    )
    for project_id in PROJECT_IDS:
        data['values'] = [
            board for board in values if board["id"] in PROJECT_ID_TO_BOARDS_MAP[project_id]
        ]
        _register_jira_uri(
            m,
            endpoint=f"{endpoint_base}?projectKeyOrId={project_id}&maxResults={max_results}",
            return_value=json.dumps(data),
            use_agile_endpoint=True,
        )
        _register_jira_uri(
            m,
            endpoint=f"{endpoint_base}?projectKeyOrId={project_id}&maxResults={max_results}&startAt={len(data['values'])}",
            return_value=terminator_payload_str,
            use_agile_endpoint=True,
        )

    return values


def _mark_board_as_does_not_support_sprints(
    m: requests_mock.Mocker, board_id: int, status_code: int
):
    sprints_not_supported_payload = get_fixture_file_data(
        f"api_responses/boards_sprints_not_supported.json"
    )

    _register_jira_uri(
        m,
        endpoint=f"board/{board_id}/sprint?maxResults=50",
        return_value=sprints_not_supported_payload,
        use_agile_endpoint=True,
        status_code=status_code,
    )


@contextmanager
def _mock_boards_and_sprints(
    jira_status_code_for_board_does_not_support_sprints: int = 400,
):
    with requests_mock.Mocker() as m:
        boards_from_api = _mock_board_or_sprint_endpoint(
            m, fixture_file_path="boards.json", is_sprint_endpoint=False
        )
        boards_sprints_for_board_1 = _mock_board_or_sprint_endpoint(
            m,
            fixture_file_path="boards_sprints_for_board_1.json",
            is_sprint_endpoint=True,
            board_id=1,
        )
        _mark_board_as_does_not_support_sprints(
            m,
            board_id=2,
            status_code=jira_status_code_for_board_does_not_support_sprints,
        )
        _mark_board_as_does_not_support_sprints(
            m,
            board_id=3,
            status_code=jira_status_code_for_board_does_not_support_sprints,
        )
        yield (boards_from_api, boards_sprints_for_board_1)


def test_download_boards_and_not_sprints():
    with _mock_boards_and_sprints() as board_and_sprint_tuple:
        boards_from_api = board_and_sprint_tuple[0]

        boards, sprints, links = download_boards_and_sprints(
            get_jira_mock_connection(), download_sprints=False
        )

        # Assert that we are properly parsing and getting all board data
        for board in boards:
            assert board in boards_from_api

        # Assert we are not getting sprint data, or links data
        assert sprints == []
        assert links == []


def test_download_board_with_sprints():
    with _mock_boards_and_sprints() as board_and_sprint_tuple:
        boards_from_api = board_and_sprint_tuple[0]
        boards_sprints_for_board_1 = board_and_sprint_tuple[1]

        # MOCK SPRINT DATA FOR BOARD
        boards, sprints, links = download_boards_and_sprints(
            get_jira_mock_connection(), download_sprints=True
        )

        assert boards_from_api == boards
        # Assert we are not getting sprint data, or links data
        assert sprints == boards_sprints_for_board_1
        links_from_api = [
            {
                "board_id": 1,
                "sprint_ids": [sprint["id"] for sprint in boards_sprints_for_board_1],
            },
            {"board_id": 2, "sprint_ids": []},
            {"board_id": 3, "sprint_ids": []},
        ]

        for link in links:
            assert link in links_from_api

def test_download_board_with_sprints_jira_throws_404():
    with _mock_boards_and_sprints(
        jira_status_code_for_board_does_not_support_sprints=404
    ) as board_and_sprint_tuple:
        boards_from_api = board_and_sprint_tuple[0]
        boards_sprints_for_board_1 = board_and_sprint_tuple[1]

        # MOCK SPRINT DATA FOR BOARD
        boards, sprints, links = download_boards_and_sprints(
            get_jira_mock_connection(), download_sprints=True
        )

        assert boards_from_api == boards
        # Assert we are not getting sprint data, or links data
        assert sprints == boards_sprints_for_board_1
        links_from_api = [
            {
                "board_id": 1,
                "sprint_ids": [sprint["id"] for sprint in boards_sprints_for_board_1],
            },
            {"board_id": 2, "sprint_ids": []},
            {"board_id": 3, "sprint_ids": []},
        ]

        for link in links:
            assert link in links_from_api


def test_download_board_with_sprints_jira_throws_500():
    with _mock_boards_and_sprints(
        jira_status_code_for_board_does_not_support_sprints=500
    ) as board_and_sprint_tuple, patch('jf_ingest.utils.time.sleep', return_value=0):
        boards_from_api = board_and_sprint_tuple[0]
        boards_sprints_for_board_1 = board_and_sprint_tuple[1]

        # MOCK SPRINT DATA FOR BOARD
        boards, sprints, links = download_boards_and_sprints(
            get_jira_mock_connection(), download_sprints=True
        )

        assert boards_from_api == boards
        # Assert we are not getting sprint data, or links data
        assert sprints == boards_sprints_for_board_1
        links_from_api = [
            {
                "board_id": 1,
                "sprint_ids": [sprint["id"] for sprint in boards_sprints_for_board_1],
            },
            {"board_id": 2, "sprint_ids": []},
            {"board_id": 3, "sprint_ids": []},
        ]

        for link in links:
            assert link in links_from_api


def test_download_board_with_project_filtering_smoke_test():
    with _mock_boards_and_sprints() as board_and_sprint_tuple, patch('jf_ingest.utils.time.sleep', return_value=0):
        boards_from_api = board_and_sprint_tuple[0]
        boards_sprints_for_board_1 = board_and_sprint_tuple[1]

        # MOCK SPRINT DATA FOR BOARD
        boards, sprints, links = download_boards_and_sprints(
            get_jira_mock_connection(), download_sprints=True, filter_boards_by_projects=PROJECT_IDS
        )

        boards.sort(key=lambda x: x["id"])
        boards_from_api.sort(key=lambda x: x["id"])
        assert len(boards_from_api) == len(boards)
        assert boards_from_api == boards
        # Assert we are not getting sprint data, or links data
        assert sprints == boards_sprints_for_board_1
        links_from_api = [
            {
                "board_id": 1,
                "sprint_ids": [sprint["id"] for sprint in boards_sprints_for_board_1],
            },
            {"board_id": 2, "sprint_ids": []},
            {"board_id": 3, "sprint_ids": []},
        ]

        for link in links:
            assert link in links_from_api

def test_download_board_with_project_filtering_by_projects():
    with _mock_boards_and_sprints() as board_and_sprint_tuple, patch('jf_ingest.utils.time.sleep', return_value=0):

        def _test_filter_by_board(project_id_set: set[str]) -> list[dict]:
            boards, _, _ = download_boards_and_sprints(
                get_jira_mock_connection(), download_sprints=False, filter_boards_by_projects=project_id_set
            )

            board_ids = []
            for proj_id in project_id_set:
                board_ids.extend(PROJECT_ID_TO_BOARDS_MAP[proj_id])
            assert len(boards) == len(board_ids)
            for board in boards:
                assert board["id"] in board_ids

            return boards

        _test_filter_by_board({"12"})
        _test_filter_by_board({"12", "51"})
        _test_filter_by_board({"51"})

        all_boards = _test_filter_by_board({"12", "51", "1001"})
        assert len(all_boards) == 3

        no_boards = _test_filter_by_board({"1001"})
        assert len(no_boards) == 0
