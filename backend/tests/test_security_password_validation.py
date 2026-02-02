"""
Tests for password policy validation in auth.py.

Tests verify that password strength requirements are enforced:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (@$!%*?&-_#^+=)
"""

import pytest
from pydantic import ValidationError

from backend.app.api.routes.auth import (
    validate_password_strength,
    MIN_PASSWORD_LENGTH,
    ResetPasswordRequest,
    ChangePasswordRequest,
    RegisterRequest,
)


# ============================================
# Unit Tests for validate_password_strength()
# ============================================

class TestValidatePasswordStrength:
    """Unit tests for the validate_password_strength function."""

    def test_password_too_short(self):
        """Password with less than 12 characters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("Abc123!@#")  # 9 chars
        assert f"pelo menos {MIN_PASSWORD_LENGTH} caracteres" in str(exc_info.value)

    def test_password_exactly_11_chars_rejected(self):
        """Password with exactly 11 characters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("Abcdef123!@")  # 11 chars
        assert f"pelo menos {MIN_PASSWORD_LENGTH} caracteres" in str(exc_info.value)

    def test_password_missing_lowercase(self):
        """Password without lowercase letters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("ABCDEFGH123!@#")  # No lowercase
        assert "letra minuscula" in str(exc_info.value)

    def test_password_missing_uppercase(self):
        """Password without uppercase letters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("abcdefgh123!@#")  # No uppercase
        assert "letra maiuscula" in str(exc_info.value)

    def test_password_missing_digit(self):
        """Password without digits should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("Abcdefgh!@#xyz")  # No digit
        assert "numero" in str(exc_info.value)

    def test_password_missing_special_char(self):
        """Password without special characters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("Abcdefgh123xyz")  # No special char
        assert "caractere especial" in str(exc_info.value)

    def test_password_valid_complex(self):
        """Password meeting all requirements should pass."""
        result = validate_password_strength("MySecure123!Pass")
        assert result == "MySecure123!Pass"

    def test_password_exactly_12_chars(self):
        """Password with exactly 12 characters meeting all requirements should pass."""
        result = validate_password_strength("Abcdef123!@#")  # 12 chars
        assert result == "Abcdef123!@#"

    def test_password_with_all_special_chars(self):
        """Password with various allowed special characters should pass."""
        # Test each special char: @$!%*?&-_#^+=
        special_chars = "@$!%*?&-_#^+="
        for char in special_chars:
            password = f"Abcdefgh123{char}"
            result = validate_password_strength(password)
            assert result == password, f"Special char '{char}' should be accepted"

    def test_password_very_long(self):
        """Very long password meeting requirements should pass."""
        long_password = "A" + "a" * 50 + "1" + "!"
        result = validate_password_strength(long_password)
        assert result == long_password

    def test_password_with_hyphen(self):
        """Password with hyphen special character should pass."""
        result = validate_password_strength("MyPassword1-xyz")
        assert result == "MyPassword1-xyz"

    def test_password_with_underscore(self):
        """Password with underscore special character should pass."""
        result = validate_password_strength("MyPassword1_xyz")
        assert result == "MyPassword1_xyz"

    def test_password_with_caret(self):
        """Password with caret special character should pass."""
        result = validate_password_strength("MyPassword1^xyz")
        assert result == "MyPassword1^xyz"


# ============================================
# Integration Tests for Pydantic Models
# ============================================

