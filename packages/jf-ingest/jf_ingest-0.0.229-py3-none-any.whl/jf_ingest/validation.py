import json
import logging
import traceback
from collections import defaultdict
from dataclasses import asdict, dataclass, field, fields
from typing import Optional

from jira import JIRA, JIRAError
from requests.exceptions import RequestException

from jf_ingest import logging_helper
from jf_ingest.config import GitConfig, IngestionType, JiraDownloadConfig
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.exceptions import GitProviderUnavailable
from jf_ingest.jf_git.standardized_models import StandardizedRepository
from jf_ingest.jf_jira.auth import (
    JiraAuthenticationException,
    JiraAuthMethod,
    get_jira_connection,
)
from jf_ingest.jf_jira.downloaders import _get_project_filters, download_users
from jf_ingest.utils import (
    PROJECT_HTTP_CODES_TO_RETRY_ON,
    retry_for_status,
    test_jira_or_git_object_access,
)

# NOTE:
# Logger.info will log to stdout AND to our log file.
# We do NOT want to log any passwords or usernames.
# To be extra safe, use print instead of logger.log within validation if you think data could be sensitive.
logger = logging.getLogger(__name__)


@dataclass
class ProjectAccessResult:
    """Jira Specific"""

    issues: bool = False
    versions: bool = False
    components: bool = False


@dataclass
class BoardAccessResult:
    """Jira Specific"""

    sprint_access_ok: bool = False
    sprints: list[str] = field(default_factory=list)


@dataclass
class ObjectAccessResult:
    """General access result for Jira and Git"""

    access_ok: bool = False
    available_objects: list[str] = field(default_factory=list)


@dataclass
class RepositoryAccessResult:
    """Git Specific"""

    repository_name: str
    repository_id: str
    pull_requests: bool = False
    branches: bool = False
    commits_on_default_branch: bool = False


def _bar_factory():
    """
    Annoyingly, dataclasses.field required a callable that takes no args.
    This satisfies that requirement.
    """
    return defaultdict(BoardAccessResult)


def _par_factory():
    """
    Annoyingly, dataclasses.field required a callable that takes no args.
    This satisfies that requirement.
    """
    return defaultdict(ProjectAccessResult)


class SafeDumpDataClass:
    """
    dataclasses.asdict does not work when the values of the dataclasses can be default dicts.
    Let's fix that.

    On version 3.12 we can remove this.
    https://github.com/python/cpython/pull/32056
    https://docs.python.org/3/whatsnew/changelog.html#python-3-12-0-alpha-1
    """

    @classmethod
    def from_dict(cls, body: dict):
        return cls(**body)

    def to_dict(self):
        # convert defaultdict fields to plain old dicts so we can dump the data
        _fields = fields(self)
        for field in _fields:
            value = getattr(self, field.name)
            if isinstance(value, defaultdict):
                setattr(self, field.name, dict(value))
            # recursively handle the sub-healthcheck results on IngestionHealthCheckResult
            elif isinstance(
                value, (GitConnectionHealthCheckResult, JiraConnectionHealthCheckResult)
            ):
                setattr(self, field.name, value.to_dict())
        return asdict(self)


@dataclass
class JiraConnectionHealthCheckResult(SafeDumpDataClass):
    """
    Representing the result of a Jira connection healthcheck report.
    """

    successful: bool

    # The version of Jira that is being run
    server_version: Optional[str] = None

    # Total list of projects accessible
    accessible_projects: list[str] = field(default_factory=list)

    # Projects included in the ingestion configuration to be downloaded but inaccessible from the validator.
    included_inaccessible_projects: list[str] = field(default_factory=list)

    # Access to project-specific data
    project_data: dict = field(default_factory=_par_factory)

    # Fields available on the instance
    fields: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Included fields that we cannot access
    included_inaccessible_fields: list[str] = field(default_factory=list)

    # Resolutions available on the instance
    resolutions: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Issue Types available on the instance
    issue_types: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Issue Link Types available on the instance
    issue_link_types: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Priorities available on the instance
    priorities: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Boards available on the instance
    boards: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Sprints available on the instance by Board
    boards_and_sprints: dict = field(default_factory=_bar_factory)

    # How many users the validator can access
    num_accessible_users: int = 0

    # Permissions granted to the user.
    granted_permissions: list[str] = field(default_factory=list)

    # Whether we have been able to receive an X-ANODE-ID header from the Jira connection.
    # This means the customer is a Jira Data Center customer.
    returns_anode_id_header: bool = False


