"""
Pydantic schemas for UsuariosIpWhitelist.

Validates IP whitelist entries for user access control per empresa.
"""

import ipaddress
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, field_serializer


class UsuarioIpWhitelistBase(BaseModel):
    """Base schema with common fields."""

    usuario_id: str
    empresa_id: str
    ip_address: str
    descricao: Optional[str] = None

    @field_validator("ip_address")
    @classmethod
    def validar_ip(cls, v: str) -> str:
        """Validate that ip_address is a valid IPv4 or IPv6 address."""
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError(f"'{v}' nao e um endereco IP valido")
        return v


class UsuarioIpWhitelistCreate(UsuarioIpWhitelistBase):
    """Schema for creating a new whitelist entry."""

    pass


class UsuarioIpWhitelistUpdate(BaseModel):
    """Schema for updating a whitelist entry (all fields optional)."""

    ip_address: Optional[str] = None
    descricao: Optional[str] = None

    @field_validator("ip_address")
    @classmethod
    def validar_ip(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP if provided."""
        if v is not None:
            try:
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError(f"'{v}' nao e um endereco IP valido")
        return v


class UsuarioIpWhitelistOut(BaseModel):
    """Schema for whitelist entry response."""

    model_config = ConfigDict(from_attributes=True)

    whitelist_id: UUID
    usuario_id: UUID
    empresa_id: UUID
    ip_address: str
    descricao: Optional[str] = None
    criado_em: datetime
    criado_por: UUID

    @field_serializer("whitelist_id", "usuario_id", "empresa_id", "criado_por")
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)
