from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from functools import wraps
from typing import Any, Dict, List, Optional

from jf_ingest.jf_git.utils import (
    branch_redactor,
    organization_redactor,
    repo_redactor,
    sanitize_text,
)


@dataclass
class StandardizedObject:
    def redact_names_and_urls(self):
        '''This method is used to redact names and urls from the object,
        it should be implemented by the child classes'''
        pass

    def strip_text_content(self):
        '''This method is used to strip text content from the object,
        it should be implemented by the child classes'''
        pass


@dataclass
class StandardizedUser(StandardizedObject):
    id: str
    name: Optional[str]
    login: str
    email: Optional[str] = None
    url: Optional[str] = None
    account_id: Optional[str] = None


@dataclass
class StandardizedTeam(StandardizedObject):
    id: str
    slug: str
    name: str
    description: Optional[str]
    members: list[StandardizedUser]


@dataclass
class StandardizedBranch(StandardizedObject):
    name: Optional[str]
    sha: Optional[str]
    repo_id: str
    is_default: bool

    def redact_names_and_urls(self):
        self.name = branch_redactor.redact_name(self.name)


@dataclass
class StandardizedOrganization(StandardizedObject):
    id: str
    name: Optional[str]
    login: str
    url: Optional[str]

    def redact_names_and_urls(self):
        self.name = organization_redactor.redact_name(self.name)
        self.url = None


@dataclass
class StandardizedShortRepository(StandardizedObject):
    id: str
    name: str
    url: str

    def redact_names_and_urls(self):
        self.name = repo_redactor.redact_name(self.name)
        self.url = None


@dataclass
class StandardizedRepository(StandardizedObject):
    id: str
    name: str
    full_name: str
    url: str
    is_fork: bool
    default_branch_name: Optional[str]
    default_branch_sha: Optional[str]
    organization: StandardizedOrganization
    branches: list = field(default_factory=list)
    commits_backpopulated_to: Optional[datetime] = None
    prs_backpopulated_to: Optional[datetime] = None
    full_path: Optional[str] = (
        None  # This is only used by the Gitlab adapter and is ignored during git import
    )

    def redact_names_and_urls(self):
        self.name = repo_redactor.redact_name(self.name)
        self.full_name = repo_redactor.redact_name(self.full_name)
        self.url = None

        if self.default_branch_name:
            self.default_branch_name = branch_redactor.redact_name(self.default_branch_name)

        self.organization.redact_names_and_urls()

    def short(self):
        # return the short form of Standardized Repository
        return StandardizedShortRepository(id=self.id, name=self.name, url=self.url)


@dataclass
class StandardizedCommit(StandardizedObject):
    hash: str
    url: str
    message: str
    commit_date: datetime
    author_date: datetime
    author: Optional[StandardizedUser]
    repo: StandardizedShortRepository
    is_merge: bool
    branch_name: Optional[str] = None

    def redact_names_and_urls(self):
        self.branch_name = branch_redactor.redact_name(self.branch_name)
        self.url = None
        self.repo.redact_names_and_urls()

    def strip_text_content(self):
        self.message = sanitize_text(self.message)


@dataclass
class StandardizedPullRequestComment(StandardizedObject):
    user: Optional[StandardizedUser]
    body: str
    created_at: datetime
    system_generated: Optional[bool] = None

    def strip_text_content(self):
        self.body = sanitize_text(self.body)


# TODO: This exists in the Jellyfish source code
# and has been copied over. The source code should be
# replaced with this, so we have one "source of truth".
# NOTE: These enum string values are based off of Github,
# we need to normalize all other providers to this
class PullRequestReviewState(IntEnum):
    UNKNOWN = 0
    PENDING = 1
    APPROVED = 2
    COMMENTED = 3
    CHANGES_REQUESTED = 4
    DISMISSED = 5


@dataclass
class StandardizedPullRequestReview(StandardizedObject):
    user: Optional[StandardizedUser]
    foreign_id: str
    review_state: str


@dataclass
class StandardizedLabel(StandardizedObject):
    id: int
    name: str
    default: bool
    description: str


@dataclass
class StandardizedFileData(StandardizedObject):
    status: str
    changes: int
    additions: int
    deletions: int


@dataclass
class StandardizedPullRequest(StandardizedObject):
    id: Any
    additions: int
    deletions: int
    changed_files: int
    is_closed: bool
    is_merged: bool
    created_at: datetime
    updated_at: datetime
    merge_date: Optional[datetime]
    closed_date: Optional[datetime]
    title: str
    body: str
    url: str
    base_branch: str
    head_branch: str
    author: StandardizedUser
    merged_by: Optional[StandardizedUser]
    commits: List[StandardizedCommit]
    merge_commit: Optional[StandardizedCommit]
    comments: List[StandardizedPullRequestComment]
    approvals: List[StandardizedPullRequestReview]
    base_repo: StandardizedShortRepository
    head_repo: StandardizedShortRepository
    labels: List[StandardizedLabel]
    files: Dict[str, StandardizedFileData]

    def redact_names_and_urls(self):
        self.base_branch = branch_redactor.redact_name(self.base_branch)
        self.head_branch = branch_redactor.redact_name(self.head_branch)
        self.url = None

        self.base_repo.redact_names_and_urls()
        self.head_repo.redact_names_and_urls()

        if self.merge_commit:
            self.merge_commit.redact_names_and_urls()

        for commit in self.commits:
            commit.redact_names_and_urls()

    def strip_text_content(self):
        self.title = sanitize_text(self.title)
        self.body = sanitize_text(self.body)

        for comment in self.comments:
            comment.strip_text_content()

        for commit in self.commits:
            commit.strip_text_content()

        if self.merge_commit:
            self.merge_commit.strip_text_content()


@dataclass
class StandardizedPullRequestMetadata(StandardizedObject):
    id: Optional[Any]
    updated_at: datetime
    # API Index place holder, needed if the adapter DOES NOT support PullRequest API Time filtering
    # (git_provider_pr_endpoint_supports_date_filtering)
    api_index: Optional[Any] = None


@dataclass
class StandardizedJFAPIPullRequest(StandardizedObject):
    pr_number: int
    repo_name: str
    org_login: str


@dataclass
class StandardizedPullRequestAuthor(StandardizedObject):
    # PR fields
    pr_number: int
    repo_name: str
    org_login: str

    # User fields
    # Not using StandardizedUser here to allow for less strict type
    # definitions, specifically when our search could result in users
    # that have been deleted from their GHC instance
    user_id: Optional[str] = None
    user_login: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
