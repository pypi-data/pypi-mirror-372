from typing import List, Optional
from pydantic import BaseModel

from nf_jira.entities.pagamento import Pagamento

from .dados_basicos_miro import DadosBasicosMiro
from .referencia_pedido import ReferenciaPedido
from .detalhe import Detalhe
from .sintese_miro import SinteseMiro
from .dados_nfe import DadosNfe

class Miro(BaseModel):
    dados_basicos: DadosBasicosMiro
    pagamento: Pagamento
    referencia_pedido: Optional[ReferenciaPedido] = None
    detalhe: Detalhe
    sintese: List[SinteseMiro]
    dados_nfe: DadosNfe

