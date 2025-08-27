from pydantic import BaseModel
from typing import Optional

class ItensFatura(BaseModel):
    cta_razao: str
    montante: float
    valor_bruto: Optional[float]=0.0
    valor_liquido: Optional[float]=0.0
    percentage: float
    loc_negocios: str
    atribuicao: Optional[str]
    texto: str
    centro_custo: str

    def __init__(self, **data):
        super().__init__(**data)
        self.montante = round(self.montante, 2)

    def handle_montante(self):
        self.valor_bruto = self.montante
        if self.valor_liquido:
            self.montante = self.valor_liquido
