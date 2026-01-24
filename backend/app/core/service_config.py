"""
Service configuration for microservices orchestration.

This module provides configuration for connecting to external services:
- Auth Service (8001): Authentication, users, organizations
- Cofre Service (8002): Certificate encryption, storage, signing
"""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class ServiceSettings:
    """Configuration settings for external services."""

    # Auth Service
    auth_service_url: str
    auth_service_timeout: float

    # Cofre Service
    cofre_service_url: str
    cofre_service_api_key: str
    cofre_service_timeout: float

    # Circuit Breaker
    circuit_breaker_failure_threshold: int
    circuit_breaker_recovery_timeout: int

    # Retry settings
    retry_max_attempts: int
    retry_wait_min: float
    retry_wait_max: float


@lru_cache
def get_service_settings() -> ServiceSettings:
    """
    Get service settings from environment variables.
    Uses lru_cache to ensure settings are loaded once.
    """
    return ServiceSettings(
        # Auth Service
        auth_service_url=os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8001"),
        auth_service_timeout=float(os.getenv("AUTH_SERVICE_TIMEOUT", "10.0")),
        # Cofre Service
        cofre_service_url=os.getenv("COFRE_SERVICE_URL", "http://127.0.0.1:8002"),
        cofre_service_api_key=os.getenv("COFRE_SERVICE_API_KEY", ""),
        cofre_service_timeout=float(os.getenv("COFRE_SERVICE_TIMEOUT", "30.0")),
        # Circuit Breaker
        circuit_breaker_failure_threshold=int(
            os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")
        ),
        circuit_breaker_recovery_timeout=int(
            os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "30")
        ),
        # Retry
        retry_max_attempts=int(os.getenv("RETRY_MAX_ATTEMPTS", "3")),
        retry_wait_min=float(os.getenv("RETRY_WAIT_MIN", "0.5")),
        retry_wait_max=float(os.getenv("RETRY_WAIT_MAX", "2.0")),
    )


settings = get_service_settings()
