import logging
import traceback
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Generator, List, NamedTuple, Optional, Union

from dateutil import parser
from requests.exceptions import HTTPError
from tqdm import tqdm

from jf_ingest import diagnostics, logging_helper
from jf_ingest.config import GitConfig
from jf_ingest.graphql_utils import gql_format_to_datetime
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.clients.github import GithubClient
from jf_ingest.jf_git.standardized_models import (
    PullRequestReviewState,
    StandardizedBranch,
    StandardizedCommit,
    StandardizedFileData,
    StandardizedJFAPIPullRequest,
    StandardizedLabel,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestAuthor,
    StandardizedPullRequestComment,
    StandardizedPullRequestMetadata,
    StandardizedPullRequestReview,
    StandardizedRepository,
    StandardizedShortRepository,
    StandardizedTeam,
    StandardizedUser,
)

logger = logging.getLogger(__name__)

'''

    Data Fetching

'''


class GithubRepoMetaData(NamedTuple):
    """This is a data class unique to Github. It helps us cache information about repos
    so we can intelligently determine if we need to pull commits, branches, and PRs.
    """

    # Repo ID, as set by github
    repo_id: str
    # Branches count
    branches_count: int
    # Commits information
    #  Commits are pulled in Deltas, so we'll have a datetime that we're pulling from.
    #  When initially querying repo data, get the latest commit date. That way, in
    #  memory, we can determine if we need to pull commits or not. For customers with
    #  large repo counts, this can save us A LOT of time!
    latest_commit_date_on_default_branch: Optional[
        datetime
    ]  # If this value is none, that indicates there are NO commits to pull
    # PR Information
    #  PRs follow the same pattern as commits above
    latest_pr_updated_at: Optional[
        datetime
    ]  # If this value is none, that indicates there are NO PRs to pull


