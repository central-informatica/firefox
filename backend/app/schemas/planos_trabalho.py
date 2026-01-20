from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional


class PlanoTrabalhoBase(BaseModel):
    nome: constr(min_length=2, max_length=100)
    descricao: Optional[str] = None


class PlanoTrabalhoCreate(PlanoTrabalhoBase):
    pass


class PlanoTrabalhoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None


class PlanoTrabalhoOut(PlanoTrabalhoBase):
    plano_id: int
    criado_em: datetime

    class Config:
        orm_mode = True
