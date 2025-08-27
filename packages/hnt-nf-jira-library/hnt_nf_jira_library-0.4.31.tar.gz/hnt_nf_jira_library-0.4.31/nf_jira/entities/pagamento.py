from pydantic import BaseModel

class Pagamento(BaseModel):
    data_basica: str
    cond_pgto: str