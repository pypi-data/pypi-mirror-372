from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    centro_desc: str
    centro: Optional[str]=None
    centro_custo: str
    cod_imposto: str
    montante: float=0.0
    valor_bruto: float=0.0
    valor_liquido: Optional[float]=0.0
    percentage: float

    def handle_montante(self):
        self.valor_bruto = self.montante
        if self.valor_liquido:
            self.montante = self.valor_liquido