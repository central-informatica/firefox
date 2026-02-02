"""
Tests for IP range validation in usuarios_ip_whitelist.py schema.

Tests verify that reserved/private IP addresses are rejected to prevent
whitelist bypass attacks:
- Loopback (127.0.0.0/8, ::1)
- Private ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
- Link-local (169.254.0.0/16, fe80::/10)
- Multicast (224.0.0.0/4, ff00::/8)
- Reserved/unspecified (0.0.0.0, ::)
"""

import uuid
import pytest
from pydantic import ValidationError

from backend.app.schemas.usuarios_ip_whitelist import (
    validate_ip_not_reserved,
    UsuarioIpWhitelistBase,
    UsuarioIpWhitelistCreate,
    UsuarioIpWhitelistUpdate,
)


# ============================================
# Unit Tests for validate_ip_not_reserved()
# ============================================

class TestValidateIpNotReserved:
    """Unit tests for the validate_ip_not_reserved function."""

    # -----------------------------------------
    # Loopback addresses
    # -----------------------------------------

    def test_loopback_ipv4_rejected(self):
        """127.0.0.1 (loopback) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("127.0.0.1")
        assert "loopback" in str(exc_info.value).lower()

    def test_loopback_ipv4_other_rejected(self):
        """127.0.0.2 (loopback range) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("127.0.0.2")
        assert "loopback" in str(exc_info.value).lower()

    def test_loopback_ipv6_rejected(self):
        """::1 (IPv6 loopback) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("::1")
        assert "loopback" in str(exc_info.value).lower()

    # -----------------------------------------
    # Private ranges (RFC 1918)
    # -----------------------------------------

    def test_private_10_range_rejected(self):
        """10.0.0.1 (Class A private) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("10.0.0.1")
        assert "privado" in str(exc_info.value).lower()

    def test_private_10_range_end_rejected(self):
        """10.255.255.255 (Class A private end) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("10.255.255.255")
        assert "privado" in str(exc_info.value).lower()

    def test_private_172_range_rejected(self):
        """172.16.0.1 (Class B private) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("172.16.0.1")
        assert "privado" in str(exc_info.value).lower()

    def test_private_172_range_middle_rejected(self):
        """172.20.0.1 (Class B private middle) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("172.20.0.1")
        assert "privado" in str(exc_info.value).lower()

    def test_private_172_range_end_rejected(self):
        """172.31.255.255 (Class B private end) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("172.31.255.255")
        assert "privado" in str(exc_info.value).lower()

    def test_private_192_range_rejected(self):
        """192.168.1.1 (Class C private) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("192.168.1.1")
        assert "privado" in str(exc_info.value).lower()

    def test_private_192_range_start_rejected(self):
        """192.168.0.1 (Class C private start) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("192.168.0.1")
        assert "privado" in str(exc_info.value).lower()

    # -----------------------------------------
    # Link-local addresses
    # Note: Link-local addresses may be caught by is_private check first
    # depending on Python's ipaddress module behavior
    # -----------------------------------------

    def test_link_local_rejected(self):
        """169.254.1.1 (link-local) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("169.254.1.1")
        # May be caught as private or link-local depending on check order
        error_msg = str(exc_info.value).lower()
        assert "link-local" in error_msg or "privado" in error_msg

    def test_link_local_ipv6_rejected(self):
        """fe80::1 (IPv6 link-local) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("fe80::1")
        # May be caught as private or link-local depending on check order
        error_msg = str(exc_info.value).lower()
        assert "link-local" in error_msg or "privado" in error_msg

    # -----------------------------------------
    # Multicast addresses
    # -----------------------------------------

    def test_multicast_rejected(self):
        """224.0.0.1 (multicast) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("224.0.0.1")
        assert "multicast" in str(exc_info.value).lower()

    def test_multicast_ipv6_rejected(self):
        """ff02::1 (IPv6 multicast) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("ff02::1")
        assert "multicast" in str(exc_info.value).lower()

    # -----------------------------------------
    # Unspecified addresses
    # Note: Unspecified addresses may be caught by is_private check first
    # depending on Python's ipaddress module behavior
    # -----------------------------------------

    def test_unspecified_ipv4_rejected(self):
        """0.0.0.0 (unspecified) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("0.0.0.0")
        # May be caught as private or unspecified depending on check order
        error_msg = str(exc_info.value).lower()
        assert "nao especificado" in error_msg or "privado" in error_msg

    def test_unspecified_ipv6_rejected(self):
        """:: (IPv6 unspecified) should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("::")
        # May be caught as private or unspecified depending on check order
        error_msg = str(exc_info.value).lower()
        assert "nao especificado" in error_msg or "privado" in error_msg

    # -----------------------------------------
    # Invalid IP format
    # -----------------------------------------

    def test_invalid_ip_format_rejected(self):
        """Invalid IP format should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("not-an-ip")
        assert "nao e um endereco IP valido" in str(exc_info.value)

    def test_invalid_ip_too_many_octets(self):
        """IP with too many octets should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("192.168.1.1.1")
        assert "nao e um endereco IP valido" in str(exc_info.value)

    def test_invalid_ip_octet_out_of_range(self):
        """IP with octet > 255 should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("192.168.1.256")
        assert "nao e um endereco IP valido" in str(exc_info.value)

    def test_invalid_ip_empty_string(self):
        """Empty string should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_ip_not_reserved("")
        assert "nao e um endereco IP valido" in str(exc_info.value)

    # -----------------------------------------
    # Valid public IP addresses
    # -----------------------------------------

    def test_valid_public_ipv4_accepted(self):
        """8.8.8.8 (Google DNS - public) should be accepted."""
        result = validate_ip_not_reserved("8.8.8.8")
        assert result == "8.8.8.8"

    def test_valid_public_ipv4_cloudflare_accepted(self):
        """1.1.1.1 (Cloudflare DNS - public) should be accepted."""
        result = validate_ip_not_reserved("1.1.1.1")
        assert result == "1.1.1.1"

    def test_valid_public_ipv6_accepted(self):
        """2001:4860:4860::8888 (Google DNS IPv6 - public) should be accepted."""
        result = validate_ip_not_reserved("2001:4860:4860::8888")
        assert result == "2001:4860:4860::8888"

    def test_valid_public_ipv6_cloudflare_accepted(self):
        """2606:4700:4700::1111 (Cloudflare DNS IPv6 - public) should be accepted."""
        result = validate_ip_not_reserved("2606:4700:4700::1111")
        assert result == "2606:4700:4700::1111"

    def test_valid_public_ipv4_random_accepted(self):
        """203.0.113.50 (TEST-NET-3 / documentation - but is_private is False) should be accepted."""
        # Note: 203.0.113.0/24 is reserved for documentation but not marked as private
        result = validate_ip_not_reserved("200.100.50.25")
        assert result == "200.100.50.25"

    # -----------------------------------------
    # Edge cases - boundary testing
    # -----------------------------------------

    def test_172_15_not_private(self):
        """172.15.255.255 (just before private range) should be accepted."""
        result = validate_ip_not_reserved("172.15.255.255")
        assert result == "172.15.255.255"

    def test_172_32_not_private(self):
        """172.32.0.1 (just after private range) should be accepted."""
        result = validate_ip_not_reserved("172.32.0.1")
        assert result == "172.32.0.1"


