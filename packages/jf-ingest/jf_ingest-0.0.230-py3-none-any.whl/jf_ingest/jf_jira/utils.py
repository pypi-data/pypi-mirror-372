import logging
from typing import Any, Generator, NamedTuple, Optional

import requests

from jf_ingest import logging_helper
from jf_ingest.config import UserMetadata
from jf_ingest.utils import (
    get_jellyfish_api_base_url,
    get_jellyfish_api_token,
    retry_for_status,
)


class JiraFieldIdentifier(NamedTuple):
    """When scrubbing field information using include_fields or exclude_fields
    Jira is not always consistent in how it identifies the fields. From the
    fields API endpoint (downloaders.download_fields) you can reliable use
    the "id" field (something like "customfield_XXXXXXXX"), but when scrubbing
    changelogs on issues (via _filter_changelogs) you sometimes can only use
    the human readable name (like "Your Custom Field"). This Tuple will hold both the
    Jira ID and the human readable name.

    For premade fields in Jira, like "Description", the ID field is typically the same
    as the human readable name but with/without capitalization. Example: 'description' vs 'Description'
    """

    jira_field_id: str  # The Jira ID field. Can be premade (like 'description') or custom (like 'customfield_XXXXXX')
    jira_field_name: str  # The human readable field name. Can be premade (like 'Description') or custom like 'Your Custom Field'

    def matches_changelog_item(self, changelog_item: dict):
        if 'fieldId' in changelog_item:
            return self.jira_field_id == changelog_item['fieldId']
        elif 'field' in changelog_item:
            changelog_field_name: str = changelog_item['field']
            jira_field_name = self.jira_field_name
            # NOTE: When Agent customers want to include fields that are specific to Jira
            # (think description, status, assignee), it generally doesn't use capitalization
            # for the name value of the field. To get around this, normalize everything to
            # lowercase when dealing with. Since these all come from Jira, I am not worried
            # about capitalization collisions being an issue. This is only relevant for Jira
            # Server instances, where the fieldId is generally not included
            if field_type := changelog_item.get('fieldtype', ''):
                if field_type == 'jira':
                    changelog_field_name = changelog_field_name.lower()
                    jira_field_name = jira_field_name.lower()
            return jira_field_name == changelog_field_name
        else:
            logging_helper.log_standard_error(
                level=logging.WARNING,
                error_code=3082,
                msg_args=[changelog_item.keys()],
            )
            return False


def get_jellyfish_jira_issues_count(
    jellyfish_api_base_url: Optional[str] = None, jellyfish_api_token: Optional[str] = None
) -> int:
    """Helper function for getting the total number of issues that exist in Jellyfish

    Args:
        jellyfish_api_base_url (Optional[str]): Used as the base API to get data from jellyfish. If not provided, we will attempt to read it from the global variable.
        jellyfish_api_token (Optional[str]): Used for authenticating against Jellyfish. If not provided, we will attempt to read it from the global variable.

    Returns:
        int: The total number of Jellyfish Jira Issues that exist in this customers instance
    """
    if not jellyfish_api_base_url:
        jellyfish_api_base_url = get_jellyfish_api_base_url()
    if not jellyfish_api_token:
        jellyfish_api_token = get_jellyfish_api_token()

    base_url = jellyfish_api_base_url
    headers = {"Jellyfish-API-Token": jellyfish_api_token}

    r = retry_for_status(
        requests.get,
        f"{base_url}/endpoints/jira/issues/count",
        headers=headers,
    )
    r.raise_for_status()
    json_resp: dict = r.json()
    num_issues: int = json_resp.get('total_issues_in_jellyfish', 0)

    return num_issues


