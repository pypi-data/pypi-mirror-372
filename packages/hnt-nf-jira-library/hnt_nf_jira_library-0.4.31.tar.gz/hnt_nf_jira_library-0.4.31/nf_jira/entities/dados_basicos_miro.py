from typing import Optional
from pydantic import BaseModel

class DadosBasicosMiro(BaseModel):
    data_da_fatura: str
    referencia: Optional[str] = None
    montante: float=0.0
    valor_bruto: float=0.0
    valor_liquido: float=0.0
    texto: str

    def __init__(self, **data):
        super().__init__(**data)
        self._handle_montante()
    
    def _handle_montante(self):
        if self.valor_liquido:
            self.valor_bruto = self.montante
            self.montante = self.valor_liquido