"""
Cofre service client for certificate operations.

This client communicates with the Cofre microservice (port 8002) for:
- Certificate upload and encryption (using KMS for keys)
- Certificate storage
- Digital signing
- Audit logging
"""

import base64
import logging
import uuid
from typing import Any, Optional

from backend.app.core.exceptions import (
    CertificateNotFoundError,
    CertificateSigningError,
    CofreServiceError,
)
from backend.app.core.service_config import settings
from backend.app.services.base_client import BaseServiceClient

logger = logging.getLogger(__name__)


class CofreClient(BaseServiceClient):
    """
    HTTP client for the Cofre microservice.

    All certificate encryption and signing operations are delegated to this service.
    Cofre uses KMS (port 8000) internally for key management.
    """

    def __init__(self):
        super().__init__(
            service_name="Cofre",
            base_url=settings.cofre_service_url,
            timeout=settings.cofre_service_timeout,
        )
        self._service_token: Optional[str] = None
        self._api_key = settings.cofre_service_api_key

    async def health_check(self) -> bool:
        """Check if Cofre service is healthy."""
        try:
            response = await self._get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def _ensure_authenticated(self) -> str:
        """
        Ensure we have a valid service token for Cofre.

        Authenticates using API key if no token exists or if token expired.

        Returns:
            Valid bearer token
        """
        if self._service_token:
            # TODO: Check token expiration and refresh if needed
            return self._service_token

        if not self._api_key:
            raise CofreServiceError(
                message="COFRE_SERVICE_API_KEY not configured",
                status_code=500,
            )

        response = await self._post(
            "/api/v1/auth/login",
            headers={"api-key": self._api_key},
        )

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to authenticate with Cofre: {response.text}",
                status_code=response.status_code,
            )

        data = response.json()
        self._service_token = data.get("token")

        if not self._service_token:
            raise CofreServiceError(
                message="No token returned from Cofre authentication",
                status_code=500,
            )

        logger.info("Authenticated with Cofre service")
        return self._service_token

    async def _auth_headers(self) -> dict[str, str]:
        """Get authorization headers with bearer token."""
        token = await self._ensure_authenticated()
        return {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------------------
    # Certificate Management
    # -------------------------------------------------------------------------

    async def upload_certificate(
        self,
        arquivo: bytes,
        senha: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Upload certificate to Cofre for encryption and storage.

        Cofre will:
        1. Validate the PFX/P12 file
        2. Request a DEK from KMS
        3. Encrypt the certificate with the DEK
        4. Store the encrypted certificate

        Args:
            arquivo: Certificate file content (PFX/P12 bytes)
            senha: Certificate password
            metadata: Optional metadata (nome_arquivo, empresa_id, criado_por)

        Returns:
            dict with:
            - certificate_id: ID in Cofre
            - proprietario: Certificate owner (CN)
            - emitido_por: Certificate issuer
            - validade_inicio: Valid from date
            - valido_ate: Valid until date

        Raises:
            CofreServiceError: If upload fails
        """
        headers = await self._auth_headers()
        print('metadata: ', metadata)
        # Prepare multipart form data
        files = {
            "arquivo": (metadata['nome_arquivo'], arquivo, "application/x-pkcs12"),
        }
        data = {
            "senha": senha,
        }

        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                if value is not None:
                    data[key] = str(value)

        response = await self._post(
            "/api/v1/certificates",
            files=files,
            data=data,
            headers=headers,
        )

        if response.status_code == 400:
            raise CofreServiceError(
                message=f"Invalid certificate: {response.text}",
                status_code=400,
            )

        if response.status_code not in (200, 201):
            raise CofreServiceError(
                message=f"Failed to upload certificate: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def list_certificates(
        self,
        empresa_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        List certificates from Cofre.

        Args:
            empresa_id: Optional filter by empresa

        Returns:
            List of certificate dicts with metadata
        """
        headers = await self._auth_headers()
        params = {}
        if empresa_id:
            params["empresa_id"] = empresa_id

        response = await self._get(
            "/api/v1/certificates",
            headers=headers,
            params=params if params else None,
        )

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to list certificates: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_certificate(
        self,
        certificate_id: uuid.UUID,
    ) -> Optional[dict[str, Any]]:
        """
        Get certificate metadata from Cofre.

        Args:
            certificate_id: Certificate ID in Cofre

        Returns:
            Certificate dict or None if not found
        """
        headers = await self._auth_headers()

        response = await self._get(
            f"/api/v1/certificates/{certificate_id}",
            headers=headers,
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to get certificate: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def sign_data(
        self,
        certificate_id: uuid.UUID,
        data: bytes,
        user_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Sign data using a certificate stored in Cofre.

        Cofre will:
        1. Retrieve the encrypted certificate
        2. Get the DEK from KMS
        3. Decrypt the certificate
        4. Sign the data with the certificate's private key
        5. Log the operation in audit

        Args:
            certificate_id: Certificate ID in Cofre
            data: Data to sign (raw bytes, will be SHA-256 hashed)
            user_context: Optional context for audit (usuario_id, empresa_id)

        Returns:
            Base64-encoded signature

        Raises:
            CertificateNotFoundError: If certificate doesn't exist
            CertificateSigningError: If signing fails
        """
        headers = await self._auth_headers()

        # Cofre expects base64-encoded SHA-256 digest
        import hashlib

        digest = hashlib.sha256(data).digest()
        data_b64 = base64.b64encode(digest).decode("utf-8")

        request_body = {
            "cert_id": str(certificate_id),
            "data": data_b64,
        }

        # Add user context for audit if provided
        if user_context:
            request_body["context"] = user_context

        response = await self._post(
            "/api/v1/certificates/sign",
            json=request_body,
            headers=headers,
        )

        if response.status_code == 404:
            raise CertificateNotFoundError(certificate_id=certificate_id)

        if response.status_code == 400:
            raise CertificateSigningError(
                message=f"Signing failed: {response.text}",
                detail=response.json() if response.content else None,
            )

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to sign data: {response.text}",
                status_code=response.status_code,
            )

        result = response.json()
        return result.get("signature_b64", "")

    async def delete_certificate(
        self,
        certificate_id: uuid.UUID,
    ) -> bool:
        """
        Delete certificate from Cofre.

        Args:
            certificate_id: Certificate ID in Cofre

        Returns:
            True if deleted successfully
        """
        headers = await self._auth_headers()

        response = await self._delete(
            f"/api/v1/certificates/{certificate_id}",
            headers=headers,
        )

        if response.status_code == 404:
            raise CertificateNotFoundError(certificate_id=certificate_id)

        return response.status_code in (200, 204)

    async def get_certificates_der(
        self,
        certificate_ids: list[str],
    ) -> list[dict[str, Any]]:
        """
        Get DER-encoded certificate data for multiple certificates.

        Args:
            certificate_ids: List of Cofre certificate IDs

        Returns:
            List of dicts with id, label, cert_der_b64
        """
        headers = await self._auth_headers()

        response = await self._post(
            "/api/v1/certificates/der",
            json={"ids": certificate_ids},
            headers=headers,
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise CertificateNotFoundError(
                message="One or more certificates not found"
            )
        else:
            raise CofreServiceError(
                message=f"Failed to get certificate DER data: {response.text}",
                status_code=response.status_code,
            )

    # -------------------------------------------------------------------------
    # Audit Logs
    # -------------------------------------------------------------------------

    async def search_audit_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        actor_id: Optional[str] = None,
        operation: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Search audit logs from Cofre.

        Args:
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            actor_id: Filter by actor (user) ID
            operation: Filter by operation type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            success: Filter by success status
            limit: Max results
            offset: Pagination offset

        Returns:
            dict with logs list and pagination info
        """
        headers = await self._auth_headers()

        params = {
            "limit": limit,
            "offset": offset,
        }

        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if actor_id:
            params["actor_id"] = actor_id
        if operation:
            params["operation"] = operation
        if resource_type:
            params["resource_type"] = resource_type
        if resource_id:
            params["resource_id"] = resource_id
        if success is not None:
            params["success"] = str(success).lower()

        response = await self._post(
            "/api/v1/audit-logs/search",
            headers=headers,
            params=params,
        )

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to search audit logs: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_audit_log(
        self,
        audit_log_id: int,
    ) -> Optional[dict[str, Any]]:
        """
        Get specific audit log entry.

        Args:
            audit_log_id: Audit log ID

        Returns:
            Audit log dict or None if not found
        """
        headers = await self._auth_headers()

        response = await self._get(
            f"/api/v1/audit-logs/{audit_log_id}",
            headers=headers,
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise CofreServiceError(
                message=f"Failed to get audit log: {response.text}",
                status_code=response.status_code,
            )

        return response.json()


# Singleton instance
cofre_client = CofreClient()
