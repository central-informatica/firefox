"""
Base HTTP client for service-to-service communication.

Provides:
- Async HTTP client using httpx
- Retry logic with exponential backoff using tenacity
- Circuit breaker pattern for resilience
- Consistent error handling
"""

import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

import httpx
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.app.core.exceptions import (
    CircuitBreakerOpenError,
    ServiceError,
    ServiceTimeoutError,
    ServiceUnavailableError,
)
from backend.app.core.service_config import settings

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker implementation for service resilience.

    States:
    - CLOSED: Normal operation, requests are allowed
    - OPEN: Too many failures, requests are blocked
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def record_success(self) -> None:
        """Record a successful request."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker OPEN for {self.service_name} "
                f"after {self.failure_count} failures"
            )

    def can_execute(self) -> bool:
        """Check if requests can be executed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time is None:
                return True

            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info(
                    f"Circuit breaker HALF_OPEN for {self.service_name}, "
                    "testing recovery..."
                )
                return True

            return False

        # HALF_OPEN: allow one request to test
        return True

    def raise_if_open(self) -> None:
        """Raise exception if circuit is open."""
        if not self.can_execute():
            raise CircuitBreakerOpenError(
                service_name=self.service_name,
                recovery_timeout=self.recovery_timeout,
            )


class BaseServiceClient(ABC):
    """
    Base class for service clients with HTTP, retry, and circuit breaker.

    Subclasses should implement service-specific methods using the
    protected _request method for HTTP calls.
    """

    def __init__(
        self,
        service_name: str,
        base_url: str,
        timeout: float = 10.0,
    ):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._circuit_breaker = CircuitBreaker(
            service_name=service_name,
            failure_threshold=settings.circuit_breaker_failure_threshold,
            recovery_timeout=settings.circuit_breaker_recovery_timeout,
        )

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
            )
            logger.info(f"{self.service_name} client initialized: {self.base_url}")

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            logger.info(f"{self.service_name} client closed")

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, ensuring it's initialized."""
        if self._client is None:
            raise RuntimeError(
                f"{self.service_name} client not initialized. "
                "Call initialize() first."
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> httpx.Response:
        """
        Make an HTTP request with retry and circuit breaker.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            path: URL path (will be joined with base_url)
            json: JSON body
            data: Form data
            files: Files to upload
            headers: Additional headers
            cookies: Cookies to send
            params: Query parameters

        Returns:
            httpx.Response

        Raises:
            CircuitBreakerOpenError: If circuit is open
            ServiceTimeoutError: If request times out
            ServiceUnavailableError: If service is unreachable
            ServiceError: For other errors
        """
        # Check circuit breaker
        self._circuit_breaker.raise_if_open()

        try:
            response = await self._request_with_retry(
                method=method,
                path=path,
                json=json,
                data=data,
                files=files,
                headers=headers,
                cookies=cookies,
                params=params,
            )
            self._circuit_breaker.record_success()
            return response
        except CircuitBreakerOpenError:
            raise
        except RetryError as e:
            self._circuit_breaker.record_failure()
            original_error = e.last_attempt.exception()
            if isinstance(original_error, httpx.TimeoutException):
                raise ServiceTimeoutError(
                    service_name=self.service_name,
                    timeout=self.timeout,
                )
            raise ServiceUnavailableError(
                service_name=self.service_name,
                message=f"Service unavailable after retries: {original_error}",
            )
        except httpx.TimeoutException:
            self._circuit_breaker.record_failure()
            raise ServiceTimeoutError(
                service_name=self.service_name,
                timeout=self.timeout,
            )
        except httpx.ConnectError as e:
            self._circuit_breaker.record_failure()
            raise ServiceUnavailableError(
                service_name=self.service_name,
                message=f"Failed to connect: {e}",
            )
        except Exception as e:
            self._circuit_breaker.record_failure()
            logger.exception(f"Unexpected error calling {self.service_name}")
            raise ServiceError(
                message=str(e),
                service_name=self.service_name,
                status_code=500,
            )

    @retry(
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
        stop=stop_after_attempt(settings.retry_max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=settings.retry_wait_min,
            max=settings.retry_wait_max,
        ),
        reraise=True,
    )
    async def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Internal method with retry decorator."""
        logger.debug(f"{self.service_name} {method} {path}")
        return await self.client.request(method, path, **kwargs)

    async def _get(
        self,
        path: str,
        *,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> httpx.Response:
        """Convenience method for GET requests."""
        return await self._request(
            "GET",
            path,
            headers=headers,
            cookies=cookies,
            params=params,
        )

    async def _post(
        self,
        path: str,
        *,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> httpx.Response:
        """Convenience method for POST requests."""
        return await self._request(
            "POST",
            path,
            json=json,
            data=data,
            files=files,
            headers=headers,
            cookies=cookies,
        )

    async def _put(
        self,
        path: str,
        *,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> httpx.Response:
        """Convenience method for PUT requests."""
        return await self._request(
            "PUT",
            path,
            json=json,
            headers=headers,
            cookies=cookies,
        )

    async def _patch(
        self,
        path: str,
        *,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> httpx.Response:
        """Convenience method for PATCH requests."""
        return await self._request(
            "PATCH",
            path,
            json=json,
            headers=headers,
            cookies=cookies,
        )

    async def _delete(
        self,
        path: str,
        *,
        headers: Optional[dict] = None,
        cookies: Optional[dict] = None,
    ) -> httpx.Response:
        """Convenience method for DELETE requests."""
        return await self._request(
            "DELETE",
            path,
            headers=headers,
            cookies=cookies,
        )

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the service is healthy."""
        pass
