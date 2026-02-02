"""
Tests for time format and day range validation in regras_acesso.py schema.

Tests verify that:
- Time format is HH:MM (00:00 to 23:59)
- Time range is valid (inicio < fim)
- Day range is 1-7 (ISO week day format: 1=Monday, 7=Sunday)
- dias_especificos is required when tipo_dia = 'especificos'
- Duplicate days are deduplicated and sorted
"""

import uuid
import pytest
from datetime import time
from pydantic import ValidationError

from backend.app.schemas.regras_acesso import (
    _parse_time,
    _validate_time_range,
    VALID_DAY_MIN,
    VALID_DAY_MAX,
    TIME_PATTERN,
    RegraAcessoBase,
    RegraAcessoCreate,
    RegraAcessoUpdate,
)
from backend.app.enums.tipo_dia import TipoDiaEnum


# ============================================
# Unit Tests for _parse_time()
# ============================================

class TestParseTime:
    """Unit tests for the _parse_time function."""

    def test_invalid_time_format_25_hours(self):
        """Time with 25 hours should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("25:00")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_60_minutes(self):
        """Time with 60 minutes should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("12:60")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_no_colon(self):
        """Time without colon should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("1200")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_single_digit_hour(self):
        """Time with single digit hour should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("9:00")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_single_digit_minute(self):
        """Time with single digit minute should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("09:5")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_letters(self):
        """Time with letters should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("ab:cd")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_empty(self):
        """Empty time should be rejected."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_invalid_time_format_24_hours(self):
        """Time with 24 hours should be rejected (max is 23)."""
        with pytest.raises(ValueError) as exc_info:
            _parse_time("24:00")
        assert "nao esta no formato HH:MM valido" in str(exc_info.value)

    def test_valid_time_format_midnight(self):
        """00:00 (midnight) should pass."""
        result = _parse_time("00:00")
        assert result == time(0, 0)

    def test_valid_time_format_end_of_day(self):
        """23:59 (end of day) should pass."""
        result = _parse_time("23:59")
        assert result == time(23, 59)

    def test_valid_time_format_noon(self):
        """12:00 (noon) should pass."""
        result = _parse_time("12:00")
        assert result == time(12, 0)

    def test_valid_time_format_morning(self):
        """08:30 (morning) should pass."""
        result = _parse_time("08:30")
        assert result == time(8, 30)

    def test_valid_time_format_evening(self):
        """18:45 (evening) should pass."""
        result = _parse_time("18:45")
        assert result == time(18, 45)


# ============================================
# Unit Tests for _validate_time_range()
# ============================================

class TestValidateTimeRange:
    """Unit tests for the _validate_time_range function."""

    def test_start_after_end_rejected(self):
        """Start time after end time should be rejected (18:00-08:00)."""
        with pytest.raises(ValueError) as exc_info:
            _validate_time_range("18:00", "08:00")
        assert "anterior ao horario de fim" in str(exc_info.value)

    def test_start_equals_end_rejected(self):
        """Start time equals end time should be rejected (12:00-12:00)."""
        with pytest.raises(ValueError) as exc_info:
            _validate_time_range("12:00", "12:00")
        assert "anterior ao horario de fim" in str(exc_info.value)

    def test_valid_time_range(self):
        """Valid time range (08:00-18:00) should pass."""
        # Should not raise
        _validate_time_range("08:00", "18:00")

    def test_valid_time_range_narrow(self):
        """Narrow valid time range (12:00-12:01) should pass."""
        _validate_time_range("12:00", "12:01")

    def test_valid_time_range_full_day(self):
        """Full day range (00:00-23:59) should pass."""
        _validate_time_range("00:00", "23:59")


# ============================================
# Unit Tests for Day Validation
# ============================================

class TestDayValidation:
    """Tests for dias_especificos validation."""

    def _valid_regra_data(self, **overrides):
        """Return valid regra data with optional overrides."""
        data = {
            "empresa_id": uuid.uuid4(),
            "grupo_id": uuid.uuid4(),
            "tipo_dia": TipoDiaEnum.corridos,
            "horarios": [{"inicio": "08:00", "fim": "18:00"}],
        }
        data.update(overrides)
        return data

    def test_day_zero_rejected(self):
        """Day 0 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                tipo_dia=TipoDiaEnum.especificos,
                dias_especificos=[0, 1, 2]
            ))
        errors = exc_info.value.errors()
        assert any("dias_especificos" in str(e.get("loc", [])) for e in errors)

    def test_day_eight_rejected(self):
        """Day 8 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                tipo_dia=TipoDiaEnum.especificos,
                dias_especificos=[1, 8]
            ))
        errors = exc_info.value.errors()
        assert any("dias_especificos" in str(e.get("loc", [])) for e in errors)

    def test_negative_day_rejected(self):
        """Negative day should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                tipo_dia=TipoDiaEnum.especificos,
                dias_especificos=[-1, 1, 2]
            ))
        errors = exc_info.value.errors()
        assert any("dias_especificos" in str(e.get("loc", [])) for e in errors)

    def test_valid_day_monday(self):
        """Day 1 (Monday) should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[1]
        ))
        assert 1 in regra.dias_especificos

    def test_valid_day_sunday(self):
        """Day 7 (Sunday) should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[7]
        ))
        assert 7 in regra.dias_especificos

    def test_valid_all_weekdays(self):
        """All valid weekdays [1,2,3,4,5,6,7] should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[1, 2, 3, 4, 5, 6, 7]
        ))
        assert regra.dias_especificos == [1, 2, 3, 4, 5, 6, 7]

    def test_duplicate_days_deduplicated(self):
        """Duplicate days should be deduplicated and sorted."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[3, 1, 3, 2, 1]
        ))
        assert regra.dias_especificos == [1, 2, 3]

    def test_days_sorted(self):
        """Days should be sorted after validation."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[7, 5, 3, 1]
        ))
        assert regra.dias_especificos == [1, 3, 5, 7]


# ============================================
# Cross-Field Validation Tests
# ============================================

class TestCrossFieldValidation:
    """Tests for cross-field validation in RegraAcesso schemas."""

    def _valid_regra_data(self, **overrides):
        """Return valid regra data with optional overrides."""
        data = {
            "empresa_id": uuid.uuid4(),
            "grupo_id": uuid.uuid4(),
            "tipo_dia": TipoDiaEnum.corridos,
            "horarios": [{"inicio": "08:00", "fim": "18:00"}],
        }
        data.update(overrides)
        return data

    def test_especificos_without_dias_rejected(self):
        """tipo_dia='especificos' without dias_especificos should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                tipo_dia=TipoDiaEnum.especificos,
                dias_especificos=None
            ))
        assert "dias_especificos" in str(exc_info.value).lower()

    def test_especificos_with_empty_dias_rejected(self):
        """tipo_dia='especificos' with empty dias_especificos should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                tipo_dia=TipoDiaEnum.especificos,
                dias_especificos=[]
            ))
        assert "dias_especificos" in str(exc_info.value).lower()

    def test_especificos_with_dias_accepted(self):
        """tipo_dia='especificos' with dias_especificos should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.especificos,
            dias_especificos=[1, 2, 3, 4, 5]
        ))
        assert regra.tipo_dia == TipoDiaEnum.especificos
        assert regra.dias_especificos == [1, 2, 3, 4, 5]

    def test_corridos_without_dias_accepted(self):
        """tipo_dia='corridos' without dias_especificos should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.corridos,
            dias_especificos=None
        ))
        assert regra.tipo_dia == TipoDiaEnum.corridos
        assert regra.dias_especificos is None

    def test_uteis_without_dias_accepted(self):
        """tipo_dia='uteis' without dias_especificos should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            tipo_dia=TipoDiaEnum.uteis,
            dias_especificos=None
        ))
        assert regra.tipo_dia == TipoDiaEnum.uteis
        assert regra.dias_especificos is None