def expand_and_normalize_jira_fields(
    fields_from_jira: list[dict], field_names_or_ids: list[str]
) -> list[JiraFieldIdentifier]:
    """Expands/Translates whatever the Agent config has for include or exclude fields, and
    transforms them to be a list of JiraFieldIdentifier objects which contain both the name and the ID.

    For example, if the exclude_list has the following fields: ['Sprint'],
    which represents the human readable name for each field, and the Jira Fields API endpoint
    returns us {'id': 'customfield_0001', 'name': 'Sprint'}, this function would transform the
    exclude_list to be {jira_field_name: 'Sprint', jira_field_name: 'customfield_0001'}.
    If the exclude_list was ['customfield_0001'] would provide the same result
    NOTE: DO NOT EVERY MESS WITH CAPITALIZATION, AS THE JIRA API IS CASE SENSITIVE


    Args:
        fields_from_jira (list[dict]): The raw JSON fields returned from the field API endpoint
        field_names_or_ids (list[str]): A list of field IDs or field Names to expand and/or normalize

    Returns:
        : A list of JiraFieldIdentifier objects that contain both the field ID and the field Name
    """
    field_id_to_name_lookup = {field['id']: field['name'] for field in fields_from_jira}
    field_name_to_id_lookup = {field['name']: field['id'] for field in fields_from_jira}
    jira_field_identifiers = set()
    for provided_field in field_names_or_ids:
        field_name = field_id_to_name_lookup.get(provided_field)
        field_id = field_name_to_id_lookup.get(provided_field)
        if field_name:
            jira_field_identifiers.add(
                JiraFieldIdentifier(jira_field_id=provided_field, jira_field_name=field_name)
            )
        if field_id:
            jira_field_identifiers.add(
                JiraFieldIdentifier(jira_field_id=field_id, jira_field_name=provided_field)
            )
        # If we don't have a field_name or a field_id, then we might have a provided field
        # that exists on an issue but is not included in the returned data from the /field
        # endpoint. We've seen this for at least one client when it comes to the "parent" field
        if not (field_name or field_id):
            jira_field_identifiers.add(
                JiraFieldIdentifier(jira_field_id=provided_field, jira_field_name=provided_field)
            )

    return list(jira_field_identifiers)


def get_user_key(gdpr_active: bool) -> str:
    """Helper function for getting the name of the key that maps
    to the unique identify for a user in the Jira Instance. This
    value can be either "key" or "accountId". "accountId" is used
    by Jira Cloud, and "key" is used by Jira Server

    Args:
        gdpr_active (bool): Switch to determine what type of Jira
        Instance we're in

    Returns:
        str: Either "key" or "accountId", depending on the
        instance type
    """

    # Choose the key name based on the GDPR status
    if gdpr_active:
        return "accountId"
    else:
        return "key"


def get_user_key_from_user(user_dict: dict, gdpr_active: bool = False, **kwargs) -> str:
    """Helper function used for getting unique set of users

    Args:
        user_dict (dict): Raw User dict from JIRA API
        gdpr_active (bool, optional): Switches what key to grab, depending on if we are server or cloud. Defaults to False.

    Raises:
        KeyError: _description_

    Returns:
        _type_: Jira User Unique key (accountId or Key, depending on gdpr_active)
    """
    key_name = get_user_key(gdpr_active=gdpr_active)

    # Return a default value if one is provided, otherwise raise a KeyError
    try:
        if "default" in kwargs:
            default_value = kwargs["default"]
            kn: str = user_dict.get(key_name, default_value)
        else:
            kn = user_dict[key_name]

        return kn
    except KeyError as e:
        raise KeyError(
            f'Error extracting user data from Jira data. GDPR set to "{gdpr_active}" and expecting key name: "{key_name}" in user_dict. This is most likely an issue with how the GDPR flag is set on Jira instance. If this is a Jira Agent configuration, the agent config.yml settings may also be wrong.'
        ) from e


def get_unique_users_from_issue(issue: dict, gdpr_active: bool) -> set[UserMetadata]:
    """Extracts all the user keys (either key or accountId, depending on if it's server or cloud)
    from a jira issue. This is useful for getting all the users that are associated with an issue
    and seeing if we need to download additional users

    Args:
        issue (dict): A raw issue dictionary from the Jira API

    Returns;
        set[str]: A set of user keys (either key or accountId) that are associated with the issue
    """
    user_key = get_user_key(gdpr_active=gdpr_active)
    users: set[UserMetadata] = set()

    def _recurse_on_issue_data_for_user_key(dict_or_list: Any):
        if isinstance(dict_or_list, dict):
            if 'self' in dict_or_list and '/rest/api/2/user' in dict_or_list['self']:
                if user_key not in dict_or_list:
                    return
                users.add(
                    UserMetadata(
                        self_url=dict_or_list['self'],
                        user_key=dict_or_list[user_key],
                        email=dict_or_list.get('email'),
                        name=dict_or_list.get('name'),
                        active=dict_or_list.get('active'),
                    )
                )
                return
            for key, value in dict_or_list.items():
                if isinstance(value, (dict, list)):
                    _recurse_on_issue_data_for_user_key(value)
        if isinstance(dict_or_list, list):
            for value in dict_or_list:
                if isinstance(value, (dict, list)):
                    _recurse_on_issue_data_for_user_key(value)

    _recurse_on_issue_data_for_user_key(issue)
    return users
