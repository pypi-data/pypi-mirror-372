import enum
import json
import logging
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, NamedTuple, Optional, Set, TextIO, Union

import pytz
import requests
from dateutil import parser

from jf_ingest.constants import Constants
from jf_ingest.jf_git.exceptions import GitProviderUnavailable
from jf_ingest.jf_git.standardized_models import StandardizedRepository
from jf_ingest.logging_helper import send_to_agent_log_file
from jf_ingest.utils import format_datetime_to_ingest_timestamp

logger = logging.getLogger(__name__)

JELLYFISH_API_BASE = "https://app.jellyfish.co"


class JiraAuthMethod(enum.IntEnum):
    BasicAuth = 1
    AtlassianConnect = 2


class GitProvider(enum.Enum):
    # these come from an entry in the config file, so we want it to be something readable
    GITHUB = "GITHUB"
    ADO = "ADO"
    GITLAB = "GITLAB"


class GitProviderInJellyfishRepo(enum.Enum):
    # duplication of the class GitProvider values in the jellyfish repo so we can maintain consistency
    GITHUB = 'GH'
    # The agent has no notion of a GithubEnterprise (vs regular Github), so GHE doesn't need to be in the above GitProvider class
    GITHUB_ENTERPRISE = 'GHE'
    ADO = "ADO"
    GITLAB = "GL"
    GITHUB_ENTERPRISE_CLOUD = 'GHEC'


# Needs to subclass str to be serializable
class IngestionType(str, enum.Enum):
    AGENT = "AGENT"
    DIRECT_CONNECT = "DIRECT_CONNECT"


@dataclass
class IssueMetadata:
    id: str
    key: str
    updated: Optional[datetime]
    project_id: Optional[str] = (
        None  # NOTE: This field is optionally set, and generally only used for detected re-keys
    )
    # The following fields are used for detecting redownloads
    epic_link_field_issue_key: Optional[str] = None
    parent_field_issue_key: Optional[str] = None
    parent_id: Optional[str] = None

    def __post_init__(self):
        """Post Init is called here to properly type everything by doing typecasts"""
        self.id = str(self.id)
        self.key = str(self.key)
        self.updated = (
            self.updated if isinstance(self.updated, datetime) else parser.parse(self.updated)
        )

        # Sanity recasts to make sure everything is a string
        if self.project_id:
            self.project_id = str(self.project_id)
        if self.epic_link_field_issue_key:
            self.epic_link_field_issue_key = str(self.epic_link_field_issue_key)
        if self.parent_field_issue_key:
            self.parent_field_issue_key = str(self.parent_field_issue_key)
        if self.parent_id:
            self.parent_id = str(self.parent_id)

    @staticmethod
    def deserialize_json_str_to_issue_metadata(
        json_str: str,
    ) -> Union["IssueMetadata", list["IssueMetadata"]]:
        """Helper function to deserialize a JSON type object to an IssueMetadata object, or a list of IssueMetadata Objects

        Raises:
            Exception: Raises an expection if the provided json str is not a valid JSON str

        Returns:
            _type_: Either a list of IssueMetadata Objects, or an IssueMetadata Object
        """
        json_data: Union[list, dict] = json.loads(json_str)
        if type(json_data) == list:
            list_of_issue_metadata = []
            for item in json_data:
                item['updated'] = datetime.fromisoformat(item['updated'])
                list_of_issue_metadata.append(IssueMetadata(**item))
            return list_of_issue_metadata
        elif type(json_data) == dict:
            json_data['updated'] = datetime.fromisoformat(json_data['updated'])
            return IssueMetadata(**json_data)
        else:
            raise Exception(
                f'Unrecognized type for deserialize_json_str_to_issue_metadata, type={type(json_data)}'
            )

    @staticmethod
    def from_json(
        json_source: Union[str, bytes, TextIO]
    ) -> Union["IssueMetadata", list["IssueMetadata"]]:
        """Generalized wrapper for the deserialize_json_str_to_issue_metadata function, which deserializes JSON Strings to Python objects

        Returns:
            _type_: Either a list of IssueMetadata objects or an IssueMetaData object, depending on what was supplied
        """
        if isinstance(json_source, str):
            return IssueMetadata.deserialize_json_str_to_issue_metadata(json_source)
        elif isinstance(json_source, bytes):
            return IssueMetadata.deserialize_json_str_to_issue_metadata(json_source.decode("utf-8"))
        elif isinstance(json_source, TextIO):
            json_str = json_source.read()
            return IssueMetadata.deserialize_json_str_to_issue_metadata(json_str)

    @staticmethod
    def to_json_str(issue_metadata: Union["IssueMetadata", list["IssueMetadata"]]) -> str:
        """This is a STATIC helper function that can serialize both a LIST of issue_metadata and a singluar
        IssueMetadata to a JSON string!

        Args:
            issue_metadata (Union[&quot;IssueMetadata&quot;, list[&quot;IssueMetadata&quot;]]): Either a list of IssueMetadata, or a singluar IssueMetadata object

        Returns:
            str: A serialized JSON str
        """

        def _serializer(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, IssueMetadata):
                return value.__dict__
            else:
                return str(value)

        return json.dumps(issue_metadata, default=_serializer)

    @staticmethod
    def init_from_jira_issue(
        issue: dict, project_id: Optional[str] = None, skip_parent_data: bool = False
    ):
        fields: dict = issue.get("fields", {})
        return IssueMetadata(
            id=issue["id"],
            key=issue["key"],
            project_id=project_id,
            updated=parser.parse(fields.get("updated")) if fields.get("updated") else None,
            parent_id=fields.get("parent", {}).get("id") if not skip_parent_data else None,
            parent_field_issue_key=(
                fields.get("parent", {}).get("key") if not skip_parent_data else None
            ),
        )

    @staticmethod
    def init_from_jira_issues(issues=list[dict], skip_parent_data: bool = False):
        return [
            IssueMetadata.init_from_jira_issue(issue, skip_parent_data=skip_parent_data)
            for issue in issues
        ]

    # Define a hashing function so that we can find uniqueness
    # easily using sets
    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __o) -> bool:
        return hash(self) == hash(__o)


