from .helper import JsonHelper, JiraFieldsHelper
from ..constants import *

class IssueFields:

    def get_fields_by_form_and_jira(self, form_jira_keys, form_fields, jira_fields, debug=False):

        
        fields = self._generate_fields(form_jira_keys)
        fields_from_jira_keys = self._get_issue_fields_data_from_jira_keys(form_jira_keys, jira_fields)
        JiraFieldsHelper().remove_null_fields(fields_from_jira_keys)
        JiraFieldsHelper().remove_null_fields(form_fields)

        self._append_jira_fields(fields_from_jira_keys, fields)
        self._append_form_fields(form_fields, fields)

        JsonHelper().save_json(f'Fields_From_Keys_{ISSUE_KEY}',fields) if debug else None
        return fields

    def _get_issue_fields_data_from_jira_keys(self, form_jira_keys, jira_fields):

        jira_fields_from_keys = {}

        for field_key in form_jira_keys:

            jira_key = form_jira_keys[field_key]
    
            if jira_key is not None:
                field_value = jira_fields.get(jira_key)
                if field_value is not None and 'value' in field_value:
                    field_value = field_value['value']
            else:
                field_value = None

            jira_fields_from_keys[field_key] = field_value if field_value else None

        return jira_fields_from_keys
    
    def _append_jira_fields(self, jira_fields_from_keys, fields):

        for jira_field in jira_fields_from_keys:
            fields[jira_field] = jira_fields_from_keys[jira_field]  if jira_fields_from_keys[jira_field] is not None else fields[jira_field]

        pass

    def _append_form_fields(self, form_fields, fields):

        for form_field in form_fields:
            fields[form_field] = form_fields[form_field] if form_fields[form_field] is not None else fields[form_field]

        pass

    def _generate_fields(self, fields_keys):

        fields = {}
        for key in fields_keys:
            fields[key] = None

        return fields