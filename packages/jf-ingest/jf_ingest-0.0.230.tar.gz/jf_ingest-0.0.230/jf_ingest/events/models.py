import enum
from dataclasses import dataclass
from typing import Optional


class EventState(str, enum.Enum):
    START = 'START'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'


class IngestType(str, enum.Enum):
    JIRA = 'JIRA_INGEST'
    GIT = 'GIT_INGEST'


class JiraIngestEventNames:
    GET_JIRA_DATA = 'get_jira_data'
    GET_JIRA_CONNECTION = 'get_jira_connection'
    GET_JIRA_PROJECTS = 'get_jira_projects'
    GET_JIRA_FIELDS = 'get_jira_fields'
    GET_JIRA_USERS = 'get_jira_users'
    GET_JIRA_RESOLUTIONS = 'get_jira_resolutions'
    GET_JIRA_ISSUE_TYPES = 'get_jira_issue_types'
    GET_JIRA_LINK_TYPES = 'get_jira_link_types'
    GET_JIRA_PRIORITIES = 'get_jira_priorities'
    GET_JIRA_STATUSES = 'get_jira_statuses'
    GET_JIRA_BOARD_AND_SPRINTS = 'get_jira_board_and_sprints'
    GET_JIRA_ISSUES = 'get_jira_issues'
    GET_JIRA_WORKLOGS = 'get_jira_worklogs'


class GitIngestionEventNames:
    GET_GIT_DATA = 'get_git_data'
    GET_GIT_ORGANIZATIONS = 'get_git_organizations'
    GET_GIT_USERS = 'get_git_users'
    GET_GIT_TEAMS = 'get_git_teams'
    GET_GIT_REPOS = 'get_git_repos'
    GET_GIT_BRANCHES = 'get_git_branches'
    GET_GIT_COMMITS = 'get_git_commits'
    GET_GIT_PULL_REQUESTS = 'get_git_pull_requests'


@dataclass
class IngestEvent:
    company_slug: str
    # This will be filled out by child classes
    ingest_type: IngestType
    # this should reflect what we're doing within the ingest component
    # "get_git_repos", "get_jira_issues", etc.
    event_name: str

    event_state: Optional[EventState] = None
    # Only applicable if is_error is true
    error_message: str = ''

    @staticmethod
    def from_dict(event: dict) -> Optional["IngestEvent"]:
        if ingest_type := event.get(f'ingest_type'):
            if ingest_type == IngestType.JIRA.value:
                return JiraIngestEvent(**event)
            elif ingest_type == IngestType.GIT.value:
                return GitIngestEvent(**event)
        return None


@dataclass
class JiraIngestEvent(IngestEvent):
    ingest_type = IngestType.JIRA


@dataclass
class GitIngestEvent(IngestEvent):
    ingest_type = IngestType.GIT
    git_instance: str = ''
    git_provider: str = ''
