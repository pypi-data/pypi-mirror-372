
import json
from jf_ingest.jf_jira.utils import JiraFieldIdentifier, expand_and_normalize_jira_fields
from tests.jf_jira.utils import get_fixture_file_data

def get_field_data() -> list[dict]:
    return [
    {
        "id": "statuscategorychangedate",
        "key": "statuscategorychangedate",
        "name": "Status Category Changed",
        "custom": False,
        "orderable": False,
        "navigable": True,
        "searchable": True,
        "clauseNames": [
            "statusCategoryChangedDate"
        ],
        "schema": {
            "type": "datetime",
            "system": "statuscategorychangedate"
        }
    },
    {
        "id": "parent",
        "key": "parent",
        "name": "Parent",
        "custom": False,
        "orderable": False,
        "navigable": True,
        "searchable": False,
        "clauseNames": [
            "parent"
        ]
    },
    {
        "id": "customfield_10070",
        "key": "customfield_10070",
        "name": "Satisfaction date",
        "untranslatedName": "Satisfaction date",
        "custom": True,
        "orderable": True,
        "navigable": True,
        "searchable": True,
        "clauseNames": [
            "cf[10070]",
            "Satisfaction date"
        ],
        "schema": {
            "type": "datetime",
            "custom": "com.atlassian.servicedesk:sd-request-feedback-date",
            "customId": 10070
        }
    },
    {
        "id": "customfield_10071",
        "key": "customfield_10071",
        "name": "Reporters",
        "untranslatedName": "Reporters",
        "custom": True,
        "orderable": True,
        "navigable": True,
        "searchable": True,
        "clauseNames": [
            "Reporters",
            "Reporters[User Picker (multiple users)]",
            "cf[10071]"
        ],
        "schema": {
            "type": "array",
            "items": "user",
            "custom": "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker",
            "customId": 10071
        }
    }
]

def test_expand_and_normalize_jira_fields_smoke_test():
    raw_fields = get_field_data()
    
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=[])
    assert jira_field_identifiers == []
    

def test_expand_and_normalize_jira_fields_with_id():
    raw_fields = get_field_data()
    
    fields_to_expand = ['customfield_10070']
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=fields_to_expand)
    assert len(jira_field_identifiers) == 1
    assert jira_field_identifiers[0].jira_field_id == 'customfield_10070'
    assert jira_field_identifiers[0].jira_field_name == 'Satisfaction date'

def test_expand_and_normalize_jira_fields_with_name():
    raw_fields = get_field_data()
    
    fields_to_expand = ['Satisfaction date']
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=fields_to_expand)
    assert len(jira_field_identifiers) == 1
    assert jira_field_identifiers[0].jira_field_id == 'customfield_10070'
    assert jira_field_identifiers[0].jira_field_name == 'Satisfaction date'

def test_expand_and_normalize_jira_fields_with_redundant_data():
    raw_fields = get_field_data()
    
    fields_to_expand = ['customfield_10070', 'Satisfaction date']
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=fields_to_expand)
    assert len(jira_field_identifiers) == 1
    assert jira_field_identifiers[0].jira_field_id == 'customfield_10070'
    assert jira_field_identifiers[0].jira_field_name == 'Satisfaction date'
    
def test_expand_and_normalize_jira_fields_with_all_ids():
    raw_fields = sorted(get_field_data(), key=lambda _dict: _dict['id'])
    ids = [f['id'] for f in raw_fields]
    names = [f['name'] for f in raw_fields]
    assert len(ids) == len(names)
    
    
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=ids)
    
    assert len(jira_field_identifiers) == len(ids)
    for id, name, jira_field_identifier in zip(ids, names, sorted(jira_field_identifiers, key=lambda jfi: jfi.jira_field_id)):
        print(id, name, jira_field_identifier)
        assert jira_field_identifier.jira_field_id == id
        assert jira_field_identifier.jira_field_name == name

def test_expand_and_normalize_jira_fields_with_all_names():
    raw_fields = sorted(get_field_data(), key=lambda _dict: _dict['id'])
    ids = [f['id'] for f in raw_fields]
    names = [f['name'] for f in raw_fields]
    assert len(ids) == len(names)
    
    
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=names)
    
    assert len(jira_field_identifiers) == len(names)
    for id, name, jira_field_identifier in zip(ids, names, sorted(jira_field_identifiers, key=lambda jfi: jfi.jira_field_id)):
        print(id, name, jira_field_identifier)
        assert jira_field_identifier.jira_field_id == id
        assert jira_field_identifier.jira_field_name == name

