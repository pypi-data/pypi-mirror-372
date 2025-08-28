import logging
from datetime import datetime, timedelta, timezone
from itertools import chain
from typing import Any, Dict, Generator, List, Optional, cast

from dateutil import parser

from jf_ingest import logging_helper
from jf_ingest.config import GitConfig
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.clients.azure_devops import AzureDevopsClient
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
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.utils import hash_filename


class AzureDevopsAdapter(GitAdapter):
    def __init__(self, config: GitConfig):
        # Git Config options
        self.client = AzureDevopsClient(config.git_auth_config)
        self.config = config
        self.repo_id_to_name_lookup: Dict[str, str] = {}
        self.repo_id_to_project_name: Dict[str, str] = {}
        self.org_to_project_names: Dict[str, List[str]] = {}

        for org in self.config.git_organizations:
            if len(org.split('/')) == 2:
                org_name, project_name = org.split('/')
                if org_name in self.org_to_project_names:
                    self.org_to_project_names[org_name].append(project_name)
                else:
                    self.org_to_project_names[org_name] = [project_name]
            else:
                self.org_to_project_names[org] = []

    @property
    def supports_get_all_users(self) -> bool:
        """
        mpk 5/12/23: Azure DevOps Server 2020 (on-prem, encountered for at least one client) does NOT support a
        get_all_users method in the API. Cloud-based Azure DevOps Services (i.e., dev.azure.com) does. We
        haven't yet encountered other ADO server versions (like ADO Server 2022), so don't know whether or
        not those other versions will support get_all_users. For now I'll just assume that anything that
        runs the API version "6.1*" (like ADO Server 2020) will NOT support get_all_users.

        Returns:
            bool: True if we are in a version that is not 6.1
        """
        return not self.client.api_version.startswith('6.1')

    def _project_name_from_repo(self, standardized_repo: StandardizedRepository) -> str:
        '''
        The Project Name should be pre-loaded into the self.repo_id_to_project_name object,
        which gets set in the adapter get_repos function, and mapped to the repo ID. If
        it isn't, call the get_all_repos() client function again and save the results
        to the adapter.

        Returns the project name of the provided standardized_repo
        '''
        if project_name := self.repo_id_to_project_name.get(standardized_repo.id):
            return project_name
        else:
            logging_helper.send_to_agent_log_file(
                f'Repos were not preloaded? Loading them now', level=logging.WARNING
            )
            for repo in self.client.get_all_repos(org_name=standardized_repo.organization.login):
                self.repo_id_to_project_name[repo['id']] = repo['project']['name']

        return self.repo_id_to_project_name[standardized_repo.id]

    def get_organizations(self) -> List[StandardizedOrganization]:
        return [
            _standardize_organization(org, self.client.base_url)
            for org in self.org_to_project_names.keys()  # Set up the login to match only the Org, not the included project name(s)
        ]

    def get_api_scopes(self) -> str:
        raise NotImplementedError()

    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        i = 1
        for api_user in self.client.get_graph_users(org_name=standardized_organization.login):
            standardized_user = _standardize_graph_user(api_user)
            if standardized_user:
                yield standardized_user
                if limit and i >= limit:
                    return
                i += 1

    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedTeam, None, None]:
        for i, api_team in enumerate(
            self.client.get_teams(org_name=standardized_organization.login), start=1
        ):
            api_team_members = self.client.get_team_users(
                org_name=standardized_organization.login, team_descriptor=api_team['descriptor']
            )
            yield _standardize_team(api_team, api_team_members=api_team_members)
            if limit and i >= limit:
                return

    def get_repos(
        self,
        standardized_organization: StandardizedOrganization,
        limit: Optional[int] = None,
        only_private: bool = False,
    ) -> Generator[StandardizedRepository, None, None]:
        # Note: the only_private param is unused here, since we don't use the 'include hidden repositories'
        # flag when querying for repos from the ADO API. If this changes in the future, we'll need to add
        # this functionality
        org_name = standardized_organization.login
        project_names_in_org = self.org_to_project_names.get(org_name, [])

        if project_names_in_org:
            org_project_names = [
                f'{org_name}/{_project_name}' for _project_name in project_names_in_org
            ]
        else:
            org_project_names = [org_name]

        for org_project_name in org_project_names:
            for idx, api_repo in enumerate(
                self.client.get_all_repos(org_name=org_project_name), start=1
            ):
                project_name = api_repo['project']['name']
                if f'{org_name}/{project_name}' in self.config.excluded_organizations:
                    continue
                self.repo_id_to_project_name[api_repo['id']] = project_name
                yield _standardize_repo(
                    org=standardized_organization,
                    api_repo=api_repo,
                )

                if limit and idx >= limit:
                    return

    def get_repos_count(
        self, standardized_organization: StandardizedOrganization, only_private: bool = False
    ) -> int:
        """
        Get the count of repos in the organization. only_private is ignored here, since we don't normally pull
        hidden ADO repos

        Args:
            standardized_organization: A StandardizedOrganization object
            only_private: Ignored for ADO

        Returns:
            int: The count of repos in the organization
        """
        org_name = standardized_organization.login
        project_names_in_org = self.org_to_project_names.get(org_name, [])

        if project_names_in_org:
            org_project_names = [
                f'{org_name}/{_project_name}' for _project_name in project_names_in_org
            ]
        else:
            org_project_names = [org_name]

        count = 0
        for org_project_name in org_project_names:
            count += len(self.client.get_all_repos(org_name=org_project_name))

        return count

    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        for i, api_commit in enumerate(
            self.client.get_commits(
                org_name=standardized_repo.organization.login,
                project_name=self._project_name_from_repo(standardized_repo),
                repo_id=standardized_repo.id,
                branch_name=standardized_repo.default_branch_name,
                from_date=pull_since,
                to_date=pull_until,
            ),
            start=1,
        ):
            yield _standardize_commit(
                api_commit,
                branch_name=standardized_repo.default_branch_name,
                standardized_repo=standardized_repo,
            )
            if limit and i >= limit:
                return

    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_branches: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> Generator[StandardizedBranch, None, None]:
        if pull_branches:
            for idx, api_branch in enumerate(
                self.client.get_branches(
                    org_name=standardized_repo.organization.login,
                    project_name=self._project_name_from_repo(standardized_repo),
                    repo_id=standardized_repo.id,
                ),
                start=1,
            ):
                if standardized_branch := _standardize_branch(
                    api_branch=api_branch, standardized_repo=standardized_repo
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
        pulled_commit_count = 0

        for branch_name in self.get_filtered_branches(standardized_repo, branches):
            try:
                login = standardized_repo.organization.login
                for api_commit in self.client.get_commits(
                    org_name=login,
                    project_name=self._project_name_from_repo(standardized_repo),
                    repo_id=standardized_repo.id,
                    branch_name=branch_name,
                    from_date=pull_since,
                    to_date=pull_until,
                ):
                    yield _standardize_commit(
                        api_commit=api_commit,
                        branch_name=branch_name,
                        standardized_repo=standardized_repo,
                    )

                    pulled_commit_count += 1
                    if limit and pulled_commit_count >= limit:
                        return

            except Exception as e:
                logging_helper.send_to_agent_log_file(
                    f'Got exception for branch {branch_name}: {e}. Skipping...',
                    level=logging.WARNING,
                )

    def get_pr_updated_date(
        self, standardized_repo: StandardizedRepository, api_pr: Dict
    ) -> datetime:
        if 'closedDate' in api_pr:
            return cast(datetime, parser.parse(api_pr['closedDate']))

        org_name = standardized_repo.organization.login
        project_name = self._project_name_from_repo(standardized_repo)
        repo_id = standardized_repo.id
        pr_iterations = self.client.get_pull_request_iterations(
            org_name=org_name,
            project_name=project_name,
            repo_id=repo_id,
            pr_id=api_pr['pullRequestId'],
        )
        assert len(pr_iterations) > 0
        # Get the latest iteration and grab the updatedDate value
        return cast(datetime, parser.parse(pr_iterations[-1]['updatedDate']))

    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pr_pull_from_date: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        supports_pr_filter_func = self.git_provider_pr_endpoint_supports_date_filtering
        raise NotImplementedError(
            'This function is NOT implemented, because ADO supports PR date filtering '
            f'({supports_pr_filter_func.__name__} is {supports_pr_filter_func()})'
        )

    def git_provider_pr_endpoint_supports_date_filtering(self):
        return True

    def _get_prs_helper(
        self,
        standardized_repo: StandardizedRepository,
        start_window: Optional[datetime],
        end_window: Optional[datetime],
    ) -> Generator[Dict, None, None]:
        tomorrow = datetime.now().astimezone(timezone.utc) + timedelta(days=1)

        def _get_prs_from_client_wrapper(
            _end_window: Optional[datetime], status: str, filter_by: str
        ):
            return self.client.get_pull_requests(
                org_name=standardized_repo.organization.login,
                project_name=self._project_name_from_repo(standardized_repo=standardized_repo),
                repo_id=standardized_repo.id,
                start_window=start_window,
                end_window=_end_window,
                status=status,
                filter_by=filter_by,
            )

        abandoned_prs_generator = _get_prs_from_client_wrapper(end_window, 'abandoned', 'closed')
        completed_prs_generator = _get_prs_from_client_wrapper(end_window, 'completed', 'closed')
        active_prs = _get_prs_from_client_wrapper(tomorrow, 'active', 'open')
        return cast(
            Generator[Dict, None, None],
            chain(abandoned_prs_generator, completed_prs_generator, active_prs),
        )

    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: Optional[int] = None,  # Not used by ADO adapter
        start_cursor: Any = 0,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        try:
            login = standardized_repo.organization.login
            repo_id = standardized_repo.id
            project_name = self._project_name_from_repo(standardized_repo)

            api_prs = self._get_prs_helper(
                standardized_repo=standardized_repo,
                start_window=start_window,
                end_window=end_window,
            )

            for i, api_pr in enumerate(
                api_prs,
                start=1,
            ):
                try:
                    pr_id = api_pr['pullRequestId']
                    head_branch = api_pr['sourceRefName'].replace('refs/heads/', '')
                    base_branch = api_pr['targetRefName'].replace('refs/heads/', '')
                    files = {}
                    changed_count = 0
                    additions = 0
                    deletions = 0
                    if 'lastMergeTargetCommit' in api_pr and 'lastMergeCommit' in api_pr:
                        change_counts = self.client.get_pull_request_changes_counts(
                            org_name=login,
                            repo_id=standardized_repo.id,
                            base_sha=api_pr['lastMergeTargetCommit']['commitId'],
                            target_sha=api_pr['lastMergeCommit']['commitId'],
                        )
                        changed_count = sum(change_counts.values())
                        additions = change_counts.get('Add', 0)
                        deletions = change_counts.get('Delete', 0)
                        if pull_files_for_pr:
                            changes = self.client.get_pull_request_diff(
                                org_name=login,
                                repo_id=standardized_repo.id,
                                base_sha=api_pr['lastMergeTargetCommit']['commitId'],
                                target_sha=api_pr['lastMergeCommit']['commitId'],
                            )
                            files = {
                                c['item']['path']: StandardizedFileData(
                                    status=c.get('changedType', ''),
                                    changes=0,
                                    additions=0,
                                    deletions=0,
                                )
                                for c in changes
                                if not c['item'].get('isFolder', False)
                            }
                            if hash_files_for_prs:
                                files = {
                                    hash_filename(file_path): file_data
                                    for file_path, file_data in files.items()
                                }
                        else:
                            files = {}

                    pr_updated_at = self.get_pr_updated_date(
                        standardized_repo=standardized_repo, api_pr=api_pr
                    )

                    commits = [
                        _standardize_commit(
                            api_commit=api_commit,
                            branch_name=head_branch,
                            standardized_repo=standardized_repo,
                        )
                        for api_commit in self.client.get_pr_commits(
                            org_name=login,
                            project_name=project_name,
                            repo_id=repo_id,
                            pr_id=pr_id,
                        )
                    ]
                    # If a merge commit is in here, retroactively mark one of the commits
                    # as a merge commit
                    if api_pr['status'] == 'completed' and 'lastMergeCommit' in api_pr:
                        for commit in commits:
                            if commit.hash == api_pr['lastMergeCommit']['commitId']:
                                commit.is_merge = True

                    comments: List[StandardizedPullRequestComment] = []
                    reviews: List[StandardizedPullRequestReview] = []
                    for comment_thread in self.client.get_pr_comment_threads(
                        org_name=login, project_name=project_name, repo_id=repo_id, pr_id=pr_id
                    ):
                        comment_thread_id = comment_thread['id']
                        for api_comment in comment_thread['comments']:
                            comments.append(_standardize_pull_request_comment(api_comment))
                            pr_review = _standardize_pull_request_review(
                                api_comment=api_comment,
                                pr_id=pr_id,
                                comment_thread_id=comment_thread_id,
                            )

                            if pr_review:
                                reviews.append(pr_review)

                    labels = [label['name'] for label in api_pr.get('labels', [])]

                    yield _standardize_pull_request(
                        api_pr,
                        standardized_repo,
                        pr_updated_at=pr_updated_at,
                        commits=commits,
                        comments=comments,
                        approvals=reviews,
                        labels=labels,
                        additions=additions,
                        deletions=deletions,
                        changed_count=changed_count,
                        files=files,
                    )
                    if limit and i >= limit:
                        return
                except Exception:
                    # if something goes wrong with normalizing one of the prs - don't stop pulling. try
                    # the next one.
                    pr_id = api_pr.get('id', '?')
                    logging_helper.send_to_agent_log_file(
                        f'normalizing PR {pr_id} from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...',
                        level=logging.WARNING,
                        exc_info=True,
                    )

        except Exception:
            logging_helper.send_to_agent_log_file(
                f'normalizing PRs from repo {standardized_repo.name} ({standardized_repo.id}). Skipping...',
                level=logging.WARNING,
                exc_info=True,
            )

    def get_pr_authors(
        self, pr_list: list[StandardizedJFAPIPullRequest]
    ) -> list[StandardizedPullRequestAuthor]:
        """
        Get the authors of a list of PRs

        This is currently NOT IMPLEMENTED for ADO instances
        """
        return []


'''

Massage Functions (standardize raw JSON data to StandardizedPython Models)

'''


def _standardize_graph_user(api_user: Dict) -> Optional[StandardizedUser]:
    """Standardize the raw GraphUser type to our StandardizedUser.
    This is for users returned from the "Graph" API.
    https://learn.microsoft.com/en-us/rest/api/azure/devops/graph/users/list?view=azure-devops-rest-7.1&tabs=HTTP#graphuser

    Args:
        api_user (Dict): A raw dictionary from the ADO API representing a GraphUser

    Returns:
        StandardizedUser: A standardized User object
    """
    if not (user_id := api_user.get('descriptor')):
        return None
    return StandardizedUser(
        id=user_id,
        login=api_user['principalName'],
        name=api_user['displayName'],
        email=api_user['mailAddress'],
        url=api_user['url'],
    )


def _standardize_team(api_team: Dict, api_team_members: List[Dict]) -> StandardizedTeam:
    members = []
    for member in api_team_members:
        if standardized_member := _standardize_graph_user(member):
            members.append(standardized_member)

    return StandardizedTeam(
        id=api_team['descriptor'],
        slug=api_team['descriptor'],
        name=api_team['displayName'],
        description=api_team['description'],
        members=members,
    )


def _standardize_repo(org: StandardizedOrganization, api_repo: dict) -> StandardizedRepository:
    # Sanitize Repo Name
    repo_name = api_repo['name']

    # Sanitize URL
    url = api_repo['webUrl']

    # Sanitize Branch Name
    if 'defaultBranch' in api_repo:
        default_branch_name = api_repo['defaultBranch'].replace('refs/heads/', '')
    else:
        default_branch_name = None

    return StandardizedRepository(
        id=api_repo['id'],
        name=repo_name,
        full_name=f'{org.login}/{repo_name}',
        url=url,
        is_fork=api_repo.get('isFork', False),
        organization=org,
        default_branch_name=default_branch_name,
        default_branch_sha=None,  # TODO: looks like this isn't part of the base object, is it important? Do we NEED it?
    )


def _standardize_branch(
    api_branch: dict, standardized_repo: StandardizedRepository
) -> Optional[StandardizedBranch]:
    if not api_branch:
        return None
    if not api_branch.get('name'):
        return None

    branch_name = api_branch['name'].replace('refs/heads/', '')
    return StandardizedBranch(
        repo_id=standardized_repo.id,
        name=api_branch['name'].replace('refs/heads/', ''),
        sha=api_branch['objectId'],
        is_default=branch_name == standardized_repo.default_branch_name,
    )


def _standardize_git_user_data(user: Dict) -> Optional[StandardizedUser]:
    """Standardize the GitUserDate type, which is the type of user returned
    on commits.
    https://learn.microsoft.com/en-us/rest/api/azure/devops/git/commits/get-commits?view=azure-devops-rest-7.1&tabs=HTTP#gituserdate

    Args:
        user (Dict): A GitUserDict returned from the API

    Returns:
        StandardizedUser: The Standardized User
    """
    if not (email := user.get('email')):
        return None
    return StandardizedUser(
        id=email,
        name=user.get('name'),
        login=email,
        email=email,
        url=None,
        account_id=None,
    )


def _standardize_organization(org_login: str, url: str) -> StandardizedOrganization:
    # TODO this is probably wrong
    return StandardizedOrganization(
        id=org_login,
        name=org_login,
        login=org_login,
        url=url,
    )


def _standardize_commit(
    api_commit: dict,
    branch_name: Optional[str],
    standardized_repo: StandardizedRepository,
) -> StandardizedCommit:
    # NOTE: The commit object only returns "GitUserDate" types
    author = _standardize_git_user_data(api_commit['author'])
    return StandardizedCommit(
        hash=api_commit['commitId'],
        url=api_commit['url'],
        message=api_commit['comment'],
        branch_name=branch_name,
        commit_date=parser.parse(api_commit['committer']['date']),
        author_date=parser.parse(api_commit['author']['date']),
        author=author if author else None,
        repo=standardized_repo.short(),
        # XXX: The commit we get back from the API doesn't include the "parents" item; the docs seem
        # to indicate it's supposed to. Without having the "parents" item, we can't tell whether or
        # not the commit is a merge commit. I think we could get the "parents" item if we use the
        # "Get" API to get a single commit rather than the "GetCommits" API to get a list of commits.
        # But that'd cause us to make way more API requests. For now at least let's avoid that and
        # just set is_merge to False (perhaps erroneously) for all commits.
        # NOTE (update): For Pull Requests we WILL mark merge commits properly as part of PR Ingestion.
        # In theory all, if not most, merge commits will come to us via PRs, so we should eventaully
        # mark all merge commits with this strategy
        is_merge=False,
    )


def _standardize_identity_ref_user(user: Dict) -> StandardizedUser:
    """Standardize the ADO IdentityRef User object.
    This is the type commonly returned by the PR related data objects.
    https://learn.microsoft.com/en-us/rest/api/azure/devops/git/pull-request-threads/list?view=azure-devops-rest-7.1&tabs=HTTP#identityref

    Args:
        user (Dict): A raw "IdentityRef" object type from ADO

    Returns:
        StandardizedUser: A standardized User Object
    """
    user_id = user.get('descriptor') or user.get('uniqueName') or user.get('id')
    return StandardizedUser(
        id=str(user_id),
        name=user.get('displayName'),
        login=str(user_id),
        email=user.get('uniqueName'),
        url=user['url'],
        account_id=user['id'],
    )


def _standardize_pull_request_review(
    api_comment: Dict, pr_id: int, comment_thread_id: int
) -> Optional[StandardizedPullRequestReview]:
    """Normalize an API comment into a review.
    State is derived by checking if this is a system comment type, and by
    checking the comment content.
    User is derived from the comment dictionary
    foreign-id is derived from Pull Request ID, Comment Thread ID, and Comment ID. Honestly,
    this probably isn't that useful but at least it's something

    Args:
        api_comment (Dict): Used to derive approval state and commenter
        pr_id (int): Used as part of the Foreign ID field
        comment_thread_id (int): Used as part of the Foreign ID field

    Returns:
        StandardizedPullRequestReview: A standardized Pull Request Review
    """
    api_comment_author = api_comment['author']
    commenter = (
        _standardize_identity_ref_user(api_comment_author)
        if 'uniqueName' in api_comment_author
        else None
    )

    comment_type = api_comment.get('commentType', '')
    comment_content = api_comment.get('content', '')

    # If the comment is an approval, construct a StandardizedPullRequestApproval
    review_state: Optional[PullRequestReviewState] = None
    if comment_type == 'system' and 'voted 5' in comment_content:
        # This is "approved the pull request with suggestions"
        review_state = PullRequestReviewState.APPROVED
    elif comment_type == 'system' and 'voted 10' in comment_content:
        # This is "approved the pull request"
        review_state = PullRequestReviewState.APPROVED
    elif comment_type == 'system' and 'voted -10' in comment_content:
        # This is "rejected the pull request"
        review_state = PullRequestReviewState.DISMISSED
    elif comment_type == 'system' and 'voted -5' in comment_content:
        # This is "is waiting for the author"
        review_state = PullRequestReviewState.CHANGES_REQUESTED
    elif comment_type == 'text':
        review_state = PullRequestReviewState.COMMENTED

    if review_state:
        return StandardizedPullRequestReview(
            user=commenter,
            foreign_id=f"{pr_id}-{comment_thread_id}-{api_comment['id']}",
            review_state=review_state.name,
        )
    return None


def _standardize_pull_request_comment(
    api_comment: Dict,
) -> StandardizedPullRequestComment:
    api_comment_author = api_comment['author']
    commenter = (
        _standardize_identity_ref_user(api_comment_author)
        if 'uniqueName' in api_comment_author
        else None
    )
    comment_body = api_comment.get('content', '')
    return StandardizedPullRequestComment(
        user=commenter,
        body=comment_body,
        created_at=parser.parse(api_comment['publishedDate']),
        system_generated=api_comment.get('commentType') == 'system',
    )


def _standardize_pull_request(
    api_pr: Dict,
    standardized_repo: StandardizedRepository,
    pr_updated_at: datetime,
    commits: List[StandardizedCommit],
    comments: List[StandardizedPullRequestComment],
    approvals: List[StandardizedPullRequestReview],
    labels: List[StandardizedLabel],
    additions: int,
    deletions: int,
    changed_count: int,
    files: Dict[str, StandardizedFileData],
) -> StandardizedPullRequest:
    #
    # PR Status
    pr_status = api_pr['status']
    is_merged = pr_status == 'completed'
    is_closed = pr_status != 'active'
    closed_date = parser.parse(api_pr['closedDate']) if 'closedDate' in api_pr else None
    merge_date = closed_date if is_merged else None

    #
    # User Transformation
    author = _standardize_identity_ref_user(api_pr['createdBy'])

    merge_commits = [c for c in commits if c.is_merge]
    merge_commit = merge_commits[0] if len(merge_commits) == 1 else None
    if merge_commit:
        merged_by = merge_commit.author
    else:
        merged_by = None

    title = api_pr['title']
    body = api_pr.get('description', '')

    base_branch = api_pr['targetRefName'].replace('refs/heads/', '')
    head_branch = api_pr['sourceRefName'].replace('refs/heads/', '')

    return StandardizedPullRequest(
        id=api_pr['pullRequestId'],
        additions=additions,
        deletions=deletions,
        changed_files=changed_count,
        is_closed=is_closed,
        is_merged=is_merged,
        created_at=parser.parse(api_pr['creationDate']),
        updated_at=pr_updated_at,
        merge_date=merge_date,
        closed_date=closed_date,
        title=title,
        body=body,
        url=api_pr['url'],
        base_branch=base_branch,
        head_branch=head_branch,
        author=author,
        merged_by=merged_by if merged_by else None,
        commits=commits,
        merge_commit=merge_commit,
        comments=comments,
        approvals=approvals,
        base_repo=standardized_repo.short(),
        head_repo=standardized_repo.short(),
        labels=labels,
        files=files,
    )
