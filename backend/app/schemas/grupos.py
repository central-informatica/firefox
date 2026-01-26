"""Pydantic schemas for Grupos."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class GrupoCreate(BaseModel):
    """Schema for creating a grupo."""

    empresa_id: str
    plano_id: str
    nome: str


class GrupoUpdate(BaseModel):
    """Schema for updating a grupo."""

    nome: Optional[str] = None


class GrupoOut(BaseModel):
    """Schema for grupo response."""

    model_config = ConfigDict(from_attributes=True)

    grupo_id: UUID
    empresa_id: UUID
    plano_id: UUID
    nome: str
    criado_em: datetime

    @field_serializer("grupo_id", "empresa_id", "plano_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)


class GrupoCertificadoAdd(BaseModel):
    """Schema for adding certificado to grupo."""

    empresa_id: str
    certificado_id: str


class GrupoCertificadoRemove(BaseModel):
    """Schema for removing certificado from grupo."""

    empresa_id: str
    certificado_id: str


class GrupoUsuarioAdd(BaseModel):
    """Schema for adding usuario to grupo."""

    empresa_id: str
    usuario_id: str