@dataclass
class UserMetadata:
    """Helper class for tracking users that exist within issues.
    All optional fields here are for debugging purposes. The only
    required fields are self_url and user_key, which is used to
    download and/or identify users
    """

    self_url: str
    user_key: str
    email: Optional[str]
    name: Optional[str]
    active: Optional[bool]

    def __hash__(self):
        return hash(self.self_url)


@dataclass
class GitAuthConfig:
    # These fields are shared between all Git type authentication
    # schemes (I think)
    company_slug: str
    base_url: Optional[str] = None
    # Note: token is rarely provided, as we often do some type of
    # git JWT authentication to get a time sensitive login token.
    # See how we authenticate specifically for Github as an example:
    # GithubClient._get_app_access()
    token: Optional[str] = None
    verify: bool = True
    session: requests.Session = None


@dataclass
class AzureDevopsAuthConfig(GitAuthConfig):
    api_version: str = '7.0'


@dataclass
class GitLabAuthConfig(GitAuthConfig):
    """This is specifically for Gitlab Cloud and Gitlab Enterprise!"""

    keep_base_url: bool = False


@dataclass
class GithubAuthConfig(GitAuthConfig):
    """This is specifically for Github Cloud and Github Enterprise!"""

    installation_id: Optional[str] = None
    app_id: Optional[str] = None
    private_key: Optional[str] = None

    def __post_init__(self):
        if self.installation_id and self.app_id and self.private_key:
            pass
        elif self.token:
            pass
        else:
            logger.warning(
                f'Github Auth Config requires either a provided Token or an installation_id, app_id, and private_key'
            )


