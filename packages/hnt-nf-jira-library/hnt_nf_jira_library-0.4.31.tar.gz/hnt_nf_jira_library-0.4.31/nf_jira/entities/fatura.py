from typing import List
from pydantic import BaseModel

from nf_jira.entities.anexo import Anexo
from nf_jira.entities.constants import CONTA_RAZAO_JUROS_CM

from .dados_basicos_fatura import DadosBasicosFatura
from .pagamento import Pagamento
from .jira_info import JiraInfo

class Fatura(BaseModel):
    dados_basicos: DadosBasicosFatura
    pagamento: Pagamento
    anexo: List[Anexo]

    def __init__(self, **data):
        super().__init__(**data)
        self.adjust_rating_round_itens()
        self.handleAllocationValue()
        self.dados_basicos.handle_reference()

    def handleAllocationValue(self):
        if self.dados_basicos.valor_liquido and  self.dados_basicos.juros:
            self.dados_basicos.handle_montante()
            for item in self.dados_basicos.itens:
                percentage = item.percentage
                valor_liquido_total = self.dados_basicos.valor_liquido
                item.valor_liquido = valor_liquido_total * (percentage / 100)
                item.handle_montante()
            # Iten adicional de Juros
            self.dados_basicos.itens.append({
                "cta_razao": CONTA_RAZAO_JUROS_CM, #Conta Contabil SAP
                "montante":  self.dados_basicos.juros,
                "valor_bruto": 0.0,
                "valor_liquido": 0.0,
                "percentage" : 100.0,
                "loc_negocios": self.dados_basicos.centro_destinatario,
                "atribuicao": self.dados_basicos.itens[0].atribuicao,
                "texto": self.dados_basicos.texto,
                "centro_custo":  self.dados_basicos.centro_custo_destinatario
        })
        pass

    def adjust_rating_round_itens(self):
        if len(self.dados_basicos.itens) == 1: return
        current_total = sum(item.montante for item in self.dados_basicos.itens)
        difference = self.dados_basicos.montante - current_total
        if len(self.dados_basicos.itens) > 1 and difference != 0:
            self.dados_basicos.itens[-1].montante += difference