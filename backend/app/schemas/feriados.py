from pydantic import BaseModel, constr
from datetime import date, datetime
from typing import Optional
from uuid import UUID


class FeriadoBase(BaseModel):
    data: date
    nome: constr(min_length=2, max_length=120)
    recorrente: bool = False
    empresa_id: UUID


class FeriadoCreate(FeriadoBase):
    pass


class FeriadoUpdate(BaseModel):
    data: Optional[date] = None
    nome: Optional[str] = None
    recorrente: Optional[bool] = None


class FeriadoOut(FeriadoBase):
    feriado_id: UUID
    criado_em: datetime

    class Config:
        orm_mode = True
