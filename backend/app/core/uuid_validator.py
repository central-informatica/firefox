"""
UUID validation utilities.

Provides centralized UUID validation to prevent SQL errors from invalid UUID strings.
"""

import uuid
from fastapi import HTTPException, status


def validate_uuid(uuid_string: str, field_name: str = "ID") -> str:
    """
    Validate that a string is a valid UUID.

    Args:
        uuid_string: The string to validate as UUID
        field_name: The name of the field for error messages

    Returns:
        The original UUID string if valid

    Raises:
        HTTPException: 400 if the UUID is invalid, 404 if empty/None
    """
    if not uuid_string:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{field_name} não encontrado",
        )

    try:
        # Try to parse as UUID - this will raise ValueError if invalid
        uuid.UUID(uuid_string)
        return uuid_string
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} inválido: '{uuid_string}' não é um UUID válido",
        )


def validate_uuids(**kwargs: str) -> dict[str, str]:
    """
    Validate multiple UUIDs at once.

    Example:
        validate_uuids(plano_id=plano_id, empresa_id=empresa_id)

    Returns:
        Dictionary with validated UUIDs

    Raises:
        HTTPException: If any UUID is invalid
    """
    validated = {}
    for field_name, uuid_string in kwargs.items():
        if uuid_string is not None:  # Allow None values
            validated[field_name] = validate_uuid(uuid_string, field_name)
        else:
            validated[field_name] = None
    return validated
