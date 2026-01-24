"""
Custom exceptions for microservices orchestration.

These exceptions handle errors when communicating with external services
(Auth, Cofre, KMS) and provide appropriate HTTP responses.
"""

from typing import Optional


class ServiceError(Exception):
    """Base exception for all service-related errors."""

    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: Optional[int] = None,
        detail: Optional[dict] = None,
    ):
        self.message = message
        self.service_name = service_name
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.service_name}] {self.message}"


class ServiceUnavailableError(ServiceError):
    """Raised when a downstream service is unavailable or unreachable."""

    def __init__(
        self,
        service_name: str,
        message: str = "Service temporarily unavailable",
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            service_name=service_name,
            status_code=503,
            detail=detail,
        )


class ServiceTimeoutError(ServiceError):
    """Raised when a service request times out."""

    def __init__(
        self,
        service_name: str,
        timeout: float,
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=f"Request timed out after {timeout} seconds",
            service_name=service_name,
            status_code=504,
            detail=detail,
        )


class AuthServiceError(ServiceError):
    """Raised for Auth service specific errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            service_name="Auth",
            status_code=status_code,
            detail=detail,
        )


class AuthenticationError(AuthServiceError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        detail: Optional[dict] = None,
    ):
        super().__init__(message=message, status_code=401, detail=detail)


class CofreServiceError(ServiceError):
    """Raised for Cofre service specific errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            service_name="Cofre",
            status_code=status_code,
            detail=detail,
        )


class CertificateNotFoundError(CofreServiceError):
    """Raised when a certificate is not found in Cofre."""

    def __init__(
        self,
        certificate_id: str,
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=f"Certificate {certificate_id} not found",
            status_code=404,
            detail=detail,
        )


class CertificateSigningError(CofreServiceError):
    """Raised when certificate signing fails."""

    def __init__(
        self,
        message: str = "Failed to sign with certificate",
        detail: Optional[dict] = None,
    ):
        super().__init__(message=message, status_code=500, detail=detail)


class CircuitBreakerOpenError(ServiceError):
    """Raised when circuit breaker is open and requests are blocked."""

    def __init__(
        self,
        service_name: str,
        recovery_timeout: int,
        detail: Optional[dict] = None,
    ):
        super().__init__(
            message=f"Circuit breaker open, retry after {recovery_timeout} seconds",
            service_name=service_name,
            status_code=503,
            detail={"retry_after": recovery_timeout, **(detail or {})},
        )
