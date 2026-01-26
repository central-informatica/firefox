"""Pydantic schemas for GruposCertificadosUrls."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class GrupoCertUrlCreate(BaseModel):
    """Schema for creating a grupo-certificado URL association."""

    global_urls_id: str


class GrupoCertUrlOut(BaseModel):
    """Schema for grupo-certificado URL response."""

    model_config = ConfigDict(from_attributes=True)

    grupo_cert_url_id: UUID
    grupo_cert_id: UUID
    global_urls_id: UUID
    empresa_id: UUID

    @field_serializer("grupo_cert_url_id", "grupo_cert_id", "global_urls_id", "empresa_id")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
