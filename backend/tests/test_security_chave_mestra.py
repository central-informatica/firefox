"""
Tests for PBKDF2 key derivation in chave_mestra.py.

Tests verify:
- Key generation produces 32 bytes (256-bit)
- Same password + salt produces same key (deterministic)
- Different passwords produce different keys
- Salt file is created on first run
- Existing salt is reused on subsequent calls
- PBKDF2_ITERATIONS constant is set correctly
"""

import os
import tempfile
import shutil
from unittest.mock import patch

import pytest

from backend.app.utils.chave_mestra import (
    gerar_chave,
    SALT_FILE,
    PBKDF2_ITERATIONS,
)


# ============================================
# Unit Tests for Key Generation
# ============================================

class TestGerarChave:
    """Unit tests for the gerar_chave function."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory for tests."""
        temp_dir = tempfile.mkdtemp()
        original_salt_file = SALT_FILE

        # Create the storage subdirectory
        storage_path = os.path.join(temp_dir, "storage")
        os.makedirs(storage_path, exist_ok=True)

        yield temp_dir, os.path.join(storage_path, "salt.bin")

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_gerar_chave_returns_32_bytes(self, temp_storage_dir):
        """Key generation should return exactly 32 bytes (256-bit key)."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            with patch("backend.app.utils.chave_mestra.os.makedirs"):
                # Manually create the directory
                os.makedirs(os.path.dirname(salt_path), exist_ok=True)

                key = gerar_chave("test-password")

        assert isinstance(key, bytes)
        assert len(key) == 32  # 256 bits = 32 bytes

    def test_gerar_chave_deterministic(self, temp_storage_dir):
        """Same password + salt should produce same key."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            # Manually create the directory
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            # Generate key twice with same password
            key1 = gerar_chave("same-password")
            key2 = gerar_chave("same-password")

        assert key1 == key2

    def test_gerar_chave_different_passwords(self, temp_storage_dir):
        """Different passwords should produce different keys."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            # Manually create the directory
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key1 = gerar_chave("password1")
            key2 = gerar_chave("password2")

        assert key1 != key2

    def test_gerar_chave_creates_salt_file(self, temp_storage_dir):
        """Salt file should be created on first run."""
        temp_dir, salt_path = temp_storage_dir

        # Ensure salt file doesn't exist
        if os.path.exists(salt_path):
            os.remove(salt_path)

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            # Manually create the directory
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("test-password")

        # Salt file should now exist
        assert os.path.exists(salt_path)

        # Salt should be 16 bytes
        with open(salt_path, "rb") as f:
            salt = f.read()
        assert len(salt) == 16

    def test_gerar_chave_uses_existing_salt(self, temp_storage_dir):
        """Existing salt should be reused on subsequent calls."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            # Manually create the directory
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            # First call creates salt
            key1 = gerar_chave("test-password")

            # Read the salt
            with open(salt_path, "rb") as f:
                original_salt = f.read()

            # Second call should use same salt
            key2 = gerar_chave("test-password")

            # Read salt again
            with open(salt_path, "rb") as f:
                second_salt = f.read()

        # Salt should be unchanged
        assert original_salt == second_salt

        # Keys should be the same
        assert key1 == key2

    def test_gerar_chave_with_custom_password(self, temp_storage_dir):
        """Custom password should work correctly."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("my-custom-master-key-123!")

        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_gerar_chave_with_empty_password(self, temp_storage_dir):
        """Empty password should still produce a valid key."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("")

        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_gerar_chave_with_unicode_password(self, temp_storage_dir):
        """Unicode password should work correctly."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("senha-com-acentos-\u00e9\u00e0\u00f5")

        assert isinstance(key, bytes)
        assert len(key) == 32

    def test_gerar_chave_with_long_password(self, temp_storage_dir):
        """Very long password should work correctly."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            long_password = "a" * 10000  # 10,000 character password
            key = gerar_chave(long_password)

        assert isinstance(key, bytes)
        assert len(key) == 32


# ============================================
# Tests for PBKDF2 Constants
# ============================================

