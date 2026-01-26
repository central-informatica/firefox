"""
Authentication routes - proxies to Auth microservice.

All authentication operations (login, logout, 2FA, password reset)
are delegated to the Auth service (port 8001).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, field_validator

# from backend.app.api.deps import get_current_user
from backend.app.core.exceptions import AuthenticationError, AuthServiceError
from backend.app.utils.validators import (
    validate_cnpj,
    validate_postal_code,
    validate_state_code,
)
from backend.app.services.auth_client import auth_client

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for OpenAPI documentation
bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Session token for authentication. Use the session_token from login response.",
    auto_error=False,
)


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class LoginRequest(BaseModel):
    """Login request body."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response."""

    message: str
    requires_2fa: bool = False
    access_token: str | None = None
    csrf_token: str | None = None


class Verify2FARequest(BaseModel):
    """2FA verification request."""
    user_id: str
    code: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request."""

    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    current_password: str
    new_password: str


class RegisterRequest(BaseModel):
    """Registration request (organization + admin user)."""

    # Organization
    organization_name: str
    slug: str | None = None
    domain: str | None = None

    # Company identification
    cnpj: str

    # Company address
    address_street: str
    address_city: str
    address_state: str
    address_country: str
    address_postal_code: str

    # Admin user
    admin_email: EmailStr
    admin_password: str
    admin_first_name: str
    admin_last_name: str

    @field_validator('cnpj')
    @classmethod
    def validate_cnpj_format(cls, v: str) -> str:
        """Validate CNPJ format (14 digits)."""
        return validate_cnpj(v)

    @field_validator('address_postal_code')
    @classmethod
    def validate_postal_code_format(cls, v: str) -> str:
        """Validate CEP format (XXXXX-XXX)."""
        return validate_postal_code(v)

    @field_validator('address_state')
    @classmethod
    def validate_state_format(cls, v: str) -> str:
        """Validate Brazilian state code."""
        return validate_state_code(v)

    @field_validator('address_street')
    @classmethod
    def validate_street(cls, v: str) -> str:
        """Validate street address."""
        if len(v.strip()) < 3:
            raise ValueError("Street address must be at least 3 characters")
        if len(v) > 255:
            raise ValueError("Street address must be less than 255 characters")
        return v.strip()

    @field_validator('address_city')
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Validate city name."""
        if len(v.strip()) < 2:
            raise ValueError("City name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("City name must be less than 100 characters")
        return v.strip()

    @field_validator('address_country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country name."""
        if len(v.strip()) < 2:
            raise ValueError("Country name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Country name must be less than 100 characters")
        return v.strip()


class VerifyEmailRequest(BaseModel):
    """Email verification request."""
    token: str


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
) -> LoginResponse:
    """
    Authenticate user via Auth service.

    Proxies the login request to Auth service and returns
    the access_token and csrf_token in the response body.
    """
    try:
        result = await auth_client.login(
            email=credentials.email,
            password=credentials.password,
            client_type="web",
        )

        # Extract tokens from Auth service response
        tokens = result.get("tokens", {})
        data = result.get("data", {})
        requires_2fa = data.get("requires_2fa", False)

        return LoginResponse(
            message="Login realizado com sucesso"
            if not requires_2fa
            else "Codigo 2FA enviado para seu email",
            requires_2fa=requires_2fa,
            access_token=tokens.get("access_token"),
            csrf_token=tokens.get("csrf_token"),
        )

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, str]:
    """
    Logout user and invalidate session.

    Requires Authorization Bearer header with session token.
    Proxies logout to Auth service to invalidate the session.
    """
    session_token = credentials.credentials

    if session_token:
        try:
            await auth_client.logout(session_token)
        except Exception:
            pass

    return {"message": "Logout realizado com sucesso"}


@router.post("/verify-2fa")
async def verify_2fa(
    request: Request,
    data: Verify2FARequest,
) -> dict[str, Any]:
    """
    Verify 2FA code after login.

    Forwards request to Auth service /api/v1/auth/verify-2fa.
    """
    # Forward Authorization header if present
    headers = {}
    if auth_header := request.headers.get("Authorization"):
        headers["Authorization"] = auth_header

    try:
        result = await auth_client.verify_2fa(
            body=data.model_dump(),
            headers=headers if headers else None,
        )
        return result

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.get("/me")
async def get_me(
    request: Request,
) -> dict[str, Any]:
    """
    Get current authenticated user.

    Forwards request to Auth service /api/v1/auth/me.
    """
    excluded_headers = {'content-length', 'host', 'transfer-encoding', 'content-type'}
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded_headers
    }

    try:
        return await auth_client.proxy_request(
            method="GET",
            path="/api/v1/auth/me",
            headers=headers,
        )
    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 401,
            detail=e.message,
        )


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
) -> dict[str, str]:
    """
    Request password reset email.

    Always returns success to prevent email enumeration.
    """
    try:
        await auth_client.forgot_password(email=data.email)
    except Exception:
        # Always return success to prevent email enumeration
        pass

    return {
        "message": "Se o email estiver cadastrado, voce recebera um link para redefinir sua senha"
    }


@router.post("/reset-password")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
) -> dict[str, str]:
    """
    Reset password using token from email.
    """
    headers = {}
    if auth_header := request.headers.get("Authorization"):
        headers["Authorization"] = auth_header

    try:
        success = await auth_client.reset_password(
            token=data.token,
            new_password=data.new_password,
            headers=headers if headers else None,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token invalido ou expirado",
            )

        return {"message": "Senha redefinida com sucesso"}

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 400,
            detail=e.message,
        )


@router.post("/change-password")
async def change_password(
    request: Request,
    data: ChangePasswordRequest,
) -> dict[str, str]:
    """
    Change password for authenticated user.

    Requires Authorization Bearer token in header.
    Proxies the request to Auth service to validate current password
    and update to new password.
    """
    # Forward headers, excluding hop-by-hop and body-related headers
    excluded_headers = {'content-length', 'host', 'transfer-encoding', 'content-type'}
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded_headers
    }

    try:
        success = await auth_client.change_password(
            current_password=data.current_password,
            new_password=data.new_password,
            headers=headers,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao alterar senha",
            )

        return {"message": "Senha alterada com sucesso"}

    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )
    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/register")
async def register(
    data: RegisterRequest,
    response: Response,
) -> dict[str, Any]:
    """
    Register new organization with admin user.

    Creates both the organization and the admin user in Auth service.
    """
    try:
        result = await auth_client.create_organization_with_admin(
            data=data.model_dump(exclude_none=True)
        )

        return result

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
) -> dict[str, Any]:
    """
    Verify email using token from registration email.

    Proxies request to Auth service /api/v1/auth/verify-email.
    """
    try:
        result = await auth_client.verify_email(token=data.token)
        return result

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 400,
            detail=e.message,
        )
