import json
from os import getcwd, makedirs, path
import requests
from ..constants import *
from .helper import JsonHelper, JiraFieldsHelper
import logging
logger = logging.getLogger(__name__)

class IssueJira:
    def get_issue_jql(self, jql):
        logger.info(f"Enter execute get_issue_jql jql:{jql}")
        issues = []
        start_at = 0
        PAGE_SIZE = 50
        while True:
            fields=["key", NRO_DOCUMENTO_FATURA_SAP_FIELD, CODIGO_BARRAS_FIELD]
            params=f"jql={jql}&fields={','.join(fields)}&startAt={start_at}&maxResults={PAGE_SIZE}"
            url=f"{API_ISSUE_URL}/search?{params}"
            response = requests.get(
                url,
                headers=API_HEADERS,
                auth=JIRA_AUTH,
            )
            response.raise_for_status()
            data = response.json()
            issues.extend(data.get("issues", []))
            if len(issues) >= data.get("total", 0):
                break
            start_at += PAGE_SIZE
        result = [{ 
            "key": issue['key'],
            "nro_documento_fatura": issue['fields'].get(NRO_DOCUMENTO_FATURA_SAP_FIELD),
            "codigo_barras": issue['fields'].get(CODIGO_BARRAS_FIELD)  # Example for another custom field
            } for issue in issues]
        logger.info(f"Enter execute get_issue_jql result len:{len(result)}")
        return result
    def get_issue(self, issue_key, debug=False):
        issue = self._get_issue_data(issue_key)
        JsonHelper().save_json(f'Issue_{issue_key}',issue) if debug else None

        return issue
    
    def get_issue_fields_data(self, issue_key, debug=False):

        issue = self._get_issue_data(issue_key)
        issue_fields = self._get_issue_fields(issue)
        
        JsonHelper().save_json(f'Issue_Fields_{issue_key}',issue_fields) if debug else None
        issue_fields_min = JiraFieldsHelper().remove_null_fields(issue_fields)

        return issue_fields_min

    def _get_issue_data(self, issue_key):
        try:
            request = requests.get(
                f"{API_ISSUE_URL}/issue/{issue_key}",
                # f"{API_ISSUE_URL}/{CLOUD_ID}/issue/{issue_key}",
                headers=API_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            data = request.json()

            return data
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber dados da issue:\n{e}")
        
    def _get_issue_fields(self, issue):

        jira_fields = issue.get('fields')
        return jira_fields
    

        
class AttachmentJira:

    def get_attachment(self, issue, is_pdf=False):

        self._check_issue_attachment(issue)
        attachments_ids = self._get_attachment_id(issue)
        attachment = {}
        for attachment_key in attachments_ids:
            attachments_from_issue = self._get_attachments_from_issue(attachment_key)
            if attachments_from_issue:
                attachment = attachments_from_issue

        
        return attachment
        
    def _check_issue_attachment(self, issue):
        if issue.get("fields")["attachment"] is None:
            raise Exception("Could not find attachment")
        
    def _get_attachments_from_issue(self, attachment_key):
        try:
            request = requests.get(
                f"{API_ISSUE_URL}/attachment/content/{attachment_key}",
                headers=API_ATTACHMENT_HEADERS,
                auth=JIRA_AUTH,
            )
            request.raise_for_status()
            check_pdf = self._check_pdf_attachment_request(request)
            check_img = self._check_img_attachment_request(request)
            attachment_data = json.loads(request.text.replace('\n','')) if not check_pdf and not check_img else None

            return attachment_data

        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao receber anexo Jira:\n{e}")
        
    def _check_img_attachment_request(self, request):
        return True if "image/gif" in request.headers.get("Content-Type", "") else False
       
    def _check_pdf_attachment_request(self, request):
        return True if "application/pdf" in request.headers.get("Content-Type", "") else False
        
    def _check_pdf_attachment_list(self, attachment):
        if 'mimeType' in attachment:
            return True if "application/pdf" in attachment['mimeType'] else False
        return False
    
    def _get_attachment_id(self, issue):
        attachment_ids = []

        for attachment in issue.get("fields")["attachment"]:
            attachment_ids.append(attachment["id"])

        return attachment_ids
    
    def download_attachments(self, issue_data):

        attachment_list = self._get_attachment_list(issue_data)
        donwload_list = []

        for attachment in attachment_list:
            attachment_params = self._get_download_attachment_params(attachment)
            check_pdf = self._check_pdf_attachment_list(attachment)
            if check_pdf:
                donwload_path = self._download_attachment(attachment_params, DEST_PATH) if check_pdf else None
                download_path_without_filename, filename = os.path.split(donwload_path)
                donwload_list.append({
                    "path": download_path_without_filename,
                    "filename": filename
                })

        return donwload_list

    def _get_attachment_list(self, issue_data):

        attachment_list = []

        for attachment in issue_data.get("fields")["attachment"]:
            attachment_list.append(attachment)

        return attachment_list

    def _get_download_attachment_params(self, attachment):
        attachment_params = {
            "filename": attachment['filename'],
            'content': attachment['content']
        }
        return attachment_params
    
    def _download_attachment(self, attachment_params, dest_path):
        try:
            res = requests.get(
                attachment_params['content'],
                timeout=10,
                auth=JIRA_AUTH,
                allow_redirects=True)
            res.raise_for_status()
            if not path.exists(dest_path):
                makedirs(dest_path)
            dest_path_filename = path.join(dest_path, attachment_params['filename'])
            open(dest_path_filename, 'wb').write(res.content)
            return dest_path_filename
        
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao baixar anexo Jira:\n{e}")
    
class TransitionJira:

    def post_transition(self, transition_id, issue_key):

        self._post_transition(transition_id, issue_key)
        pass

    def _post_transition(self, transition_id, issue_key):

        payload = json.dumps(
            {
                "transition": {"id": transition_id},
                "update": {"comment": []},
            }
        )
        try:
            res = requests.post(
                f"{API_ISSUE_URL}/issue/{issue_key}/transitions",
                auth=JIRA_AUTH,
                headers=API_HEADERS,
                data=payload,
            )
            res.raise_for_status()
            pass
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao alterar transição da issue:\n{e}")    
        
class CommentJira:

    def add_comment(self, issue_key, comment):

        self._add_comment(issue_key, comment)
        pass

    def _add_comment(self, issue_key, message):

        try:
            payload = json.dumps(
                {
                    "body": {
                        "content": [
                            {
                                "content": [
                                    {
                                        "type": "emoji",
                                        "attrs": {
                                            "shortName": ":robot:",
                                            "id": "1f916",
                                            "text": "🤖",
                                        },
                                    },
                                    {"text": f" {message}", "type": "text"},
                                ],
                                "type": "paragraph",
                            }
                        ],
                        "type": "doc",
                        "version": 1,
                    }
                }
            )
            res = requests.post(
                f"{API_ISSUE_URL}/issue/{issue_key}/comment",
                auth=JIRA_AUTH,
                headers=API_HEADERS,
                data=payload,
            )
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Erro ao enviar comentario para issue:\n{e}")
        