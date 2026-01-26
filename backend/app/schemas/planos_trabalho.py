from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, constr, field_serializer


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
    model_config = ConfigDict(from_attributes=True)

    plano_id: UUID
    empresa_id: UUID
    criado_em: datetime

    @field_serializer("plano_id", "empresa_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)


class PlanoTrabalhoPage(BaseModel):
    data: List[PlanoTrabalhoOut]
    total: int
    