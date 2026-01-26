"""
Auth service client for authentication and user management.

This client communicates with the Auth microservice (port 8001) for:
- User authentication (login, logout, 2FA)
- Session validation
- User management (CRUD)
- Organization management
"""

import logging
from typing import Any, Optional

from backend.app.core.exceptions import AuthenticationError, AuthServiceError
from backend.app.core.service_config import settings
from backend.app.services.base_client import BaseServiceClient

logger = logging.getLogger(__name__)


class AuthClient(BaseServiceClient):
    """
    HTTP client for the Auth microservice.

    All authentication operations are delegated to this service.
    """

    def __init__(self):
        super().__init__(
            service_name="Auth",
            base_url=settings.auth_service_url,
            timeout=settings.auth_service_timeout,
        )

    async def health_check(self) -> bool:
        """Check if Auth service is healthy."""
        try:
            response = await self._get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def proxy_request(
        self,
        method: str,
        path: str,
        headers: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Generic proxy to auth service.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., /api/v1/users/)
            headers: Headers to forward
            json: JSON body
            params: Query parameters

        Returns:
            Auth service response

        Raises:
            AuthServiceError: If request fails
        """
        response = await self._request(
            method,
            path,
            headers=headers,
            json=json,
            params=params,
        )

        if response.status_code >= 400:
            raise AuthServiceError(
                message=response.text,
                status_code=response.status_code,
            )

        return response.json() if response.content else {}

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------

    async def login(
        self,
        email: str,
        password: str,
        client_type: str = "web",
    ) -> dict[str, Any]:
        """
        Authenticate user via Auth service.

        Args:
            email: User email
            password: User password
            client_type: "web" (1h token) or "desktop" (7d token)

        Returns:
            dict with session info and cookies to set

        Raises:
            AuthenticationError: If credentials are invalid
            AuthServiceError: If service returns an error
        """
        endpoint = f"/api/v1/auth/login/{client_type}"
        response = await self._post(
            endpoint,
            json={"email": email, "password": password},
        )

        if response.status_code == 401:
            raise AuthenticationError(
                message="Invalid credentials",
                detail=response.json() if response.content else None,
            )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Login failed: {response.text}",
                status_code=response.status_code,
            )

        # Extract tokens from response body
        data = response.json()

        return {
            "data": data,
            "tokens": {
                "access_token": data.get("access_token"),
                "csrf_token": data.get("csrf_token"),
            },
        }

    async def logout(self, session_token: str) -> bool:
        """
        Logout user and invalidate session.

        Args:
            session_token: The session token to invalidate

        Returns:
            True if logout successful
        """
        response = await self._post(
            "/api/v1/auth/logout",
            cookies={"session_token": session_token},
        )
        return response.status_code == 200

    async def verify_2fa(
        self,
        body: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Verify 2FA code after login.

        Forwards the request body and headers to Auth service.

        Args:
            body: Request body to forward
            headers: Request headers to forward

        Returns:
            dict with Auth service response
        """
        response = await self._post(
            "/api/v1/auth/verify-2fa",
            json=body,
            headers=headers,
        )

        if response.status_code == 401:
            raise AuthenticationError(
                message="Invalid 2FA code",
                detail=response.json() if response.content else None,
            )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"2FA verification failed: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_current_user(
        self,
        session_token: str,
        csrf_token: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Get current authenticated user from session.

        Args:
            session_token: Session token from cookie
            csrf_token: CSRF token (optional, for validation)

        Returns:
            User data dict or None if session invalid

        The returned dict contains:
        - id: User ID
        - email: User email
        - first_name, last_name: User name
        - organization_id: Current organization
        - is_owner: Whether user owns the organization
        - requires_2fa: Whether 2FA is required
        """
        headers = {}
        if csrf_token:
            headers["X-CSRF-Token"] = csrf_token

        try:
            response = await self._get(
                "/api/v1/auth/me",
                cookies={"session_token": session_token},
                headers=headers if headers else None,
            )

            if response.status_code == 401:
                return None

            if response.status_code == 200:
                return response.json()

            logger.warning(
                f"Unexpected status from /auth/me: {response.status_code}"
            )
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise

    async def forgot_password(self, email: str) -> bool:
        """
        Request password reset email.

        Args:
            email: User email

        Returns:
            True if request sent (always returns true for security)
        """
        response = await self._post(
            "/api/v1/auth/forgot-password",
            json={"email": email},
        )
        return response.status_code == 200

    async def verify_email(self, token: str) -> dict[str, Any]:
        """
        Verify email using token.

        Args:
            token: Email verification token

        Returns:
            Auth service response
        """
        response = await self._post(
            "/api/v1/auth/verify-email",
            json={"token": token},
        )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Email verification failed: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def reset_password(
        self,
        token: str,
        new_password: str,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """
        Reset password using token from email.

        Args:
            token: Reset token from email
            new_password: New password
            headers: Optional headers to forward (Authorization)

        Returns:
            True if password reset successful
        """
        response = await self._post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": new_password},
            headers=headers,
        )
        return response.status_code == 200

    async def change_password(
        self,
        current_password: str,
        new_password: str,
        headers: dict[str, str] | None = None,
    ) -> bool:
        """
        Change password for authenticated user.

        Args:
            current_password: Current password
            new_password: New password
            headers: Headers to forward (including Authorization)

        Returns:
            True if password changed successfully
        """
        print('veio aquio auth client')
        response = await self._post(
            "/api/v1/auth/change-password",
            json={
                "current_password": current_password,
                "new_password": new_password,
            },
            headers=headers,
        )

        if response.status_code == 401:
            raise AuthenticationError(
                message="Invalid current password",
            )

        return response.status_code == 200

    # -------------------------------------------------------------------------
    # User Management
    # -------------------------------------------------------------------------

    async def list_users(
        self,
        session_token: str,
        organization_id: Optional[int] = None,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        List users in organization.

        Args:
            session_token: Session token
            organization_id: Filter by organization (optional)
            include_deleted: Include soft-deleted users
            limit: Max results
            offset: Pagination offset

        Returns:
            dict with users list and pagination info
        """
        params = {
            "limit": limit,
            "offset": offset,
            "include_deleted": str(include_deleted).lower(),
        }
        if organization_id:
            params["organization_id"] = organization_id

        response = await self._get(
            "/api/v1/users/",
            cookies={"session_token": session_token},
            params=params,
        )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to list users: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_user(
        self,
        session_token: str,
        user_id: int,
    ) -> Optional[dict[str, Any]]:
        """
        Get specific user by ID.

        Args:
            session_token: Session token
            user_id: User ID

        Returns:
            User dict or None if not found
        """
        response = await self._get(
            f"/api/v1/users/{user_id}",
            cookies={"session_token": session_token},
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to get user: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def update_user(
        self,
        session_token: str,
        user_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Update user.

        Args:
            session_token: Session token
            user_id: User ID
            data: Update data (first_name, last_name, is_active, requires_2fa)

        Returns:
            Updated user dict
        """
        response = await self._put(
            f"/api/v1/users/{user_id}",
            json=data,
            cookies={"session_token": session_token},
        )

        if response.status_code not in (200, 204):
            raise AuthServiceError(
                message=f"Failed to update user: {response.text}",
                status_code=response.status_code,
            )

        return response.json() if response.content else {}

    async def delete_user(
        self,
        session_token: str,
        user_id: int,
    ) -> bool:
        """
        Soft delete user.

        Args:
            session_token: Session token
            user_id: User ID

        Returns:
            True if deleted successfully
        """
        response = await self._delete(
            f"/api/v1/users/{user_id}",
            cookies={"session_token": session_token},
        )
        return response.status_code in (200, 204)

    # -------------------------------------------------------------------------
    # Organization Management
    # -------------------------------------------------------------------------

    async def list_organizations(
        self,
        session_token: str,
    ) -> list[dict[str, Any]]:
        """
        List organizations owned by current user.

        Args:
            session_token: Session token

        Returns:
            List of organization dicts
        """
        response = await self._get(
            "/api/v1/organizations/",
            cookies={"session_token": session_token},
        )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to list organizations: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_organization(
        self,
        session_token: str,
        org_id: int,
    ) -> Optional[dict[str, Any]]:
        """
        Get specific organization.

        Args:
            session_token: Session token
            org_id: Organization ID

        Returns:
            Organization dict or None if not found
        """
        response = await self._get(
            f"/api/v1/organizations/{org_id}",
            cookies={"session_token": session_token},
        )

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to get organization: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def create_organization_with_admin(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create organization with admin user (registration flow).

        Args:
            data: Registration data including:
                - organization_name (required) - Company name
                - slug (optional) - URL-friendly organization identifier
                - domain (optional) - Organization domain
                - cnpj (required) - Brazilian company registration number (14 digits)
                - address_street (required) - Street address
                - address_city (required) - City name
                - address_state (required) - Two-letter state code (e.g., SP, RJ)
                - address_country (required) - Country name
                - address_postal_code (required) - Brazilian CEP (XXXXX-XXX format)
                - admin_email (required) - Admin user email
                - admin_password (required) - Admin user password
                - admin_first_name (required) - Admin user first name
                - admin_last_name (required) - Admin user last name

        Returns:
            dict with created organization and admin user

        Raises:
            AuthServiceError: If organization creation fails
        """
        response = await self._post(
            "/api/v1/organizations/register-with-admin",
            json=data,
        )

        if response.status_code not in (200, 201):
            raise AuthServiceError(
                message=f"Failed to create organization: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def get_organization_members(
        self,
        session_token: str,
        org_id: int,
    ) -> list[dict[str, Any]]:
        """
        List members of an organization.

        Args:
            session_token: Session token
            org_id: Organization ID

        Returns:
            List of member dicts
        """
        response = await self._get(
            f"/api/v1/organizations/{org_id}/members",
            cookies={"session_token": session_token},
        )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to get organization members: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    # -------------------------------------------------------------------------
    # Employee Invitations
    # -------------------------------------------------------------------------

    async def create_invitation(
        self,
        session_token: str,
        email: str,
        organization_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Create employee invitation.

        Args:
            session_token: Session token (must be org owner)
            email: Email to invite
            organization_id: Organization to invite to (optional)

        Returns:
            Invitation dict
        """
        data = {"email": email}
        if organization_id:
            data["organization_id"] = organization_id

        response = await self._post(
            "/api/v1/invitations/",
            json=data,
            cookies={"session_token": session_token},
        )

        if response.status_code not in (200, 201):
            raise AuthServiceError(
                message=f"Failed to create invitation: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def list_invitations(
        self,
        session_token: str,
        include_accepted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List invitations for current user's organization.

        Args:
            session_token: Session token
            include_accepted: Include already accepted invitations
            limit: Max results
            offset: Pagination offset

        Returns:
            List of invitation dicts
        """
        response = await self._get(
            "/api/v1/invitations/",
            cookies={"session_token": session_token},
            params={
                "include_accepted": str(include_accepted).lower(),
                "limit": limit,
                "offset": offset,
            },
        )

        if response.status_code != 200:
            raise AuthServiceError(
                message=f"Failed to list invitations: {response.text}",
                status_code=response.status_code,
            )

        return response.json()

    async def revoke_invitation(
        self,
        session_token: str,
        invitation_id: int,
    ) -> bool:
        """
        Revoke a pending invitation.

        Args:
            session_token: Session token
            invitation_id: Invitation ID

        Returns:
            True if revoked successfully
        """
        response = await self._delete(
            f"/api/v1/invitations/{invitation_id}",
            cookies={"session_token": session_token},
        )
        return response.status_code in (200, 204)


# Singleton instance
auth_client = AuthClient()
