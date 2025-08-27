from pydantic import BaseModel
from typing import List, Optional

from nf_jira.entities.constants import MAX_LEN_SAP_REFERENCE

from .itens_fatura import ItensFatura

class DadosBasicosFatura(BaseModel):
    cod_fornecedor: str
    data_fatura: str
    referencia: Optional[str] = None
    montante: float
    valor_bruto: Optional[float]=0.0
    valor_liquido: Optional[float]
    juros: float=0    
    bus_pl_sec_cd: str
    texto: str
    centro_custo_destinatario: str
    centro_destinatario: str
    itens: Optional[List[ItensFatura]] = None

    def handle_montante(self):
        self.valor_bruto = self.montante

    def handle_reference(self):
        if self.referencia is not None and len(self.referencia) > MAX_LEN_SAP_REFERENCE:
            self.referencia = self.referencia[:MAX_LEN_SAP_REFERENCE]
