from pydantic import BaseModel

from .chave_acesso import ChaveAcesso
from .nfe_sefaz import NfeSefaz

class DadosNfe(BaseModel):
    chave_acesso_sefaz : ChaveAcesso
    nfe_sefaz : NfeSefaz