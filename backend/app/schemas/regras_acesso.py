from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from backend.app.enums.tipo_dia import TipoDiaEnum


class RegraAcessoBase(BaseModel):
    empresa_id: int
    grupo_id: int
    tipo_dia: TipoDiaEnum   
    dias_especificos: Optional[List[int]] = None
    horarios: List[Dict]


class RegraAcessoCreate(RegraAcessoBase):
    pass


class RegraAcessoUpdate(BaseModel):
    tipo_dia: Optional[TipoDiaEnum] = None
    dias_especificos: Optional[List[int]] = None
    horarios: Optional[List[Dict]] = None


class RegraAcessoOut(RegraAcessoBase):
    regra_id: int
    criado_em: datetime

    class Config:
        orm_mode = True