@dataclass
class GitConfig:
    """This is the generalized Ingest Configuration for all Git Providers (Github, Gitlab, etc)

    Raises:
        GitProviderUnavailable: This error gets thrown in the git_provider is not currently supported

    Returns:
        GitConfig: A git config data object
    """

    company_slug: str
    instance_slug: str
    instance_file_key: str
    git_provider: GitProvider
    git_auth_config: GitAuthConfig

    # If not provided we will use the default Github API
    url: Optional[str] = None

    # Jellyfish Feature Flags
    jf_options: dict[str, Any] = field(default_factory=dict)

    # Maps when we should pull commits from for each repository (by ['org_login']['repo_id'] name)
    repos_to_skip_pull_prs_for: dict[str, datetime] = field(default_factory=dict)
    repos_to_prs_last_updated: dict[str, datetime] = field(default_factory=dict)
    # Maps the oldest PR/commit date we have in our system
    repos_to_commits_backpopulated_to: dict[str, datetime] = field(default_factory=dict)
    repos_to_prs_backpopulated_to: dict[str, datetime] = field(default_factory=dict)

    # Git Organization info
    git_organizations: List[str] = field(default_factory=list)
    pull_from: datetime = datetime.min.replace(tzinfo=pytz.UTC)

    # Pull Teams
    pull_teams: bool = False

    # Copilot info
    copilot_enabled: bool = False

    # D.C. only logic
    skip_pulling_users: bool = False
    skip_pulling_repos: bool = False
    discover_organizations: bool = (
        False  # Do not discover orgs by default. This is controlled via the JFGithubInstance object
    )
    repos_in_jellyfish: List[StandardizedRepository] = field(default_factory=list)
    # Mark whether we should pull all commits AND branches for each repo.
    # In agent, this should be True. In Jellyfish, it is controlled by the JiraInstance
    pull_all_commits_and_branches: bool = False
    # In jellyfish this is controlled at the instance level and at the repo level
    repo_id_to_pull_all_commits_and_branches: dict[str, bool] = field(default_factory=dict)
    force_full_backpopulation_pull: bool = False
    backpopulation_window_days: int = 60
    # A list of Repo IDs that are marked as quiescent in the Jellyfish DB
    quiescent_repos: set[str] = field(default_factory=set)
    # Flags for if we should pull PR Metadata
    pull_files_for_prs: bool = False
    hash_files_for_prs: bool = False

    # Agent specific configuration
    excluded_organizations: List[str] = field(default_factory=list)
    included_repos: List[str] = field(default_factory=list)
    excluded_repos: List[str] = field(default_factory=list)
    included_branches_by_repo: Dict[str, List[str]] = field(default_factory=dict)
    git_redact_names_and_urls: bool = False
    git_strip_text_content: bool = False
    check_ghc_mannequin_user_prs: bool = False

    def __post_init__(self):
        if type(self.git_provider) == str:
            if self.git_provider.upper() in [
                GitProvider.GITHUB.value,
                GitProviderInJellyfishRepo.GITHUB.value,
                GitProviderInJellyfishRepo.GITHUB_ENTERPRISE.value,
            ]:
                self.git_provider = GitProviderInJellyfishRepo.GITHUB
            elif self.git_provider.upper() in [
                GitProvider.ADO.value,
                GitProviderInJellyfishRepo.ADO.value,
            ]:
                self.git_provider = GitProviderInJellyfishRepo.ADO
            elif self.git_provider.upper() in [
                GitProvider.GITLAB.value,
                GitProviderInJellyfishRepo.GITLAB.value,
            ]:
                self.git_provider = GitProviderInJellyfishRepo.GITLAB
            else:
                raise GitProviderUnavailable(
                    f'Provided git provider is not available: {self.git_provider}'
                )

    def get_pull_from_for_commits(
        self,
    ) -> datetime:
        """This is a helper function for getting the 'pull_from' date for Commits for any given repository.

        The normal, daily case -- we pull commits based on a commit date greater than some date in the past.  A commit
        with a commit date of 1 week ago could be present in a branch today even though it wasn't yesterday (if, say, it
        was just merged into the branch today) -- so we don't want earliest_commit_date_to_pull_if_not_backpop to be too
        small.  30 days ago is probably reasonable.

        Returns:
            datetime: A pull from date to pull commits from (in UTC). Typically about 60 days in the past
        """
        return datetime.now(tz=timezone.utc) - timedelta(days=31)

    def get_pull_from_for_prs(
        self,
        repo_id: str,
    ) -> datetime:
        """This is a helper function for getting the specified 'pull_from' date for PRs, for a given repo.
        This value is generally the date of the latest commit we have in our Jellyfish database. If a datetime
        is not set for this repo ID, we will default to the value set at pull_from

        Args:
            org_login (str): The org login for the parent Git Organization
            repo_id (str): The ID for the repository we are concerned with

        Returns:
            datetime: A pull from date to pull PRs from (in UTC)
        """
        return self.repos_to_prs_last_updated.get(repo_id, self.pull_from)

    def get_backpopulated_date_for_commits(
        self,
        repo_id: str,
    ) -> Optional[datetime]:
        """This is a helper function to get the oldest commit date that we have in our system. It is needed
        to determine if we need to run a backpopulation algorithm

        Args:
            org_login (str): The org login for the parent Git Organization
            repo_id (str): The ID for the repository we are concerned with

        Returns:
            datetime: A pull from date to pull commits from (in UTC)
        """
        return self.repos_to_commits_backpopulated_to.get(repo_id, None)

    def get_backpopulated_date_for_prs(
        self,
        repo_id: str,
    ) -> Optional[datetime]:
        """This is a helper function to get the oldest PR date that we have in our system. It is needed
        to determine if we need to run a backpopulation algorithm

        Args:
            org_login (str): The org login for the parent Git Organization
            repo_id (str): The ID for the repository we are concerned with

        Returns:
            datetime: A pull from date to pull PRs from (in UTC)
        """
        return self.repos_to_prs_backpopulated_to.get(repo_id, None)


