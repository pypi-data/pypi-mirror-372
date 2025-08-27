from pydantic import BaseModel

from typing import List

from .sintese_itens import SinteseItens
from .anexo import Anexo
from .jira_info import JiraInfo

class NotaPedido(BaseModel):
    montante: float=0.0
    valor_bruto: float=0.0
    valor_liquido: float=0.0
    juros: float=0    
    tipo: str
    org_compras: str
    grp_compradores: str
    empresa: str
    cod_fornecedor: str
    centro_custo_destinatario: str
    centro_destinatario: str
    sintese_itens: List[SinteseItens]
    anexo: List[Anexo]

    def __init__(self, **data):
        super().__init__(**data)
        self.handleAllocationValue()
        self.handleCentro()

    def handleCentro(self):
        for sintese_item in self.sintese_itens:
            sintese_item.item.centro = self.centro_destinatario

    def handleAllocationValue(self):
        if self.valor_liquido:
            self.handle_montante()
            for sintese_item in self.sintese_itens:
                percentage = sintese_item.item.percentage
                valor_liquido_total = self.valor_liquido
                sintese_item.item.valor_liquido = valor_liquido_total * (percentage / 100)
                sintese_item.item.handle_montante()
        pass

    def handle_montante(self):
        self.valor_bruto = self.montante
        if self.valor_liquido:
            self.montante = self.valor_liquido