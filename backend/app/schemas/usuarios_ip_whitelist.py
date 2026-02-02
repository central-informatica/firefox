"""
Pydantic schemas for UsuariosIpWhitelist.

Validates IP whitelist entries for user access control per empresa.
"""

import ipaddress
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, field_serializer


def validate_ip_not_reserved(ip_str: str) -> str:
    """
    Validate that an IP address is not a reserved/private range.

    Rejects:
    - Loopback (127.0.0.0/8, ::1)
    - Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    - Link-local (169.254.0.0/16, fe80::/10)
    - Multicast (224.0.0.0/4, ff00::/8)
    - Reserved/unspecified (0.0.0.0, ::)

    These ranges could be used to bypass IP whitelist controls.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        raise ValueError(f"'{ip_str}' nao e um endereco IP valido")

    if ip.is_loopback:
        raise ValueError(
            f"'{ip_str}' e um endereco de loopback e nao pode ser usado na whitelist"
        )

    if ip.is_private:
        raise ValueError(
            f"'{ip_str}' e um endereco IP privado e nao pode ser usado na whitelist. "
            "Use apenas enderecos IP publicos para garantir a seguranca."
        )

    if ip.is_link_local:
        raise ValueError(
            f"'{ip_str}' e um endereco link-local e nao pode ser usado na whitelist"
        )

    if ip.is_multicast:
        raise ValueError(
            f"'{ip_str}' e um endereco multicast e nao pode ser usado na whitelist"
        )

    if ip.is_reserved:
        raise ValueError(
            f"'{ip_str}' e um endereco reservado e nao pode ser usado na whitelist"
        )

    if ip.is_unspecified:
        raise ValueError(
            f"'{ip_str}' e um endereco nao especificado (0.0.0.0 ou ::) e nao pode ser usado na whitelist"
        )

    return ip_str


class UsuarioIpWhitelistBase(BaseModel):
    """Base schema with common fields."""

    usuario_id: str
    empresa_id: str
    ip_address: str
    descricao: Optional[str] = None

    @field_validator("ip_address")
    @classmethod
    def validar_ip(cls, v: str) -> str:
        """
        Validate that ip_address is a valid public IPv4 or IPv6 address.

        Rejects reserved/private ranges to prevent whitelist bypass attacks.
        """
        return validate_ip_not_reserved(v)


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
        """
        Validate IP if provided.

        Rejects reserved/private ranges to prevent whitelist bypass attacks.
        """
        if v is not None:
            return validate_ip_not_reserved(v)
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
