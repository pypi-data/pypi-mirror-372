from typing import Optional
from pydantic import BaseModel

class ChaveAcesso(BaseModel):
    tp_emissao: Optional[str] = None
    numero_aleatorio: Optional[str] = None
    dig_verif: Optional[str] = None