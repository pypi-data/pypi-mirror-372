from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Union

from jf_ingest.config import JiraDownloadConfig
from jf_ingest.data_manifests.manifest_base import ManifestSource


# Some Jellyfish core dependencies were removed from this definition.
# project_keys_to_classification_type is provided by the caller instead of relying on
# ambient context or Django ORM. This should also make the class more testable and reusable.
@dataclass
class ManifestAdapter(ABC):
    '''
    Abstract class for getting different Jira Manifests
    '''

    company_slug: str
    config: JiraDownloadConfig
    manifest_source: ManifestSource
    excluded_project_keys: set[str] = field(default_factory=set)
    project_keys_to_classification_type: Union[dict[str, str], MappingProxyType] = field(
        default=MappingProxyType({})
    )

    def __init__(
        self,
        config: JiraDownloadConfig,
        manifest_source: ManifestSource,
        project_keys_to_classification_type: Union[
            dict[str, str], MappingProxyType
        ] = MappingProxyType({}),
    ):
        self.company_slug = config.company_slug
        self.config = config
        self.manifest_source = manifest_source
        self.excluded_project_keys = set(config.exclude_projects)
        self.project_keys_to_classification_type = project_keys_to_classification_type

    @abstractmethod
    def get_users_count(self) -> int:
        pass

    @abstractmethod
    def get_fields_count(self) -> int:
        pass

    @abstractmethod
    def get_resolutions_count(self) -> int:
        pass

    @abstractmethod
    def get_issue_types_count(self) -> int:
        pass

    @abstractmethod
    def get_issue_link_types_count(self) -> int:
        pass

    @abstractmethod
    def get_priorities_count(self) -> int:
        pass

    @abstractmethod
    def get_project_data_dicts(self) -> list[dict]:
        pass

    @abstractmethod
    # Boards count is both a 'global' and a project_id
    # based value because you can have a personal Jira Board
    # that is associated with only a user and NOT a project.
    # This appears as the total board count being different
    # from the value you would get if you summed up the board_count
    # across all project manifests
    def get_boards_count(self) -> int:
        pass

    @abstractmethod
    def get_issues_count(self) -> int:
        pass

    @abstractmethod
    def get_project_versions_count(self) -> int:
        pass

    # EVERYTHING BELOW IS PROJECT SPECIFIC FUNCTIONS

    @abstractmethod
    def test_basic_auth_for_project(self, project_id: int) -> bool:
        pass

    @abstractmethod
    def get_project_versions_count_for_project(self, project_id: int) -> int:
        pass

    @abstractmethod
    def get_issues_count_for_project(self, project_id: int) -> int:
        pass

    @abstractmethod
    def get_issues_data_count_for_project(self, project_id: int) -> int:
        pass

    @abstractmethod
    def get_last_updated_for_project(self, project_id):
        pass
