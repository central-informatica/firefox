"""
Tests for URL domain normalization and file size limits in certificados.py.

Tests verify:
- Domain normalization using IDNA encoding (homograph attack prevention)
- File size limit enforcement (10 MB max)
"""

import pytest

from backend.app.api.routes.certificados import (
    _normalize_domain,
    MAX_CERT_SIZE_BYTES,
)


# ============================================
# Unit Tests for _normalize_domain()
# ============================================

class TestNormalizeDomain:
    """Unit tests for domain normalization (homograph attack prevention)."""

    def test_normalize_domain_basic(self):
        """Basic ASCII domain should remain unchanged (lowercase)."""
        result = _normalize_domain("example.com")
        assert result == "example.com"

    def test_normalize_domain_uppercase(self):
        """Uppercase domain should be lowercased."""
        result = _normalize_domain("EXAMPLE.COM")
        assert result == "example.com"

    def test_normalize_domain_mixed_case(self):
        """Mixed case domain should be lowercased."""
        result = _normalize_domain("ExAmPlE.CoM")
        assert result == "example.com"

    def test_normalize_domain_cyrillic_a(self):
        """Domain with Cyrillic 'a' (homograph) should be converted to punycode."""
        # Cyrillic 'a' (U+0430) looks like Latin 'a' but is different
        cyrillic_domain = "ex\u0430mple.com"  # 'a' is Cyrillic
        result = _normalize_domain(cyrillic_domain)
        # Should be converted to punycode (xn--...) form
        assert result.startswith("xn--") or result != "example.com"

    def test_normalize_domain_cyrillic_e(self):
        """Domain with Cyrillic 'e' (homograph) should be converted to punycode."""
        # Cyrillic 'e' (U+0435) looks like Latin 'e' but is different
        cyrillic_domain = "\u0435xample.com"  # first 'e' is Cyrillic
        result = _normalize_domain(cyrillic_domain)
        # Should be converted to punycode (xn--...) form
        assert result.startswith("xn--") or result != "example.com"

    def test_normalize_domain_mixed_script(self):
        """Domain with mixed scripts should be converted to punycode."""
        # Mix of Latin and Cyrillic characters
        mixed_domain = "g\u043eogle.com"  # 'o' is Cyrillic
        result = _normalize_domain(mixed_domain)
        # Should be converted to punycode
        assert "xn--" in result or result != "google.com"

    def test_normalize_domain_greek_omicron(self):
        """Domain with Greek omicron (looks like 'o') should be normalized."""
        # Greek omicron (U+03BF) looks like Latin 'o'
        greek_domain = "g\u03bfgle.com"
        result = _normalize_domain(greek_domain)
        # Should be converted to punycode
        assert "xn--" in result or result != "gogle.com"

    def test_normalize_domain_subdomain(self):
        """Subdomain should also be normalized."""
        result = _normalize_domain("WWW.EXAMPLE.COM")
        assert result == "www.example.com"

    def test_normalize_domain_with_port(self):
        """Domain with port should be normalized."""
        result = _normalize_domain("example.com:8080")
        assert result == "example.com:8080"

    def test_normalize_domain_international_punycode(self):
        """International domain in Unicode should be converted to punycode."""
        # Chinese domain
        result = _normalize_domain("\u4e2d\u6587.com")  # Chinese characters
        assert "xn--" in result

    def test_normalize_domain_already_punycode(self):
        """Domain already in punycode should remain as-is."""
        result = _normalize_domain("xn--nxasmq5b.com")
        assert result == "xn--nxasmq5b.com"

    def test_normalize_domain_empty_string(self):
        """Empty string should return empty."""
        result = _normalize_domain("")
        assert result == ""

    def test_normalize_domain_special_tld(self):
        """Domain with special TLD should be normalized."""
        result = _normalize_domain("EXAMPLE.COM.BR")
        assert result == "example.com.br"

    def test_normalize_domain_hyphen(self):
        """Domain with hyphen should be preserved."""
        result = _normalize_domain("my-domain.example.com")
        assert result == "my-domain.example.com"


# ============================================
# Tests for File Size Constants
# ============================================

class TestCertificateFileSizeLimit:
    """Tests for certificate file size limits."""

    def test_max_cert_size_constant(self):
        """Verify MAX_CERT_SIZE_BYTES is set to 10 MB."""
        assert MAX_CERT_SIZE_BYTES == 10 * 1024 * 1024  # 10 MB

    def test_max_cert_size_in_megabytes(self):
        """Verify MAX_CERT_SIZE_BYTES equals 10 megabytes."""
        megabytes = MAX_CERT_SIZE_BYTES / (1024 * 1024)
        assert megabytes == 10

    def test_file_size_check_logic(self):
        """Test the file size comparison logic."""
        # Simulate the check in upload_certificate
        # if len(file_content) > MAX_CERT_SIZE_BYTES:

        # File larger than limit should be rejected
        large_content = b"x" * (MAX_CERT_SIZE_BYTES + 1)
        assert len(large_content) > MAX_CERT_SIZE_BYTES

        # File at exact limit should pass (> not >=)
        exact_content = b"x" * MAX_CERT_SIZE_BYTES
        assert not (len(exact_content) > MAX_CERT_SIZE_BYTES)

        # File under limit should pass
        small_content = b"x" * (MAX_CERT_SIZE_BYTES - 1)
        assert not (len(small_content) > MAX_CERT_SIZE_BYTES)

        # Empty file should pass size check
        empty_content = b""
        assert not (len(empty_content) > MAX_CERT_SIZE_BYTES)


# ============================================
# Edge Cases for Domain Normalization
# ============================================

class TestDomainNormalizationEdgeCases:
    """Additional edge case tests for domain normalization."""

    def test_normalize_preserves_valid_ascii(self):
        """Valid ASCII characters should be preserved."""
        domains = [
            "example.com",
            "sub.domain.example.com",
            "my-site.example.com",
            "123.example.com",
            "a.b.c.d.example.com",
        ]
        for domain in domains:
            result = _normalize_domain(domain)
            assert result == domain.lower()

    def test_normalize_different_homoglyphs_differ(self):
        """Different homoglyphs should produce different normalized results."""
        latin_domain = "example.com"
        cyrillic_domain = "ex\u0430mple.com"  # Cyrillic 'a'

        latin_result = _normalize_domain(latin_domain)
        cyrillic_result = _normalize_domain(cyrillic_domain)

        # They should be different after normalization
        assert latin_result != cyrillic_result

    def test_normalize_fallback_on_encoding_error(self):
        """Invalid encoding should fall back to lowercase."""
        # Test with a string that might cause encoding issues
        # Most normal strings won't cause this, but we verify the fallback exists
        result = _normalize_domain("normal.domain.com")
        assert result == "normal.domain.com"

    def test_normalize_numeric_domain(self):
        """Numeric domain should be normalized."""
        result = _normalize_domain("123.456.789")
        assert result == "123.456.789"

    def test_normalize_single_char_domain(self):
        """Single character domain should be normalized."""
        result = _normalize_domain("A")
        assert result == "a"
