from pydantic import BaseModel

from .item import Item

class SinteseItens(BaseModel):
    categoria_cc: str
    quantidade: int
    cod_material: str
    item: Item