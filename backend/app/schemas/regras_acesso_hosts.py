from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from backend.app.enums.tipo_dia import TipoDiaEnum


class RegraAcessoHostBase(BaseModel):
    grupo_id: str
    tipo_dia: TipoDiaEnum
    dias_especificos: Optional[List[int]] = None
    horarios: List[Dict]
    urls: Optional[str] = None
    bloquear_em_feriado: Optional[bool] = False

    @validator("dias_especificos", always=True)
    def validar_dias(cls, v, values):
        tipo = values.get("tipo_dia")
        if tipo == TipoDiaEnum.especificos and not v:
            raise ValueError("dias_especificos é obrigatório quando tipo_dia = 'especificos'")
        return v

    @validator("horarios")
    def validar_horarios(cls, v):
        if not v or not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")
        for item in v:
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")
        return v


class RegraAcessoHostCreate(RegraAcessoHostBase):
    pass


class RegraAcessoHostUpdate(BaseModel):
    tipo_dia: Optional[TipoDiaEnum] = None
    dias_especificos: Optional[List[int]] = None
    horarios: Optional[List[Dict]] = None
    urls: Optional[str] = None
    bloquear_em_feriado: Optional[bool] = None


class RegraAcessoHostOut(RegraAcessoHostBase):
    regra_id: str
    criado_em: datetime

    class Config:
        orm_mode = True