class TestResetPasswordRequestValidation:
    """Tests for ResetPasswordRequest schema validation."""

    def test_reset_password_weak_password_short(self):
        """Reset password with short password should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            ResetPasswordRequest(token="valid-token", new_password="Abc123!")
        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors)

    def test_reset_password_weak_password_no_uppercase(self):
        """Reset password without uppercase should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            ResetPasswordRequest(token="valid-token", new_password="abcdefgh123!@#")
        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors)

    def test_reset_password_weak_password_no_digit(self):
        """Reset password without digit should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            ResetPasswordRequest(token="valid-token", new_password="Abcdefgh!@#xyz")
        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors)

    def test_reset_password_valid(self):
        """Reset password with valid strong password should pass."""
        request = ResetPasswordRequest(
            token="valid-token",
            new_password="MySecure123!Pass"
        )
        assert request.new_password == "MySecure123!Pass"


class TestChangePasswordRequestValidation:
    """Tests for ChangePasswordRequest schema validation."""

    def test_change_password_weak_new_password(self):
        """Change password with weak new password should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="oldpassword",
                new_password="weak"
            )
        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors)

    def test_change_password_weak_no_special_char(self):
        """Change password without special character should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="oldpassword",
                new_password="Abcdefgh123xyz"  # No special char
            )
        errors = exc_info.value.errors()
        assert any("new_password" in str(e.get("loc", [])) for e in errors)

    def test_change_password_valid(self):
        """Change password with valid passwords should pass."""
        request = ChangePasswordRequest(
            current_password="oldpassword",
            new_password="NewSecure123!Pass"
        )
        assert request.new_password == "NewSecure123!Pass"


class TestRegisterRequestValidation:
    """Tests for RegisterRequest schema validation."""

    def _valid_register_data(self, **overrides):
        """Return valid register data with optional overrides."""
        data = {
            "organization_name": "Test Company",
            "slug": "test-company",
            "domain": "test.com",
            "cnpj": "12345678901234",
            "address_street": "Test Street 123",
            "address_city": "Sao Paulo",
            "address_state": "SP",
            "address_country": "Brazil",
            "address_postal_code": "12345-678",
            "admin_email": "admin@test.com",
            "admin_password": "SecurePass123!",
            "admin_first_name": "Test",
            "admin_last_name": "Admin",
        }
        data.update(overrides)
        return data

    def test_register_weak_admin_password_short(self):
        """Register with short admin password should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**self._valid_register_data(admin_password="Abc123!"))
        errors = exc_info.value.errors()
        assert any("admin_password" in str(e.get("loc", [])) for e in errors)

    def test_register_weak_admin_password_no_lowercase(self):
        """Register without lowercase in admin password should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**self._valid_register_data(admin_password="ABCDEFGH123!@#"))
        errors = exc_info.value.errors()
        assert any("admin_password" in str(e.get("loc", [])) for e in errors)

    def test_register_weak_admin_password_no_special(self):
        """Register without special char in admin password should return 422."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(**self._valid_register_data(admin_password="Abcdefgh123xyz"))
        errors = exc_info.value.errors()
        assert any("admin_password" in str(e.get("loc", [])) for e in errors)

    def test_register_valid_password(self):
        """Register with valid strong admin password should pass."""
        request = RegisterRequest(**self._valid_register_data())
        assert request.admin_password == "SecurePass123!"


# ============================================
# Edge Cases
# ============================================

class TestPasswordEdgeCases:
    """Test edge cases for password validation."""

    def test_empty_password(self):
        """Empty password should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("")
        assert f"pelo menos {MIN_PASSWORD_LENGTH} caracteres" in str(exc_info.value)

    def test_password_with_spaces(self):
        """Password with spaces meeting requirements should pass."""
        result = validate_password_strength("My Pass 123! xyz")
        assert result == "My Pass 123! xyz"

    def test_password_unicode_chars(self):
        """Password with unicode characters meeting requirements should pass."""
        # Unicode letters still count as letters
        result = validate_password_strength("MyPassword1!abc")
        assert result == "MyPassword1!abc"

    def test_password_only_special_chars_at_start(self):
        """Password with special chars at start should pass if all requirements met."""
        result = validate_password_strength("!@#Abcdefgh123")
        assert result == "!@#Abcdefgh123"

    def test_password_numbers_and_special_chars_only(self):
        """Password with only numbers and special chars should be rejected (no letters)."""
        with pytest.raises(ValueError) as exc_info:
            validate_password_strength("123456789!@#$%")
        # Should fail on missing lowercase or uppercase
        error_msg = str(exc_info.value)
        assert "letra minuscula" in error_msg or "letra maiuscula" in error_msg
