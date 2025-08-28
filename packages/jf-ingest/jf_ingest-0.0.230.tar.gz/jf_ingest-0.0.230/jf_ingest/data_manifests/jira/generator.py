import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Protocol

from jira import JIRAError
from tqdm import tqdm

from jf_ingest.data_manifests.jira.adapters.manifest_adapter import ManifestAdapter
from jf_ingest.data_manifests.jira.manifest_base import (
    IJiraDataManifest,
    IJiraProjectManifest,
)
from jf_ingest.data_manifests.manifest_base import ManifestSource

logger = logging.getLogger(__name__)


class UnsupportedJiraProvider(Exception):
    pass


class ProjectManifestGenerationException(Exception):
    pass


# This function was moved from Jellyfish core along with base models for Jira manifests.
# It is used to generate a Jira manifest from a manifest adapter.
# The manifest adapter is a class that provides the necessary data to generate the manifest.
# create_jira_data_manifest and create_jira_project_manifest are callables that create the actual manifest objects.
#  This was done to retain the behavior of the original data/project manifests while avoiding circular imports.
# reset_current_tenant is a callable that resets the current tenant in the Jellyfish ORM when spawning threads.
#  This is passed in because jf_ingest has no concept of Django ORM and to avoid a circular import.
def create_manifest(
    manifest_adapter: ManifestAdapter,
    classifications_name_lookup,
    reset_current_tenant: Callable,
    create_jira_data_manifest: Callable,
    create_jira_project_manifest: Callable,
) -> type[IJiraDataManifest]:
    config = manifest_adapter.config
    project_data_dicts = manifest_adapter.get_project_data_dicts()

    jira_manifest = None
    # Total threads includes all potential project manifests
    # plus one 'global' jira manifest thread that will get
    # all totals (sprints, boards, issues, etc)
    total_threads = len(project_data_dicts) + 1
    with tqdm(total=total_threads) as pbar:
        with ThreadPoolExecutor(max_workers=config.issue_download_concurrent_threads) as executor:
            pbar.set_description('Processing Jira Projects')

            def _update_pbar_from_future(future):
                pbar.update(1)

            # Create future for global Jira Manifest. This will be our main JiraManifest,
            # and we will add Project Manifests to it
            generate_base_manifest_future: Any = executor.submit(
                process_global_jira_data,
                manifest_adapter,
                create_jira_data_manifest,
                reset_current_tenant,
            )
            # Add callback
            generate_base_manifest_future.add_done_callback(_update_pbar_from_future)

            # generate futures for project manifests
            project_future_to_project_key: dict = {
                executor.submit(
                    generate_project_manifest,
                    manifest_adapter,
                    project_data_dict,
                    classifications_name_lookup,
                    create_jira_project_manifest,
                    reset_current_tenant,
                ): project_data_dict['key']
                for project_data_dict in project_data_dicts
            }

            # Add callbacks for project manifest futures
            for f in project_future_to_project_key.keys():
                f.add_done_callback(_update_pbar_from_future)

            # Process future results and handle exceptions
            project_keys_to_errors = {}
            project_manifests: list[IJiraDataManifest] = []
            for future in project_future_to_project_key.keys():
                # Track exceptions and log them in a dictionary
                # so we can map project keys to detected exceptions
                if future.exception():
                    project_keys_to_errors[project_future_to_project_key[future]] = (
                        future.exception()
                    )
                else:
                    project_manifests.append(future.result())

            pbar.set_description('Processing Jira Global Values')

            # Load base Jira Manifest object from globals generator
            jira_manifest = generate_base_manifest_future.result()

            # For sorting/typing, we can't allow None values as a key.
            def _get_project_manifests_project_key(project_manifest: IJiraProjectManifest) -> str:
                project_key: str = project_manifest.project_key or ''
                return project_key

            # Append additional manifests (only project manifests, counts related to excluded project manifest, etc)
            jira_manifest.project_manifests = sorted(
                project_manifests, key=_get_project_manifests_project_key
            )
            jira_manifest.encountered_errors_for_projects = project_keys_to_errors

            pbar.set_description('Done!')

    logger.info('Done processing Jira Manifest!')
    return_value: type[IJiraDataManifest] = jira_manifest
    return return_value


class CreateJiraProjectManifestProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> type[IJiraProjectManifest]: ...


class CreateJiraDataManifestProtocol(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> type[IJiraDataManifest]: ...


def generate_project_manifest(
    manifest_adapter: ManifestAdapter,
    project_data_dict: dict,
    classifications_name_lookup: dict,
    create_jira_project_manifest: CreateJiraProjectManifestProtocol,
    reset_current_tenant: Callable,
) -> type[IJiraProjectManifest]:
    # Need to reset tenancy when spinning up threads
    reset_current_tenant()

    project_key = project_data_dict['key']
    project_id = int(project_data_dict['id'])
    try:
        # FIRST, DO A BASIC TEST TO SEE IF WE HAVE THE PROPER PERMISSIONS
        # TO SEE ANY DATA IN THIS PROJECT
        if not manifest_adapter.test_basic_auth_for_project(project_id=project_id):
            raise ProjectManifestGenerationException(
                f'Authentication Exception Encountered for Project {project_key}!'
            )

        manifest_source = manifest_adapter.manifest_source
        excluded: bool = project_key in manifest_adapter.excluded_project_keys

        # Set the issues count to 0 if we are in a remote manifest
        # and this project is excluded
        issues_count = (
            0
            if manifest_source == ManifestSource.remote and excluded
            else manifest_adapter.get_issues_count_for_project(project_id=project_id)
        )
        version_count = manifest_adapter.get_project_versions_count_for_project(
            project_id=project_id
        )
        last_issue_updated_date = manifest_adapter.get_last_updated_for_project(
            project_id=project_id
        )
        project_classification = manifest_adapter.project_keys_to_classification_type.get(
            project_key
        )

        return create_jira_project_manifest(
            company=manifest_adapter.company_slug,
            data_source=manifest_source,
            project_id=str(project_id),
            project_key=project_key,
            issues_count=issues_count,
            version_count=version_count,
            excluded=excluded,
            pull_from=manifest_adapter.config.pull_from,
            last_issue_updated_date=last_issue_updated_date,
            classification=project_classification,
            classification_str=classifications_name_lookup.get(project_classification),
        )
    except JIRAError as e:
        logger.debug(f'{traceback.format_exc()}')
        raise ProjectManifestGenerationException(e.text)
    except Exception as e:
        logger.debug(f'{traceback.format_exc()}')
        raise ProjectManifestGenerationException(str(e))


def process_global_jira_data(
    manifest_adapter: ManifestAdapter,
    create_jira_data_manifest: CreateJiraDataManifestProtocol,
    reset_current_tenant: Callable,
) -> type[IJiraDataManifest]:
    # Need to reset tenancy when spinning up threads
    reset_current_tenant()

    total_users_count = manifest_adapter.get_users_count()
    total_fields_count = manifest_adapter.get_fields_count()
    total_resolutions_count = manifest_adapter.get_resolutions_count()
    total_issue_types_count = manifest_adapter.get_issue_types_count()
    total_issue_link_types_count = manifest_adapter.get_issue_link_types_count()
    total_priorities_count = manifest_adapter.get_priorities_count()
    total_boards_count = manifest_adapter.get_boards_count()
    project_data_dicts = manifest_adapter.get_project_data_dicts()
    project_versions_count = manifest_adapter.get_project_versions_count()
    issues_count = manifest_adapter.get_issues_count()

    return create_jira_data_manifest(
        company=manifest_adapter.company_slug,
        data_source=manifest_adapter.manifest_source,
        pull_from=manifest_adapter.config.pull_from,
        users_count=total_users_count,
        fields_count=total_fields_count,
        resolutions_count=total_resolutions_count,
        issue_types_count=total_issue_types_count,
        issue_link_types_count=total_issue_link_types_count,
        priorities_count=total_priorities_count,
        projects_count=len(project_data_dicts),
        boards_count=total_boards_count,
        project_versions_count=project_versions_count,
        issues_count=issues_count,
        # The following fields must be filled out after processing
        # all ProjectManifests
        project_manifests=[],
        encountered_errors_for_projects={},
    )