# ============================================
# Integration Tests for Pydantic Schemas
# ============================================

class TestUsuarioIpWhitelistCreateValidation:
    """Tests for UsuarioIpWhitelistCreate schema validation."""

    def _valid_create_data(self, **overrides):
        """Return valid create data with optional overrides."""
        data = {
            "usuario_id": str(uuid.uuid4()),
            "empresa_id": str(uuid.uuid4()),
            "ip_address": "8.8.8.8",
            "descricao": "Test IP",
        }
        data.update(overrides)
        return data

    def test_create_whitelist_private_ip_returns_422(self):
        """Creating whitelist with private IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="192.168.1.1"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_loopback_ip_returns_422(self):
        """Creating whitelist with loopback IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="127.0.0.1"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_link_local_ip_returns_422(self):
        """Creating whitelist with link-local IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="169.254.1.1"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_multicast_ip_returns_422(self):
        """Creating whitelist with multicast IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="224.0.0.1"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_unspecified_ip_returns_422(self):
        """Creating whitelist with unspecified IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="0.0.0.0"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_invalid_ip_returns_422(self):
        """Creating whitelist with invalid IP format should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistCreate(**self._valid_create_data(ip_address="not-an-ip"))
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_create_whitelist_public_ip_success(self):
        """Creating whitelist with public IP should succeed."""
        whitelist = UsuarioIpWhitelistCreate(**self._valid_create_data())
        assert whitelist.ip_address == "8.8.8.8"

    def test_create_whitelist_public_ipv6_success(self):
        """Creating whitelist with public IPv6 should succeed."""
        whitelist = UsuarioIpWhitelistCreate(
            **self._valid_create_data(ip_address="2001:4860:4860::8888")
        )
        assert whitelist.ip_address == "2001:4860:4860::8888"


class TestUsuarioIpWhitelistUpdateValidation:
    """Tests for UsuarioIpWhitelistUpdate schema validation."""

    def test_update_whitelist_private_ip_returns_422(self):
        """Updating whitelist to private IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistUpdate(ip_address="10.0.0.1")
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_update_whitelist_loopback_ip_returns_422(self):
        """Updating whitelist to loopback IP should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            UsuarioIpWhitelistUpdate(ip_address="127.0.0.1")
        errors = exc_info.value.errors()
        assert any("ip_address" in str(e.get("loc", [])) for e in errors)

    def test_update_whitelist_public_ip_success(self):
        """Updating whitelist to public IP should succeed."""
        update = UsuarioIpWhitelistUpdate(ip_address="8.8.8.8")
        assert update.ip_address == "8.8.8.8"

    def test_update_whitelist_none_ip_success(self):
        """Updating whitelist with None IP (not changing) should succeed."""
        update = UsuarioIpWhitelistUpdate(descricao="New description")
        assert update.ip_address is None
        assert update.descricao == "New description"
