from typing import Optional
from pydantic import BaseModel

class NfeSefaz(BaseModel):
    numero_log: Optional[str] = None
    data_procmto: Optional[str] = None
    hora_procmto: Optional[str] = None