@dataclass
class GitConnectionHealthCheckResult(SafeDumpDataClass):
    """
    Representing the result of a Git connection healthcheck report, broken down by Git Organization
    """

    instance_slug: str
    organization_login: str

    successful: bool

    git_provider: str

    api_scopes: Optional[str] = None

    # users available on the instance
    users: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # teams available on the instance
    teams: ObjectAccessResult = field(default_factory=ObjectAccessResult)

    # Dict of organization name : repo list of repos we can access
    accessible_repos: list[str] = field(default_factory=list)
    repo_data: dict[str, RepositoryAccessResult] = field(default_factory=dict)

    # list of repos explicitly included in the config but inaccessible with our credentials
    # This is specific only to the Agent
    included_inaccessible_repos: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, body: dict):
        return cls(**body)


@dataclass
class IngestionHealthCheckResult(SafeDumpDataClass):
    """
    Dataclass representing the result of a pre-ingestion permission healthcheck run.
    """

    ingestion_type: IngestionType

    # Whether the healthcheck result was fully successful
    fully_successful: bool = False

    # Customers may have multiple git configs, so we want to account for that with multiple healthcheck results.
    # The key here should be the instance slug.
    git_connection_healthcheck: list[GitConnectionHealthCheckResult] = field(default_factory=list)

    jira_connection_healthcheck: Optional[JiraConnectionHealthCheckResult] = None

    def __post_init__(self):
        """
        Sets the fully_successful field based on the successful fields on the jira and git inputs.
        """
        jira_successful = (
            self.jira_connection_healthcheck.successful
            if self.jira_connection_healthcheck
            else False
        )

        # If we have a non-empty git healthcheck result list, ensure all its members are successful.
        git_successful = bool(self.git_connection_healthcheck) and all(
            [x.successful for x in self.git_connection_healthcheck]
        )

        self.fully_successful = jira_successful and git_successful

    def to_json(self) -> str:
        """
        Converts to a JSON string.

        Returns: The IngestionHealthCheckResult as a JSON representation.

        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, body: str):
        """
        Deserializes a JSON string into an IngestionHealthCheckResult

        Args:
            body:

        Returns: The IngestionHealthCheckResult as a properly nested dataclass

        """
        healthcheck_dict = json.loads(body)

        # We need to do this because Python dataclasses won't natively deserialize a dict representation of a nested
        # dataclass (without third-party packages), so we intercept the list[dict] result
        # and convert it into a list[dataclass].

        new_git_healthcheck_list = []

        for healthcheck_result in healthcheck_dict["git_connection_healthcheck"]:
            parsed_result = GitConnectionHealthCheckResult.from_dict(healthcheck_result)
            new_git_healthcheck_list.append(parsed_result)

        healthcheck_dict["git_connection_healthcheck"] = new_git_healthcheck_list

        healthcheck_dict["jira_connection_healthcheck"] = (
            JiraConnectionHealthCheckResult.from_dict(
                healthcheck_dict["jira_connection_healthcheck"]
            )
            if healthcheck_dict["jira_connection_healthcheck"]
            else None
        )

        return cls(**healthcheck_dict)


def _print_debug_jira_error(e: JIRAError, config: JiraDownloadConfig):
    print("Response:")
    print("  Headers:", e.headers)
    print("  URL:", e.url)
    print("  Status Code:", e.status_code)
    print("  Text:", e.text)

    if "Basic authentication with passwords is deprecated." in str(e):
        logger.error(
            f"Error connecting to Jira instance at {config.url}. Please use a Jira API token, see https://confluence.atlassian.com/cloud/api-tokens-938839638.html"
        )
    else:
        logger.error(
            f"Error connecting to Jira instance at {config.url}, please validate your credentials. Error: {e}"
        )


def _attempt_anode_id_header_check(jira_connection: JIRA) -> bool:
    """

    Args:
        jira_connection: The Jira Connection to query over

    Returns: Whether the X-ANODEID header exists on the response.
    If it does, this means the customer is Jira Data Center.

    """
    try:
        logger.info("==> Getting Jira deployment type...")

        res = jira_connection._session.get(jira_connection._get_url("serverInfo"))
        headers = res.headers

        if "X-ANODEID" in headers:
            logger.info(
                "Response headers contains X-ANODEID! Customer is running Jira Data Center."
            )

            return True
        else:
            logger.info(
                "Response headers does not contain X-ANODEID! Customer is NOT running Jira Data Center."
            )

            return False

    except Exception:
        # This is a pretty hacky check using private members of the jira connection class
        # So we can't rely on it always working. If it breaks we should just return False
        # and move on.
        logger.error("Unable to get X-ANODEID headers from request!")

        return False


def get_jira_version(jira_connection: JIRA) -> Optional[str]:
    """

    Args:
        jira_connection: The Jira connection

    Returns: the string representation of the Jira server version.

    """

    logger.info("==> Getting Jira version...")

    server_info = jira_connection.server_info()

    jira_version: Optional[str] = (
        server_info["version"] if "version" in server_info.keys() else None
    )

    logger.info(f"Found Jira version as {jira_version}")

    return jira_version


def get_jira_permissions(jira_connection: JIRA) -> list[str]:
    """
    Gets the Jira permissions we know about for this user (experimental)
    Args:
        jira_connection: The jira connection to request over.

    Returns: A list of permissions that the user has.

    """

    logger.info("==> Getting Jira permissions...")

    # These are most of the permissions that Jira says are built-in, per this doc:
    # https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-permission-schemes/#built-in-permissions
    # We can pare this down if we decide we don't care about any of these.
    permission_set = {
        'ADD_COMMENTS',
        'ADMINISTER_PROJECTS',
        'ASSIGNABLE_USER',
        'ASSIGN_ISSUES',
        'BROWSE_PROJECTS',  # required to use JF. https://help.jellyfish.co/hc/en-us/articles/13428996347277-Connecting-Jira-to-Jellyfish
        'CLOSE_ISSUES',
        'CREATE_ISSUES',
        'DELETE_ALL_COMMENTS',
        'DELETE_ALL_WORKLOGS',
        'DELETE_ISSUES',
        'DELETE_OWN_COMMENTS',
        'DELETE_OWN_WORKLOGS',
        'EDIT_ALL_COMMENTS',
        'EDIT_ALL_WORKLOGS',
        'EDIT_ISSUES',
        'EDIT_OWN_COMMENTS',
        'EDIT_OWN_WORKLOGS',
        'LINK_ISSUES',
        'MODIFY_REPORTER',
        'MOVE_ISSUES',
        'RESOLVE_ISSUES',
        'SCHEDULE_ISSUES',
        'SET_ISSUE_SECURITY',
        'TRANSITION_ISSUES',
        'USER_PICKER',  # required to use JF. https://help.jellyfish.co/hc/en-us/articles/13428996347277-Connecting-Jira-to-Jellyfish
        'VIEW_READONLY_WORKFLOW',
        'WORK_ON_ISSUES',
    }

    params = {"permissions": ", ".join(list(permission_set))}

    # Jira has some changes here, and we want to be backwards and forwards compatible.
    # Our version of the Jira client does *not* support this parameter right now, so we manually do it.
    # If we update the Jira version we can instead do jira_connection.my_permissions
    # https://developer.atlassian.com/cloud/jira/platform/change-notice-get-my-permissions-requires-permissions-query-parameter/#let-s-see-the-code

    permissions = jira_connection._get_json("mypermissions", params=params)

    granted_permissions = []

    for key, value in permissions["permissions"].items():
        if value["havePermission"]:
            granted_permissions.append(key)

    logger.info(f"Found granted permissions as {granted_permissions}")

    return granted_permissions


def validate_jira(
    config: JiraDownloadConfig,
) -> JiraConnectionHealthCheckResult:
    """
    Validates jira configuration and credentials. Returns a JiraHealthcheckResult object
    representing whether the check was successful and what the errors were, if any.
    Modified from the original Jira validation logic in the Agent.
    """

    healthcheck_result = JiraConnectionHealthCheckResult(successful=True)

    print("\nJira details:")
    print(f"  URL:      {config.url}")
    print(f"  Username: {config.user}")

    if config.user and config.password:
        print("  Password: **********")
    elif config.personal_access_token:
        print("  Token: **********")
    else:
        logger.error("No Jira credentials found in Jira authentication config!")
        healthcheck_result.successful = False

        return healthcheck_result

    # test Jira connection
    try:
        logger.info("==> Testing Jira connection...")
        jira_connection = get_jira_connection(
            config=config, auth_method=JiraAuthMethod.BasicAuth, max_retries=1
        )
        jira_connection.myself()

        healthcheck_result.server_version = get_jira_version(jira_connection)
        healthcheck_result.returns_anode_id_header = _attempt_anode_id_header_check(jira_connection)
        healthcheck_result.granted_permissions = get_jira_permissions(jira_connection)

    except (JIRAError, JiraAuthenticationException) as e:
        print(e)
        # we want to grab the underlying exception on JiraAuthenticationException
        # so we can provide the maximum amount of useful data to someone running in validate mode.
        # if we don't have a JIRAError as the current or underlying exception, call it quits after
        # printing above.
        if type(e) == JiraAuthenticationException and type(e.original_exception) == JIRAError:
            _print_debug_jira_error(e.original_exception, config)
        elif type(e) == JIRAError:
            _print_debug_jira_error(e, config)

        healthcheck_result.successful = False

        return healthcheck_result

    except RequestException as e:
        logger.error(f"RequestException when validating Jira! Message: {e}")

        # Print debugging information related to the request exception
        if e.request:
            print("Request:")
            print("  URL:", e.request.method, e.request.url)
            print("  Body:", e.request.body)
        else:
            print('RequestException contained no "request" value.')

        if e.response:
            print("Response:")
            print("  Headers:", e.response.headers)
            print("  URL:", e.response.url)
            print("  Status Code:", e.response.status_code)
            print("  Text:", e.response.text)
        else:
            print('RequestException contained no "response" value.')

        healthcheck_result.successful = False

        return healthcheck_result

    except Exception as e:
        raise

    # test jira users permission
    try:
        logger.info("==> Testing Jira user browsing permissions...")
        user_count = len(
            download_users(
                jira_basic_connection=jira_connection,
                jira_atlas_connect_connection=None,
                gdpr_active=config.gdpr_active,
            )
        )
        logger.info(f"We can access {user_count} Jira users.")

        healthcheck_result.num_accessible_users = user_count

    except Exception as e:
        logger.error(
            f'Error downloading users from Jira instance at {config.url}, please verify that this user has the "browse all users" permission. Error: {e}'
        )
        healthcheck_result.successful = False

    # test jira project access
    # Calling connection.projects() will return all project keys to us, even if they are private
    # and we don't have access to them. Wait to add projects to the accessible list until we are
    # certain we can get what we need.
    logger.info("==> Testing Jira project permissions...")

    filters: list = _get_project_filters(
        include_projects=config.include_projects,
        exclude_projects=config.exclude_projects,
        include_categories=config.include_project_categories,
        exclude_categories=config.exclude_project_categories,
    )

    all_projects = retry_for_status(
        jira_connection.projects, statuses_to_retry=PROJECT_HTTP_CODES_TO_RETRY_ON
    )
    projects = {p.key for p in all_projects if all(filt(p) for filt in filters)}

    logger.info(
        f"With provided credentials, the following projects are discoverable: {projects}.\nChecking project access."
    )

    accessible_projects, inaccessible_projects = [], []
    for project_key in sorted(projects):
        logger.info(f'Testing access for project: "{project_key}"')
        healthcheck_result.project_data[project_key].issues, _ = test_jira_or_git_object_access(
            jira_connection.search_issues,
            f'project="{project_key}"',
            fields=['id'],
            maxResults=1,
            return_objs=False,
        )
        healthcheck_result.project_data[project_key].versions, _ = test_jira_or_git_object_access(
            jira_connection.project_versions, project_key, return_objs=False
        )
        healthcheck_result.project_data[project_key].components, _ = test_jira_or_git_object_access(
            jira_connection.project_components, project_key, return_objs=False
        )

        all_good = all(healthcheck_result.project_data[project_key].__dict__.values())

        if all_good:
            accessible_projects.append(project_key)
            logger.info(
                f'With provided credentials, we can access issues, versions, and components within project {project_key}'
            )
        else:
            logger.warning(
                f'Could not access all required data in project {project_key}. Access report:\n'
                f'    issues:     {healthcheck_result.project_data[project_key].issues}\n'
                f'    versions:   {healthcheck_result.project_data[project_key].versions}\n'
                f'    components: {healthcheck_result.project_data[project_key].components}\n'
            )

    if config.include_projects:
        for proj in config.include_projects:
            if proj not in accessible_projects:
                inaccessible_projects.append(proj)

    healthcheck_result.accessible_projects = accessible_projects
    healthcheck_result.included_inaccessible_projects = inaccessible_projects

    if inaccessible_projects:
        project_list_str = ", ".join(inaccessible_projects)
        logger.warning(f"\nUnable to access the following projects: {project_list_str}.")
        if config.include_projects and not set(config.include_projects).issubset(
            accessible_projects
        ):
            logger.error(
                "Unable to access the following projects explicitly provided in the config file: "
                ", ".join([p for p in config.include_projects if p not in accessible_projects])
            )
            healthcheck_result.successful = False

    logger.info('Checking access to fields')
    (
        healthcheck_result.fields.access_ok,
        healthcheck_result.fields.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.fields)
    if config.include_fields:
        healthcheck_result.included_inaccessible_fields = [
            f
            for f in config.include_fields  # type: ignore[attr-defined]
            not in [field.name for field in retry_for_status(jira_connection.fields)]
        ]
    if healthcheck_result.included_inaccessible_fields:
        logger.error(
            "Unable to access the following fields that were explicitly included in the config file: "
            ", ".join(healthcheck_result.included_inaccessible_fields)
        )

    logger.info('Checking access to resolutions')
    (
        healthcheck_result.resolutions.access_ok,
        healthcheck_result.resolutions.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.resolutions)

    logger.info('Checking access to issue types')
    (
        healthcheck_result.issue_types.access_ok,
        healthcheck_result.issue_types.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.issue_types)

    logger.info('Checking access to issue link types')
    (
        healthcheck_result.issue_link_types.access_ok,
        healthcheck_result.issue_link_types.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.issue_link_types)

    logger.info('Checking access to priorities')
    (
        healthcheck_result.priorities.access_ok,
        healthcheck_result.priorities.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.priorities)

    logger.info('Checking access to boards')
    (
        healthcheck_result.boards.access_ok,
        healthcheck_result.boards.available_objects,
    ) = test_jira_or_git_object_access(jira_connection.boards)

    if healthcheck_result.boards.access_ok:
        boards = retry_for_status(jira_connection.boards)
        logger.info('Checking access to sprints')
        for board in boards:
            (
                healthcheck_result.boards_and_sprints[board.name].sprint_access_ok,
                healthcheck_result.boards_and_sprints[board.name].sprints,
            ) = test_jira_or_git_object_access(jira_connection.sprints, board.id, is_sprint=True)

    # TODO include repo data here?
    # We currently dont flag repos as inaccessible in the UI, so shouldn't fail the overall
    # check yet if we're not able to have the user dig into the repo data.
    # Probably the best thing to do here is a similar approach to Jira projects, where we
    # only fail if we've explicitly included a repo in the config and can't access it.
    healthcheck_result.successful &= all(
        [
            healthcheck_result.fields.access_ok,
            healthcheck_result.resolutions.access_ok,
            healthcheck_result.issue_types.access_ok,
            healthcheck_result.issue_link_types.access_ok,
            healthcheck_result.priorities.access_ok,
            healthcheck_result.boards.access_ok,
            healthcheck_result.num_accessible_users,
            len(healthcheck_result.accessible_projects),
            not len(healthcheck_result.included_inaccessible_projects),
        ]
        + [bar.sprint_access_ok for bar in healthcheck_result.boards_and_sprints.values()]
    )

    return healthcheck_result


def validate_git(git_configs: list[GitConfig]) -> list[GitConnectionHealthCheckResult]:
    """Attempts to hit all relevant GIT APIs and return a health check verifying our access

    Args:
        git_configs (list[GitConfig]): A list of git configs to crawl over
        get_all_available_objects (bool, optional): A boolean flag that when set to True will query for all available objects. Defaults to False.

    Returns:
        list[GitConnectionHealthCheckResult]: A health check object detailing what we do and do not have access to
    """

    healthcheck_result_list: list[GitConnectionHealthCheckResult] = []

    for i, git_config in enumerate(git_configs, start=1):
        logger.info(f"Git Configuration details for instance {i}/{len(git_configs)}:")
        logger.info(f"  Instance slug: {git_config.instance_slug}")
        logger.info(f"  Provider: {git_config.git_provider.value}")
        logger.info(f"  Organizations: {len(git_config.git_organizations)}")
        if len(git_config.excluded_organizations) > 0:
            logger.info(f"  Excluded organizations: {git_config.excluded_organizations}")
        if len(git_config.included_repos) > 0:
            logger.info(f"  Included repos: {git_config.included_repos}")
        if len(git_config.excluded_repos) > 0:
            logger.info(f"  Excluded repos: {git_config.excluded_repos}")
        if len(git_config.included_branches_by_repo) > 0:
            logger.info(f"  Included Branches: {git_config.included_branches_by_repo}")

        logger.info('==> Testing Git connection...')

        try:
            git_adapter = GitAdapter.get_git_adapter(git_config)
        except Exception as e:
            logger.error(
                f'Error connecting to Git instance {git_config.instance_slug}. Exception: {e}\n'
            )
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)

            healthcheck_result = GitConnectionHealthCheckResult(
                successful=False,
                instance_slug=git_config.instance_slug,
                organization_login='',
                git_provider=git_config.git_provider.value,
            )
            healthcheck_result_list.append(healthcheck_result)
            continue

        for org in sorted(git_adapter.get_organizations(), key=lambda org: org.login):
            successful = True
            repos: list[StandardizedRepository] = []
            api_scopes = git_adapter.get_api_scopes()
            healthcheck_result = GitConnectionHealthCheckResult(
                successful=successful,
                instance_slug=git_config.instance_slug,
                organization_login=org.login,
                api_scopes=api_scopes,
                git_provider=git_config.git_provider.value,
            )
            if git_adapter.client.uses_jwt:  # type: ignore[attr-defined]
                logger.info('Using JWT token for authentication. No API Scopes available.')
            else:
                logger.info(f'\nFor Organization {org.name} we have the following API Scopes:')
                logger.info(f'  {api_scopes}\n')

            try:
                (
                    healthcheck_result.users.access_ok,
                    healthcheck_result.users.available_objects,
                ) = test_jira_or_git_object_access(git_adapter.get_users, org, return_attr='login')

                (
                    healthcheck_result.teams.access_ok,
                    healthcheck_result.teams.available_objects,
                ) = test_jira_or_git_object_access(git_adapter.get_teams, org)

                repos = list(git_adapter.get_repos(org))
                for repo in sorted(repos, key=lambda repo: repo.name):
                    # NOTE: I'm paranoid about if repo names are unique, so I'm combining them with their ID
                    # so we have readability and uniqueness
                    repo_access_result = RepositoryAccessResult(
                        repository_name=repo.name, repository_id=repo.id
                    )
                    repo_access_result.pull_requests = test_jira_or_git_object_access(
                        git_adapter.get_prs,
                        repo,
                        limit=1,
                        return_attr='id',
                    )[0]
                    repo_access_result.branches = bool(repo.branches)
                    repo_access_result.commits_on_default_branch = test_jira_or_git_object_access(
                        git_adapter.get_commits_for_default_branch,
                        repo,
                        limit=1,
                        return_attr='hash',
                    )[0]

                    repo_name_with_id = f'{repo.name}_({repo.id})'
                    healthcheck_result.repo_data[repo_name_with_id] = repo_access_result

                    # Report to the console what we found:
                    if (
                        repo_access_result.pull_requests
                        and repo_access_result.branches
                        and repo_access_result.commits_on_default_branch
                    ):
                        logger.info(
                            f'With provided credentials we can access PRs, Branches, and Commits for Repository {repo_access_result.repository_name} (Git Organization: {org.login})'
                        )
                    else:
                        logger.info(
                            f'Could not access all required data in Repo {repo_access_result.repository_name} (Git Organization: {org.login})'
                        )
                        logger.info(f'    PRs:      {repo_access_result.pull_requests}')
                        logger.info(f'    Commits:  {repo_access_result.commits_on_default_branch}')
                        logger.info(f'    Branches: {repo_access_result.branches}')

            except GitProviderUnavailable as e:
                logger.warning(
                    f'The Git provider is currently not supported in JF Ingest! Provider: {git_config.git_provider}. This config ({git_config.instance_slug}) will be skipped'
                )
                successful = False
            except Exception as e:
                logger.error(f"Git connection unsuccessful! Exception: {e}")
                logger.debug(traceback.format_exc())
                successful = False
            finally:
                healthcheck_result.successful = successful
                healthcheck_result.accessible_repos = [repo.name for repo in repos]
                healthcheck_result.included_inaccessible_repos = [
                    repo_name
                    for repo_name in git_config.included_repos
                    if repo_name not in healthcheck_result.accessible_repos
                ]

        healthcheck_result_list.append(healthcheck_result)

    return healthcheck_result_list
