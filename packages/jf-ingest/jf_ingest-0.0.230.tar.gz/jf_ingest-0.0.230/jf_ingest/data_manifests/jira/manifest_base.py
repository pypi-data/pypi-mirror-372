from dataclasses import dataclass, field
from datetime import date, datetime
from typing import ClassVar, List, Optional, TypeAlias, TypeVar

from jf_ingest.data_manifests.manifest_base import ManifestBase


# Separating the model from the adapter behavior as a base class to make the data more transportable and reusable
@dataclass
class JiraProjectManifestBase(ManifestBase):
    project_id: Optional[str] = field(default=None)
    project_key: Optional[str] = field(default=None)
    issues_count: Optional[int] = field(default=None)
    version_count: Optional[int] = field(default=None)
    # This reflects if a client has intentionally excluded
    # a project from being ingested
    excluded: bool = field(default=False)
    # Pull from date
    pull_from: Optional[date] = field(default=None)
    # Latest issue updated date
    last_issue_updated_date: Optional[datetime] = field(default=None)
    # Allocation Status
    classification: Optional[int] = field(default=None)
    # Human readable allocation status.
    # Values pulled from JiraProjectClassification.CLASSIFICATION_CHOICES
    classification_str: Optional[str] = field(default=None)


IJiraProjectManifest = TypeVar('IJiraProjectManifest', bound='JiraProjectManifestBase')
IJiraProjectManifestList: TypeAlias = list[IJiraProjectManifest]


# Separating the model from the adapter behavior as a base class to make the data more transportable and reusable
@dataclass
class JiraDataManifestBase(ManifestBase):
    # Pull from date
    pull_from: Optional[date] = field(default=None)

    # Counts
    users_count: Optional[int] = field(default=None)
    fields_count: Optional[int] = field(default=None)
    resolutions_count: Optional[int] = field(default=None)
    issue_types_count: Optional[int] = field(default=None)
    issue_link_types_count: Optional[int] = field(default=None)
    priorities_count: Optional[int] = field(default=None)
    projects_count: Optional[int] = field(default=None)
    project_versions_count: Optional[int] = field(default=None)
    boards_count: Optional[int] = field(default=None)
    # Adheres to Pull From Date and (in remote manifests)
    # a project that we have excluded is zero'd out,
    # i.e. even if we can see issues in that project we
    # consider it to have 0 issues since we won't ingest any
    issues_count: Optional[int] = field(default=None)

    # Drill down into each project with ProjectManifests
    project_manifests: IJiraProjectManifestList = field(default_factory=list)

    # For debug purposes. We may want to optionally exclude this when serializing
    encountered_errors_for_projects: dict = field(default_factory=dict)


IJiraDataManifest = TypeVar('IJiraDataManifest', bound='JiraDataManifestBase')
