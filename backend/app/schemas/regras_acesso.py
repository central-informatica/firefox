from uuid import UUID

from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from backend.app.enums.tipo_dia import TipoDiaEnum


class RegraAcessoBase(BaseModel):
    empresa_id: UUID
    grupo_id: UUID
    tipo_dia: TipoDiaEnum
    dias_especificos: Optional[List[int]] = None
    horarios: List[Dict]   # ex: [{"inicio": "08:00", "fim": "18:00"}]
    bloquear_em_feriado: Optional[bool] = False

    @validator("dias_especificos", always=True)
    def validar_dias(cls, v, values):
        """dias_especificos é obrigatório quando tipo_dia = 'especificos'"""
        tipo = values.get("tipo_dia")
        if tipo == TipoDiaEnum.especificos and not v:
            raise ValueError("dias_especificos é obrigatório quando tipo_dia = 'especificos'")
        return v

    @validator("horarios")
    def validar_horarios(cls, v):
        """verifica se é uma lista de objetos {'inicio','fim'}"""
        if not v or not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")
        for item in v:
            if not isinstance(item, dict):
                raise ValueError("Cada item de horarios deve ser um objeto JSON")
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")
        return v


class RegraAcessoCreate(RegraAcessoBase):
    """Modelo usado no POST /regras-acesso"""
    pass


class RegraAcessoUpdate(BaseModel):
    tipo_dia: Optional[TipoDiaEnum] = None
    dias_especificos: Optional[List[int]] = None
    horarios: Optional[List[Dict]] = None
    bloquear_em_feriado: Optional[bool] = None

    @validator("horarios")
    def validar_horarios_update(cls, v):
        if v is None:
            return v
        if not isinstance(v, list):
            raise ValueError("horarios deve ser uma lista")
        for item in v:
            if "inicio" not in item or "fim" not in item:
                raise ValueError("Cada horário deve conter 'inicio' e 'fim'")
        return v


class RegraAcessoOut(RegraAcessoBase):
    regra_id: UUID
    criado_em: datetime

    class Config:
        orm_mode = True
