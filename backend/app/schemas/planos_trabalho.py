from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr


class PlanoTrabalhoBase(BaseModel):
    nome: constr(min_length=2, max_length=100)
    descricao: Optional[str] = None


class PlanoTrabalhoCreate(BaseModel):
    nome: str
    descricao: str | None = None 

class PlanoTrabalhoUpdate(BaseModel):
    nome: Optional[constr(min_length=2, max_length=100)] = None
    descricao: Optional[str] = None


class PlanoTrabalhoOut(PlanoTrabalhoBase):
    plano_id: int
    empresa_id: int
    criado_em: datetime

    class Config:
        from_attributes = True  # pydantic v2


class PlanoTrabalhoPage(BaseModel):
    data: List[PlanoTrabalhoOut]
    total: int
    