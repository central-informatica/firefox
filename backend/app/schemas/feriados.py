from pydantic import BaseModel, ConfigDict, constr
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

    model_config = ConfigDict(from_attributes=True)


class FeriadosReplicar(BaseModel):
    """Schema para replicar feriados para outras empresas."""
    feriado_ids: list[UUID]
    empresa_ids_destino: list[UUID]


class FeriadosImportarPadroes(BaseModel):
    """Schema para importar feriados padrões nacionais."""
    empresa_id: UUID
    ano: Optional[int] = None  # Se None, usa o ano atual