class TestPBKDF2Constants:
    """Tests for PBKDF2 configuration constants."""

    def test_pbkdf2_iterations_constant(self):
        """PBKDF2_ITERATIONS should be set to 600000 per OWASP 2024 guidelines."""
        assert PBKDF2_ITERATIONS == 600000

    def test_pbkdf2_iterations_minimum(self):
        """PBKDF2_ITERATIONS should be at least 600000."""
        # NIST SP 800-132 recommends at least 10,000
        # OWASP 2024 recommends 600,000+ for PBKDF2-SHA256
        assert PBKDF2_ITERATIONS >= 600000

    def test_salt_file_path(self):
        """SALT_FILE should point to storage/salt.bin."""
        assert SALT_FILE == "storage/salt.bin"


# ============================================
# Security Tests
# ============================================

class TestKeySecurityProperties:
    """Tests for security properties of the key derivation."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory for tests."""
        temp_dir = tempfile.mkdtemp()
        storage_path = os.path.join(temp_dir, "storage")
        os.makedirs(storage_path, exist_ok=True)
        yield temp_dir, os.path.join(storage_path, "salt.bin")
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_different_salts_produce_different_keys(self):
        """Different salts with same password should produce different keys."""
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes

        password = "same-password"
        salt1 = os.urandom(16)
        salt2 = os.urandom(16)

        kdf1 = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt1,
            iterations=PBKDF2_ITERATIONS,
        )
        key1 = kdf1.derive(password.encode())

        kdf2 = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt2,
            iterations=PBKDF2_ITERATIONS,
        )
        key2 = kdf2.derive(password.encode())

        assert key1 != key2

    def test_key_length_is_256_bits(self, temp_storage_dir):
        """Generated key should be exactly 256 bits (32 bytes)."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("test")

        # 256 bits = 32 bytes = 64 hex characters
        assert len(key) == 32
        assert len(key.hex()) == 64

    def test_salt_is_16_bytes(self, temp_storage_dir):
        """Generated salt should be 16 bytes (128 bits)."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            # Generate key to create salt file
            gerar_chave("test")

            # Read and verify salt
            with open(salt_path, "rb") as f:
                salt = f.read()

        assert len(salt) == 16  # 128 bits


# ============================================
# Edge Cases
# ============================================

class TestEdgeCases:
    """Edge case tests for key generation."""

    @pytest.fixture
    def temp_storage_dir(self):
        """Create a temporary storage directory for tests."""
        temp_dir = tempfile.mkdtemp()
        storage_path = os.path.join(temp_dir, "storage")
        os.makedirs(storage_path, exist_ok=True)
        yield temp_dir, os.path.join(storage_path, "salt.bin")
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_key_not_predictable(self, temp_storage_dir):
        """Key should not be easily predictable."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            key = gerar_chave("password")

        # Key should not be all zeros or all ones
        assert key != b"\x00" * 32
        assert key != b"\xff" * 32

        # Key should have reasonable entropy (not all same byte)
        unique_bytes = len(set(key))
        assert unique_bytes > 1  # At minimum, should have variety

    def test_default_password_used(self, temp_storage_dir):
        """Default password should be used when none specified."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            # Call with default parameter
            key_default = gerar_chave()

            # Call with explicit default value
            key_explicit = gerar_chave("senha-mestra")

        assert key_default == key_explicit

    def test_special_characters_in_password(self, temp_storage_dir):
        """Password with special characters should work."""
        temp_dir, salt_path = temp_storage_dir

        with patch("backend.app.utils.chave_mestra.SALT_FILE", salt_path):
            os.makedirs(os.path.dirname(salt_path), exist_ok=True)

            special_passwords = [
                "pass with spaces",
                "pass\twith\ttabs",
                "pass\nwith\nnewlines",
                "pass!@#$%^&*()",
                "pass<>[]{}|\\",
            ]

            for password in special_passwords:
                key = gerar_chave(password)
                assert isinstance(key, bytes)
                assert len(key) == 32