class GithubAdapter(GitAdapter):
    def __init__(self, config: GitConfig):
        # Git Config options
        self.client = GithubClient(config.git_auth_config)
        self.config = config
        self.repo_id_to_name_lookup: Dict = {}
        self.repo_id_to_repo_meta_data: Dict[str, GithubRepoMetaData] = {}

    def get_api_scopes(self):
        return self.client.get_scopes_of_api_token()

    def get_organizations(self) -> List[StandardizedOrganization]:
        # NOTE: For github, organization equates to a Github organization here!
        # We have the name of the organization in the config, expected to be a list of length one
        try:
            raw_orgs = []
            if self.config.discover_organizations:
                for raw_org in self.client.get_all_organizations():
                    raw_orgs.append(raw_org)
            else:
                for org_login in self.config.git_organizations:
                    raw_orgs.append(self.client.get_organization_by_login(org_login))
        except HTTPError as e:
            if e.response.status_code == 404:
                # give something a little nicer for 404s
                raise ValueError(
                    'Organization not found. Make sure your token has appropriate access to Github.'
                )
            raise
        return [_standardize_organization(raw_org) for raw_org in raw_orgs]

    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        for i, user in enumerate(self.client.get_users(standardized_organization.login), start=1):
            if user:
                yield _standardize_user(user)
            if limit and i >= limit:
                return

    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedTeam, None, None]:
        for i, team in enumerate(
            self.client.get_teams(login=standardized_organization.login), start=1
        ):
            yield _standardize_team(team)
            if limit and i >= limit:
                return

    def get_repos(
        self,
        standardized_organization: StandardizedOrganization,
        limit: Optional[int] = None,
        only_private: bool = False,
    ) -> Generator[StandardizedRepository, None, None]:

        for idx, api_repo in enumerate(
            self.client.get_repos(standardized_organization.login, only_private), start=1
        ):
            repo_id = str(api_repo['id'])
            self.repo_id_to_name_lookup[repo_id] = api_repo['name']

            # Extract info for metadata caching
            # Get Branch Count
            total_branches = int(api_repo['branches']['totalCount'])

            # Get latest commit date
            # NOTE: Default branch can be None!
            latest_commit_date_on_default_branch: Optional[datetime] = None
            if default_branch := api_repo.get('defaultBranch'):
                if commits := default_branch['commitsQuery']['commitHistory']['commits']:
                    latest_commit_date_on_default_branch = gql_format_to_datetime(
                        commits[0]['committedDate']
                    )

            # Get PR Last updated at
            pr_updated_at: Optional[datetime] = None
            pr_query = api_repo['prQuery']
            if prs := pr_query['prs']:
                pr_updated_at = gql_format_to_datetime(prs[0]['updatedAt'])

            self.repo_id_to_repo_meta_data[repo_id] = GithubRepoMetaData(
                repo_id=repo_id,
                branches_count=total_branches,
                latest_commit_date_on_default_branch=latest_commit_date_on_default_branch,
                latest_pr_updated_at=pr_updated_at,
            )

            yield _standardize_repo(api_repo, standardized_organization)

            if limit and idx >= limit:
                return

    def get_repos_count(
        self, standardized_organization: StandardizedOrganization, only_private: bool = False
    ) -> int:
        return self.client.get_repos_count(standardized_organization.login, only_private)

    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_branches: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedBranch, None, None]:
        # It is possible to have 0 branches on a repo. If that is the case
        # and we've already detected that via our repo metadata query, then
        # we don't need to hit the API for any branch data
        if self.repo_id_to_repo_meta_data[standardized_repo.id].branches_count == 0:
            return
        if pull_branches:
            repo_name = self.repo_id_to_name_lookup[standardized_repo.id]
            for idx, branch in enumerate(
                self.client.get_branches(
                    login=standardized_repo.organization.login, repo_name=repo_name
                ),
                start=1,
            ):
                if standardized_branch := _standardize_branch(
                    branch,
                    repo_id=standardized_repo.id,
                    is_default_branch=standardized_repo.default_branch_sha
                    == branch['target']['sha'],
                ):
                    yield standardized_branch

                if limit and idx >= limit:
                    return
        else:
            # Above, if we're pulling all branches, it's safe to assume that the default branch
            # will be included in that
            # When we don't pull all branches, always return default branch
            if standardized_repo.default_branch_name:
                yield StandardizedBranch(
                    repo_id=standardized_repo.id,
                    name=standardized_repo.default_branch_name,
                    sha=standardized_repo.default_branch_sha,
                    is_default=True,
                )

    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        if not pull_since:
            logging_helper.send_to_agent_log_file(
                f'When pulling commits for Branches, the "pull_since" argument is required for Github',
                level=logging.ERROR,
            )
            return

        repo_meta_data = self.repo_id_to_repo_meta_data[standardized_repo.id]
        pulled_commit_count = 0

        for branch_name in self.get_filtered_branches(standardized_repo, branches):
            try:
                login = standardized_repo.organization.login
                repo_name = self.repo_id_to_name_lookup[standardized_repo.id]

                # Check out repo meta data cache to see
                if standardized_repo.default_branch_name == branch_name and repo_meta_data:
                    # If we've cached that this commit is older or equal to our pull_since value,
                    # do not bother hitting the API for more commit data OR if there are no commits
                    # If repo_meta_data.latest_commit_date_on_default_branch is None, that indicates no commits
                    if not repo_meta_data.latest_commit_date_on_default_branch:
                        logging_helper.send_to_agent_log_file(
                            f'Not pulling commits for branch {branch_name} because this branch has no commits, '
                            'according to the repo meta data.'
                        )
                        continue
                    if repo_meta_data.latest_commit_date_on_default_branch <= pull_since:
                        logging_helper.send_to_agent_log_file(
                            f'Not pulling commits for branch {branch_name} because there are no commits newer than the pull_since data. '
                            f'pull_since: {pull_since}, latest_commit_for_branch: {repo_meta_data.latest_commit_date_on_default_branch}'
                        )
                        continue

                for api_commit in self.client.get_commits(
                    login=login,
                    repo_name=repo_name,
                    branch_name=branch_name,
                    since=pull_since,
                    until=pull_until,
                ):
                    yield _standardize_commit(
                        api_commit,
                        standardized_repo,
                        branch_name,
                    )

                    pulled_commit_count += 1
                    if limit and pulled_commit_count >= limit:
                        return

            except Exception as e:
                logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
                logger.warning(f':WARN: Got exception for branch {branch_name}: {e}. Skipping...')

    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        if not pull_since:
            logging_helper.send_to_agent_log_file(
                f'When pulling commits for Branches, the "pull_since" argument is required for Github',
                level=logging.ERROR,
            )
            return

        try:
            login = standardized_repo.organization.login
            repo_name = self.repo_id_to_name_lookup[standardized_repo.id]
            if standardized_repo.default_branch_name:
                for j, api_commit in enumerate(
                    self.client.get_commits(
                        login=login,
                        repo_name=repo_name,
                        branch_name=standardized_repo.default_branch_name,
                        since=pull_since,
                        until=pull_until,
                    ),
                    start=1,
                ):
                    yield _standardize_commit(
                        api_commit,
                        standardized_repo,
                        standardized_repo.default_branch_name,
                    )
                    if limit and j >= limit:
                        return

        except Exception as e:
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)
            logger.warning(
                f':WARN: Got exception for branch {standardized_repo.default_branch_name}: {e}. Skipping...'
            )

    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pr_pull_from_date: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_id = standardized_repo.id
            repo_name = self.repo_id_to_name_lookup[repo_id]

            # IF we have repo metadata for this repo and
            # IF the repo meta data indicates the latest PR for this repo
            # is older than the pr_pull_from_date, than that means we don't
            # need to pull any newly updated PRs
            repo_metadata = self.repo_id_to_repo_meta_data[repo_id]
            if repo_metadata.latest_pr_updated_at:
                if pr_pull_from_date and pr_pull_from_date >= repo_metadata.latest_pr_updated_at:
                    logging_helper.send_to_agent_log_file(
                        f'Using Repo meta data for {repo_name} (ID: {repo_id}) we were able to determine that we do not need to pull any PR data! '
                        f'pr_pull_from_data: {pr_pull_from_date}, repo_metadata.latest_pr_updated_at: {repo_metadata.latest_pr_updated_at}'
                    )
                    return
            else:
                logging_helper.send_to_agent_log_file(
                    f'Using Repo meta data for {repo_name} (ID: {repo_id}) we were able to determine that this repo has no PRs in it. No need to hit the API'
                )
                return
            for i, api_pr_metadata in enumerate(
                self.client.get_prs_metadata(login=login, repo_name=repo_name), start=1
            ):
                yield StandardizedPullRequestMetadata(
                    id=api_pr_metadata['pr']['number'],
                    updated_at=gql_format_to_datetime(api_pr_metadata['pr']['updatedAt']),
                    api_index=api_pr_metadata['cursor'],
                )
                if limit and i >= limit:
                    return

        except Exception:
            # if something happens when pulling PRs for a repo, just keep going.
            logger.warning(
                f'Problem fetching PR metadata from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
            )
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)

    def get_pr_authors(
        self, pr_list: list[StandardizedJFAPIPullRequest]
    ) -> list[StandardizedPullRequestAuthor]:
        """
        Get the authors of a list of PRs

        Args:
            pr_list (list[StandardizedJFAPIPullRequest]): A list of PRs
        Returns:
            list[StandardizedPullRequestAuthor]: A list of PR authors
        """
        if not pr_list:
            return []

        logging_helper.send_to_agent_log_file(
            msg=f'Pulling PR authors for {len(pr_list)} PRs',
            level=logging.INFO,
        )

        # Map PRs for more efficient querying (org login -> repo name -> PR numbers)
        prs_sorted: dict[str, dict[str, list[int]]] = {}
        pr_std_authors: list[StandardizedPullRequestAuthor] = []

        for jf_pr in pr_list:
            if jf_pr.org_login not in prs_sorted:
                prs_sorted[jf_pr.org_login] = defaultdict(list)

            prs_sorted[jf_pr.org_login][jf_pr.repo_name].append(jf_pr.pr_number)

        pbar = tqdm(total=len(pr_list), desc='Pulling PR authors from GQL')

        for org_login, repo_name_to_prs in prs_sorted.items():
            for repo_name, pr_numbers in repo_name_to_prs.items():
                try:
                    query_result = self.client.get_pr_authors(org_login, repo_name, pr_numbers)
                    pr_std_authors.extend(
                        _standardize_pr_author(pr_number, repo_name, org_login, user_dict)
                        for pr_number, user_dict in query_result.items()
                    )
                except Exception as e:
                    logging_helper.send_to_agent_log_file(
                        msg=f'Error when attempting to pull PR authors for {org_login}/{repo_name}. Error: {e}',
                        level=logging.ERROR,
                    )
                    logging_helper.send_to_agent_log_file(
                        traceback.format_exc(), level=logging.ERROR
                    )

                pbar.update(len(pr_numbers))

        pbar.close()

        logging_helper.send_to_agent_log_file(
            msg=f'Successfully pulled {len(pr_std_authors)}/{len(pr_list)} PR authors',
            level=logging.INFO,
        )
        return pr_std_authors

    def git_provider_pr_endpoint_supports_date_filtering(self):
        return False

    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: Optional[int] = None,
        start_cursor: Optional[Any] = None,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,  # Not used in Github
    ) -> Generator[StandardizedPullRequest, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_id = standardized_repo.id
            repo_name = self.repo_id_to_name_lookup[repo_id]
            repo_metadata = self.repo_id_to_repo_meta_data[repo_id]
            if not repo_metadata.latest_pr_updated_at:
                logging_helper.send_to_agent_log_file(
                    f'Not querying for PR data, because the repo meta for {standardized_repo.name} indicates that there are no PRs'
                )
                return
            if start_window and repo_metadata.latest_pr_updated_at <= start_window:
                logging_helper.send_to_agent_log_file(
                    f'Not querying for PR data, because the repo meta for {standardized_repo.name} indicates that the latest PR '
                    f'was updated on {repo_metadata.latest_pr_updated_at} before our pull from window {start_window}'
                )
                return

            try:
                labels_for_repository = self.client.get_labels_for_repository(
                    org_login=standardized_repo.organization.login, repo_name=repo_name
                )
                label_node_id_to_id = {
                    label['node_id']: label['id'] for label in labels_for_repository
                }
            except Exception as e:
                logging_helper.send_to_agent_log_file(
                    msg=f'Error when attempting to pull Labels for Repo {repo_name}. Error: {e}',
                    level=logging.ERROR,
                )
                logging_helper.send_to_agent_log_file(
                    msg=traceback.format_exc(), level=logging.ERROR
                )
                label_node_id_to_id = {}

            api_prs = self.client.get_prs(
                login=login,
                repo_name=repo_name,
                include_top_level_comments=self.config.jf_options.get(
                    'get_all_issue_comments', False
                ),
                include_force_push_commits=self.config.jf_options.get(
                    'include_force_push_commits', False
                ),
                start_cursor=start_cursor,
                pull_files_for_pr=pull_files_for_pr,
                hash_files_for_prs=hash_files_for_prs,
                repository_label_node_ids_to_id=label_node_id_to_id,
            )
            for j, api_pr in enumerate(
                api_prs,
                start=1,
            ):
                try:
                    yield _standardize_pr(
                        api_pr,
                        standardized_repo,
                    )
                    if limit and j >= limit:
                        return
                except Exception:
                    # if something goes wrong with normalizing one of the prs - don't stop pulling. try
                    # the next one.
                    pr_id = f' {api_pr["id"]}' if api_pr else ''
                    logger.warning(
                        f'normalizing PR {pr_id} from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
                    )
                    logging_helper.send_to_agent_log_file(
                        traceback.format_exc(), level=logging.ERROR
                    )

        except Exception:
            # if something happens when pulling PRs for a repo, just keep going.
            logger.warning(
                f'normalizing PRs from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...'
            )
            logging_helper.send_to_agent_log_file(traceback.format_exc(), level=logging.ERROR)


'''

    Massage Functions

'''


def _standardize_user(api_user) -> StandardizedUser:
    id = api_user.get('id')
    name = api_user.get('name')
    login = api_user.get('login')
    email = api_user.get('email')

    # Mannequin users will have 'GitHubArchive\\' prepended to the name of their
    # account, which needs to be removed
    if isinstance(name, str) and name.startswith('GitHubArchive\\'):
        name = name.split('\\', 1)[1]

    # raw user, just have email (e.g. from a commit)
    if not id:
        return StandardizedUser(
            id=email,
            login=email,
            name=name,
            email=email,
        )

    # API user, where github matched to a known account
    return StandardizedUser(id=id, login=login, name=name, email=email)


def _standardize_team(api_team: Dict) -> StandardizedTeam:
    return StandardizedTeam(
        id=str(api_team.get('id', '')),
        name=api_team.get('name', ''),
        slug=api_team.get('slug', ''),
        description=api_team.get('description'),
        members=[_standardize_user(member) for member in api_team.get('members', []) if member],
    )


def _standardize_organization(api_org: Dict) -> StandardizedOrganization:
    return StandardizedOrganization(
        id=api_org['id'],
        login=api_org['login'],
        name=api_org.get('name'),
        url=api_org['url'],
    )


def _standardize_branch(
    api_branch, repo_id: str, is_default_branch: bool
) -> Optional[StandardizedBranch]:
    if not api_branch:
        return None
    if not api_branch['name']:
        return None
    return StandardizedBranch(
        repo_id=repo_id,
        name=api_branch['name'],
        sha=api_branch['target']['sha'],
        is_default=is_default_branch,
    )


def _standardize_repo(
    api_repo,
    standardized_organization: StandardizedOrganization,
) -> StandardizedRepository:
    repo_name = api_repo['name']
    url = api_repo['url']

    # NOTE: If a repo is completely empty, than there will be no default branch.
    # in that case, the standardized_default_branch object will be None
    standardized_default_branch = _standardize_branch(
        api_repo['defaultBranch'],
        repo_id=api_repo['id'],
        is_default_branch=True,
    )
    default_branch_name = standardized_default_branch.name if standardized_default_branch else None
    default_branch_sha = standardized_default_branch.sha if standardized_default_branch else None

    return StandardizedRepository(
        id=str(api_repo['id']),
        name=repo_name,
        full_name=f'{standardized_organization.login}/{repo_name}',
        url=url,
        default_branch_name=default_branch_name,
        default_branch_sha=default_branch_sha,
        is_fork=api_repo['isFork'],
        organization=standardized_organization,
    )


def _standardize_short_form_repo(api_repo: Dict) -> StandardizedShortRepository:
    return StandardizedShortRepository(
        id=str(api_repo['id']), name=api_repo['name'], url=api_repo['url']
    )


def _standardize_commit(
    api_commit: Dict,
    standardized_repo: StandardizedRepository,
    branch_name: str,
):
    author = _standardize_user(api_commit['author'])
    commit_url = api_commit['url']
    return StandardizedCommit(
        hash=api_commit['sha'],
        author=author,
        url=commit_url,
        commit_date=gql_format_to_datetime(api_commit['committedDate']),
        author_date=gql_format_to_datetime(api_commit['authoredDate']),
        message=api_commit['message'],
        is_merge=api_commit['parents']['totalCount'] > 1,
        repo=standardized_repo.short(),  # use short form of repo
        branch_name=branch_name,
    )


def _get_standardized_pr_comments(api_comments: List[Dict]) -> List[StandardizedPullRequestComment]:
    return [
        StandardizedPullRequestComment(
            user=_standardize_user(api_comment['author']),
            body=api_comment['body'],
            created_at=parser.parse(api_comment['createdAt']),
        )
        for api_comment in api_comments
    ]


def _get_standardized_reviews(api_reviews: List[Dict]):
    return [
        StandardizedPullRequestReview(
            user=_standardize_user(api_review['author']),
            foreign_id=api_review['id'],
            review_state=PullRequestReviewState[api_review['state']].name,
        )
        for api_review in api_reviews
    ]


def _standardize_pr(
    api_pr: Dict,
    standardized_repo: StandardizedRepository,
):
    base_branch_name = api_pr['baseRefName']
    head_branch_name = api_pr['headRefName']
    standardized_merge_commit = (
        _standardize_commit(
            api_pr['mergeCommit'],
            standardized_repo=standardized_repo,
            branch_name=base_branch_name,
        )
        if api_pr['mergeCommit']
        else None
    )

    return StandardizedPullRequest(
        id=api_pr['id'],
        additions=api_pr['additions'],
        deletions=api_pr['deletions'],
        changed_files=api_pr['changedFiles'],
        created_at=gql_format_to_datetime(api_pr['createdAt']),
        updated_at=gql_format_to_datetime(api_pr['updatedAt']),
        merge_date=gql_format_to_datetime(api_pr['mergedAt']) if api_pr['mergedAt'] else None,
        closed_date=gql_format_to_datetime(api_pr['closedAt']) if api_pr['closedAt'] else None,
        is_closed=api_pr['state'].lower() == 'closed',
        is_merged=api_pr['merged'],
        url=api_pr['url'],
        base_branch=base_branch_name,
        head_branch=head_branch_name,
        title=api_pr['title'],
        body=api_pr['body'],
        # standardized fields
        commits=[
            _standardize_commit(
                api_commit=commit,
                standardized_repo=standardized_repo,
                branch_name=head_branch_name,
            )
            for commit in api_pr['commits']
        ],
        merge_commit=standardized_merge_commit,
        author=_standardize_user(api_user=api_pr['author']),
        merged_by=_standardize_user(api_user=api_pr['mergedBy']) if api_pr['mergedBy'] else None,
        approvals=_get_standardized_reviews(api_pr['reviews']),
        comments=_get_standardized_pr_comments(api_pr['comments']),
        base_repo=_standardize_short_form_repo(api_pr['baseRepository']),
        head_repo=_standardize_short_form_repo(api_pr['baseRepository']),
        labels=[
            StandardizedLabel(
                id=label['id'],
                name=label['name'],
                default=label['default'],
                description=label['description'],
            )
            for label in api_pr.get('labels', [])
        ],
        files={
            file_name: StandardizedFileData(
                status=file_data['status'],
                changes=file_data['changes'],
                additions=file_data['additions'],
                deletions=file_data['deletions'],
            )
            for file_name, file_data in api_pr.get('files', {}).items()
        },
    )


def _standardize_pr_author(
    pr_number: int, repo_name: str, org_login: str, user_dict: dict[str, Union[str, None]]
) -> StandardizedPullRequestAuthor:
    return StandardizedPullRequestAuthor(
        pr_number=pr_number,
        repo_name=repo_name,
        org_login=org_login,
        user_id=user_dict.get('id'),
        user_login=user_dict.get('login'),
        user_name=user_dict.get('name'),
        user_email=user_dict.get('email'),
    )
