from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional
from uuid import UUID


class GrupoCertBase(BaseModel):
    grupo_id: str


class GrupoCertCreate(BaseModel):
    grupo_id: str
    certificado_id: str
    empresa_id: str


class GrupoCertUpdate(BaseModel):
    grupo_id: Optional[str] = None


class GrupoCertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    grupo_cert_id: UUID
    grupo_id: UUID
    certificado_id: UUID
    empresa_id: UUID

    @field_serializer("grupo_cert_id", "grupo_id", "certificado_id", "empresa_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
