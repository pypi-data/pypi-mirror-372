from pydantic import BaseModel

class JiraInfo(BaseModel):
    issue_id: str
    form_id: str