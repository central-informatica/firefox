"""Validation utilities for Brazilian business data."""

import re


def validate_cnpj(cnpj: str) -> str:
    """
    Validate and format CNPJ (Brazilian company registration number).

    Args:
        cnpj: CNPJ string (accepts with or without formatting)

    Returns:
        Formatted CNPJ (14 digits only)

    Raises:
        ValueError: If CNPJ format is invalid
    """
    # Remove non-digit characters
    formatted = re.sub(r'\D', '', cnpj)

    # Validate length
    if len(formatted) != 14:
        raise ValueError("CNPJ must have exactly 14 digits")

    # Validate all digits
    if not formatted.isdigit():
        raise ValueError("CNPJ must contain only digits")

    return formatted


def validate_postal_code(postal_code: str) -> str:
    """
    Validate Brazilian CEP (postal code).

    Args:
        postal_code: CEP string (accepts XXXXX-XXX or XXXXXXXX format)

    Returns:
        Formatted postal code (with hyphen: XXXXX-XXX)

    Raises:
        ValueError: If CEP format is invalid
    """
    # Remove hyphen
    formatted = postal_code.replace('-', '')

    # Validate length and digits
    if len(formatted) != 8 or not formatted.isdigit():
        raise ValueError("Postal code must be in format XXXXX-XXX or XXXXXXXX")

    # Return with hyphen
    return f"{formatted[:5]}-{formatted[5:]}"


def validate_state_code(state: str) -> str:
    """
    Validate Brazilian state code.

    Args:
        state: Two-letter state code

    Returns:
        Uppercase state code

    Raises:
        ValueError: If state code is invalid
    """
    VALID_STATES = {
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
        'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
        'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
    }

    state_upper = state.upper()
    if state_upper not in VALID_STATES:
        raise ValueError(f"Invalid Brazilian state code: {state}")

    return state_upper