def test_expand_and_normalize_jira_fields_with_missing_field():
    """This test specifically tests if you include a field that doesn't exist
    in the "raw_fields" data (returned by the field API endpoint), we will still
    create a JiraFieldIdentifier for the include field. In that use case, we will
    set the provided include_field as both the ID and the Name.
    This is a specific fix for some weird versions of Jira Server, where the
    parent field is not returned by the Jira Fields API endpoint, but we do still
    expect to see the parent field on the JiraIssue objects
    """
    # Set up raw fields WITH NO parent data
    raw_fields = [
        {
            "id": "customfield_10070",
            "key": "customfield_10070",
            "name": "Satisfaction date",
            "untranslatedName": "Satisfaction date",
            "custom": True,
            "orderable": True,
            "navigable": True,
            "searchable": True,
            "clauseNames": [
                "cf[10070]",
                "Satisfaction date"
            ],
            "schema": {
                "type": "datetime",
                "custom": "com.atlassian.servicedesk:sd-request-feedback-date",
                "customId": 10070
            }
        },
        {
            "id": "customfield_10071",
            "key": "customfield_10071",
            "name": "Reporters",
            "untranslatedName": "Reporters",
            "custom": True,
            "orderable": True,
            "navigable": True,
            "searchable": True,
            "clauseNames": [
                "Reporters",
                "Reporters[User Picker (multiple users)]",
                "cf[10071]"
            ],
            "schema": {
                "type": "array",
                "items": "user",
                "custom": "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker",
                "customId": 10071
            }
        }
    ]
    raw_fields = sorted(raw_fields, key=lambda _dict: _dict['id'])
    
    jira_field_identifiers = expand_and_normalize_jira_fields(fields_from_jira=raw_fields, field_names_or_ids=['parent', 'id', 'customfield_10070'])
    assert len(jira_field_identifiers) == 3
    jira_field_identifiers_ids = [jfi.jira_field_id for jfi in jira_field_identifiers]
    jira_field_identifiers_names = [jfi.jira_field_name for jfi in jira_field_identifiers]
    
    # Verify IDs
    assert 'parent' in jira_field_identifiers_ids
    assert 'id' in jira_field_identifiers_ids
    assert 'customfield_10070' in jira_field_identifiers_ids
    assert 'customfield_10071' not in jira_field_identifiers_ids
    
    # Verify Names
    assert 'parent' in jira_field_identifiers_names
    assert 'id' in jira_field_identifiers_names
    assert 'Satisfaction date' in jira_field_identifiers_names
    assert 'Reporters' not in jira_field_identifiers_names
    
        
def test_matches_changelog_item_base():
    field_name = 'FieldName'
    field_id = 'customfield_xxxxx'
    changelog_item = {
        'field': field_name,
        'fieldId': field_id
    }
    
    jfi = JiraFieldIdentifier(jira_field_id=field_id, jira_field_name=field_name)
    assert jfi.matches_changelog_item(changelog_item)
    
    changelog_item_no_id = {
        'field': field_name
    }
    
    assert jfi.matches_changelog_item(changelog_item_no_id)
    
    changelog_item_no_name = {
        'fieldId': field_id
    }
    assert jfi.matches_changelog_item(changelog_item_no_name)
    
    changelog_item_reversed = {
        'fieldId': field_name,
        'field': field_id,
    }
    assert not jfi.matches_changelog_item(changelog_item_reversed)
    
    changelog_item_reversed = {
        'fieldId': 'nomatch',
        'field': 'nomatch',
    }
    assert not jfi.matches_changelog_item(changelog_item_reversed)
    

        
def test_matches_changelog_capitalization_test():
    field_name = 'status'
    field_id = 'status'
    
    jfi = JiraFieldIdentifier(jira_field_id=field_id, jira_field_name=field_name)
    assert jfi.matches_changelog_item({
        'field': field_name
    })
    
    # This should not match, because this test should be case sensitive
    assert not jfi.matches_changelog_item({
        'field': 'Status'
    })
    
    # This should match because Jira type fields are not case sensitive
    assert jfi.matches_changelog_item({
        'field': 'Status',
        'fieldtype': 'jira'
    })
    
    
    # This should not match because non-Jira type fields are case sensitive
    assert not jfi.matches_changelog_item({
        'field': 'Status',
        'fieldtype': 'custom'
    })