@dataclass
class JiraAuthConfig:
    # Provides an authenticated connection to Jira, without the additional
    # settings needed for download/ingest.
    company_slug: str
    url: str
    gdpr_active: bool
    # NOTE: Used in the User-Agent header. Not related
    # to the Jellyfish Agent
    user_agent: str = Constants.JELLYFISH_USER_AGENT
    # Used for Basic Auth
    user: Optional[str] = None
    password: Optional[str] = None
    personal_access_token: Optional[str] = None
    # Used for Atlassian Direct Connect
    jwt_attributes: dict[str, str] = field(default_factory=dict)
    bypass_ssl_verification: bool = False
    required_email_domains: List[str] = field(default_factory=list)
    is_email_required: bool = False
    available_auth_methods: List[JiraAuthMethod] = field(default_factory=list)
    connect_app_active: bool = False


@dataclass
class JiraDownloadConfig(JiraAuthConfig):
    # Indicates whether the email augmentation should be performed. This is needed
    # when testing connect-driven data refreshes locally since the connect app used
    # for testing does not (and can not) have the required "Email" permission. As
    # such, this allows us to skip that step when necessary.
    should_augment_emails: bool = True

    include_fields: List = field(default_factory=list)
    exclude_fields: List = field(default_factory=list)
    # User information
    force_search_users_by_letter: bool = False
    search_users_by_letter_email_domain: Optional[str] = None
    skip_downloading_users: bool = False  # Skips downloading users in bulk
    user_keys_in_jellyfish: list[str] = field(
        default_factory=list
    )  # A complete list of all known users (in our DB) by their unique ID

    # Projects information
    include_projects: List = field(default_factory=list)
    exclude_projects: List = field(default_factory=list)
    include_project_categories: List = field(default_factory=list)
    exclude_project_categories: List = field(default_factory=list)

    # Boards/Sprints
    download_boards: bool = True
    download_sprints: bool = True
    filter_boards_by_projects: bool = (
        False  # When provided, we will only download boards that are associated with the projects we are downloading
    )

    # Issues
    skip_issues: bool = False
    only_issues: bool = False
    full_redownload: bool = False
    project_id_to_pull_from: Optional[Dict[str, datetime]] = None
    pull_from: datetime = datetime.min
    issue_batch_size: int = Constants.MAX_ISSUE_API_BATCH_SIZE
    issue_download_concurrent_threads: int = 1
    recursively_download_parents: bool = (
        False  # When provided, we will download parents of parents, and then those parents, until we find all parents
    )
    issue_jql_filter: Optional[str] = None
    pull_issues_by_date: bool = (
        True  # If True, we will pull issues by date, otherwise we will pull all issues. Customers using webhooks will have this value set to False
    )

    # Dict of Issue ID (str) to IssueMetadata Object
    jellyfish_issue_metadata: List[IssueMetadata] = field(default_factory=list)
    jellyfish_issue_ids_for_redownload: Set[str] = field(default_factory=set)
    jellyfish_project_ids_to_keys: Dict = field(default_factory=dict)

    # worklogs
    download_worklogs: bool = False
    # Potentially solidify this with the issues date, or pull from
    work_logs_pull_from: datetime = datetime.min

    # Jira Ingest Feature Flags
    feature_flags: dict = field(default_factory=dict)

    # Agent
    uses_agent: bool = False

    def normalize_datetimes_to_timezone_locale(self, timezone_locale: str):
        """Normalizes all datetime fields in the config to the specified timezone locale."""
        send_to_agent_log_file(
            f'Normalizing datetimes to timezone locale: {timezone_locale}', level=logging.INFO
        )
        try:
            tz = pytz.timezone(timezone_locale)
        except pytz.UnknownTimeZoneError:
            logger.warning(
                f'Unknown timezone locale: {timezone_locale}. Datetimes will not be normalized'
            )
            return

        def normalize_datetime(dt):
            if type(dt) is datetime:
                return dt.astimezone(tz)
            else:
                # Sometimes objects are passed in as Dates and not Datetimes,
                # so we can't adjust the timezone on them
                return dt

        self.pull_from = normalize_datetime(self.pull_from)
        self.work_logs_pull_from = normalize_datetime(self.work_logs_pull_from)

        # Normalize the project_id_to_pull_from datetimes
        if self.project_id_to_pull_from:
            for project_id, pull_date in self.project_id_to_pull_from.items():
                self.project_id_to_pull_from[project_id] = normalize_datetime(pull_date)

        # Normalize issue metadata datetimes
        for issue in self.jellyfish_issue_metadata:
            if issue.updated:
                issue.updated = normalize_datetime(issue.updated)

        send_to_agent_log_file(
            f'Successfully normalized datetimes to timezone locale: {timezone_locale}',
            level=logging.INFO,
        )


@dataclass
class IngestionConfig:
    # upload info
    company_slug: str
    jellyfish_api_token: str
    save_locally: bool = True
    upload_to_s3: bool = False
    local_file_path: Optional[str] = None
    timestamp: Optional[str] = None

    # Jira Auth Info and Download Configuration
    jira_config: Optional[JiraDownloadConfig] = None

    # Git Config data
    # NOTE: Unlike Jira, we can have multiple Git Configurations.
    # Each Git Configuration maps to a Git Instance
    git_configs: List[GitConfig] = field(default_factory=list)

    # JF specific config
    jellyfish_api_base: str = JELLYFISH_API_BASE
    ingest_type: Optional[IngestionType] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = format_datetime_to_ingest_timestamp(datetime.utcnow())

        if not self.local_file_path:
            self.local_file_path = f"{tempfile.TemporaryDirectory().name}/{self.timestamp}"


class IssueDownloadingResult(NamedTuple):
    downloaded_ids: set[str]
    issue_ids_too_large_to_upload: set[str]
    discovered_parent_ids: set[str]
    total_batches: int
    users_found: set[UserMetadata]


class IssueListDiff(NamedTuple):
    ids_to_delete: set[str]
    ids_to_download: set[str]