# ============================================
# Horarios Validation Tests
# ============================================

class TestHorariosValidation:
    """Tests for horarios (time windows) validation."""

    def _valid_regra_data(self, **overrides):
        """Return valid regra data with optional overrides."""
        data = {
            "empresa_id": uuid.uuid4(),
            "grupo_id": uuid.uuid4(),
            "tipo_dia": TipoDiaEnum.corridos,
            "horarios": [{"inicio": "08:00", "fim": "18:00"}],
        }
        data.update(overrides)
        return data

    def test_horarios_invalid_start_time_25_hours(self):
        """Invalid start time (25 hours) should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"inicio": "25:00", "fim": "18:00"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_invalid_end_time_60_minutes(self):
        """Invalid end time (60 minutes) should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"inicio": "08:00", "fim": "18:60"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_start_after_end(self):
        """Start time after end time should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"inicio": "18:00", "fim": "08:00"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_start_equals_end(self):
        """Start time equals end time should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"inicio": "12:00", "fim": "12:00"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_missing_inicio(self):
        """Missing 'inicio' should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"fim": "18:00"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_missing_fim(self):
        """Missing 'fim' should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[{"inicio": "08:00"}]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_empty_list(self):
        """Empty horarios list should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoCreate(**self._valid_regra_data(
                horarios=[]
            ))
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_horarios_valid_single(self):
        """Valid single horario should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            horarios=[{"inicio": "08:00", "fim": "18:00"}]
        ))
        assert len(regra.horarios) == 1

    def test_horarios_valid_multiple(self):
        """Valid multiple horarios should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            horarios=[
                {"inicio": "08:00", "fim": "12:00"},
                {"inicio": "14:00", "fim": "18:00"},
            ]
        ))
        assert len(regra.horarios) == 2

    def test_horarios_midnight_to_end(self):
        """Horario from midnight to end of day should pass."""
        regra = RegraAcessoCreate(**self._valid_regra_data(
            horarios=[{"inicio": "00:00", "fim": "23:59"}]
        ))
        assert regra.horarios[0]["inicio"] == "00:00"
        assert regra.horarios[0]["fim"] == "23:59"


# ============================================
# RegraAcessoUpdate Validation Tests
# ============================================

class TestRegraAcessoUpdateValidation:
    """Tests for RegraAcessoUpdate schema validation."""

    def test_update_invalid_day_rejected(self):
        """Updating with invalid day should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoUpdate(dias_especificos=[0, 1, 2])
        errors = exc_info.value.errors()
        assert any("dias_especificos" in str(e.get("loc", [])) for e in errors)

    def test_update_invalid_horario_rejected(self):
        """Updating with invalid horario should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            RegraAcessoUpdate(horarios=[{"inicio": "25:00", "fim": "18:00"}])
        errors = exc_info.value.errors()
        assert any("horarios" in str(e.get("loc", [])) for e in errors)

    def test_update_valid_dias(self):
        """Updating with valid dias should pass."""
        update = RegraAcessoUpdate(dias_especificos=[1, 2, 3])
        assert update.dias_especificos == [1, 2, 3]

    def test_update_valid_horarios(self):
        """Updating with valid horarios should pass."""
        update = RegraAcessoUpdate(horarios=[{"inicio": "09:00", "fim": "17:00"}])
        assert len(update.horarios) == 1

    def test_update_none_values(self):
        """Updating with None values should pass (partial update)."""
        update = RegraAcessoUpdate(bloquear_em_feriado=True)
        assert update.dias_especificos is None
        assert update.horarios is None
        assert update.bloquear_em_feriado is True

    def test_update_duplicate_dias_deduplicated(self):
        """Updating with duplicate dias should be deduplicated."""
        update = RegraAcessoUpdate(dias_especificos=[5, 3, 5, 1, 3])
        assert update.dias_especificos == [1, 3, 5]
