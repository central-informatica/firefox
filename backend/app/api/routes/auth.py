"""
Authentication routes - proxies to Auth microservice.

All authentication operations (login, logout, 2FA, password reset)
are delegated to the Auth service (port 8001).
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, field_validator
import re

# from backend.app.api.deps import get_current_user
from backend.app.core.config import DEBUG


# Password validation constants
MIN_PASSWORD_LENGTH = 12
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\-_#^+=])[A-Za-z\d@$!%*?&\-_#^+=]{12,}$'
)


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements:
    - At least 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (@$!%*?&-_#^+=)
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Senha deve ter pelo menos {MIN_PASSWORD_LENGTH} caracteres")

    if not re.search(r'[a-z]', password):
        raise ValueError("Senha deve conter pelo menos uma letra minuscula")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Senha deve conter pelo menos uma letra maiuscula")

    if not re.search(r'\d', password):
        raise ValueError("Senha deve conter pelo menos um numero")

    if not re.search(r'[@$!%*?&\-_#^+=]', password):
        raise ValueError("Senha deve conter pelo menos um caractere especial (@$!%*?&-_#^+=)")

    return password
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
    user_id: str | None = None


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

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets security requirements."""
        return validate_password_strength(v)


class ChangePasswordRequest(BaseModel):
    """Change password request."""

    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets security requirements."""
        return validate_password_strength(v)


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

    @field_validator('admin_password')
    @classmethod
    def validate_admin_password(cls, v: str) -> str:
        """Validate admin password meets security requirements."""
        return validate_password_strength(v)

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


@router.post("/login/web", response_model=LoginResponse)
async def login_web(
    credentials: LoginRequest,
    response: Response,
) -> LoginResponse:
    """
    Authenticate user via Auth service for web clients.

    Web clients receive 1-hour session tokens with CSRF protection.
    Tokens are set as cookies:
    - session_token: HttpOnly cookie (not accessible to JS, prevents XSS)
    - csrf_token: Readable cookie (accessible to JS for header)
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

        access_token = tokens.get("access_token")
        csrf_token = tokens.get("csrf_token")

        # Set cookies only if we have tokens (not during 2FA flow)
        if access_token and not requires_2fa:
            # Set HttpOnly cookie for session token (not accessible to JS)
            response.set_cookie(
                key="session_token",
                value=access_token,
                httponly=True,
                secure=not DEBUG,  # HTTPS only in production (DEBUG=false)
                samesite="lax",
                max_age=3600,  # 1 hour
                path="/",
            )

            # Set readable cookie for CSRF token (accessible to JS)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # JS needs to read this
                secure=not DEBUG,  # HTTPS only in production (DEBUG=false)
                samesite="lax",
                max_age=3600,
                path="/",
            )

        return LoginResponse(
            message="Login realizado com sucesso"
            if not requires_2fa
            else "Codigo 2FA enviado para seu email",
            requires_2fa=requires_2fa,
            access_token=None,  # Don't expose in body, use cookies
            csrf_token=None,  # Don't expose in body, use cookies
            user_id=str(data.get("user_id")) if data.get("user_id") else None,
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


@router.post("/login/desktop", response_model=LoginResponse)
async def login_desktop(
    credentials: LoginRequest,
) -> LoginResponse:
    """
    Authenticate user via Auth service for desktop clients.

    Desktop clients receive 7-day access tokens instead of 1-hour.
    No CSRF token is returned since desktop apps don't need CSRF protection.

    Proxies the login request to Auth service /api/v1/auth/login/desktop.
    """
    try:
        result = await auth_client.login(
            email=credentials.email,
            password=credentials.password,
            client_type="desktop",
        )

        # Extract tokens and data from Auth service response
        tokens = result.get("tokens", {})
        data = result.get("data", {})
        requires_2fa = data.get("requires_2fa", False)
        user_id = data.get("user_id")

        return LoginResponse(
            message="Login realizado com sucesso"
            if not requires_2fa
            else "Codigo 2FA enviado para seu email",
            requires_2fa=requires_2fa,
            access_token=tokens.get("access_token"),
            csrf_token=None,  # Desktop doesn't use CSRF protection
            user_id=str(user_id) if user_id else None,
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
    request: Request,
    response: Response,
) -> dict[str, str]:
    """
    Logout user and invalidate session.

    Reads session token from HttpOnly cookie and invalidates it.
    Clears both session_token and csrf_token cookies.
    """
    # Get session token from cookie
    session_token = request.cookies.get("session_token")

    if session_token:
        try:
            await auth_client.logout(session_token)
        except Exception:
            pass

    # Clear cookies
    response.delete_cookie(key="session_token", path="/")
    response.delete_cookie(key="csrf_token", path="/")

    return {"message": "Logout realizado com sucesso"}


@router.post("/verify-2fa")
async def verify_2fa(
    request: Request,
    response: Response,
    data: Verify2FARequest,
) -> dict[str, Any]:
    """
    Verify 2FA code after login.

    Forwards request to Auth service /api/v1/auth/verify-2fa.
    On success, sets session cookies.
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

        # Log the result for debugging
        import logging
        logging.info(f"2FA verify result: {result}")

        # Extract tokens from Auth service response and set cookies
        # Try both "tokens" object and direct properties
        tokens = result.get("tokens", {})
        access_token = tokens.get("access_token") or result.get("access_token")
        csrf_token = tokens.get("csrf_token") or result.get("csrf_token")

        if access_token:
            # Set HttpOnly cookie for session token (not accessible to JS)
            response.set_cookie(
                key="session_token",
                value=access_token,
                httponly=True,
                secure=not DEBUG,
                samesite="lax",
                max_age=3600,
                path="/",
            )

            # Set readable cookie for CSRF token (accessible to JS)
            if csrf_token:
                response.set_cookie(
                    key="csrf_token",
                    value=csrf_token,
                    httponly=False,
                    secure=not DEBUG,
                    samesite="lax",
                    max_age=3600,
                    path="/",
                )

        return {"message": "Verificacao 2FA concluida com sucesso"}

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

    Reads session token from HttpOnly cookie and CSRF token from header.
    Forwards request to Auth service /api/v1/auth/me with Authorization header.
    """
    # Get session token from cookie
    session_token = request.cookies.get("session_token")
    csrf_token = request.headers.get("X-CSRF-Token")

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nao autenticado",
        )

    # Build headers for auth service, including Authorization
    excluded_headers = {'content-length', 'host', 'transfer-encoding', 'content-type', 'cookie'}
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in excluded_headers
    }
    # Add Authorization header with session token
    headers["Authorization"] = f"Bearer {session_token}"

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


class AcceptInvitationRequest(BaseModel):
    """Accept invitation request."""
    token: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements."""
        return validate_password_strength(v)


@router.post("/invitations/accept")
async def accept_invitation(
    data: AcceptInvitationRequest,
) -> dict[str, Any]:
    """
    Accept an employee invitation and create user account.

    Proxies request to Auth service /api/v1/invitations/accept.
    """
    try:
        result = await auth_client.proxy_request(
            method="POST",
            path="/api/v1/invitations/accept",
            json={
                "token": data.token,
                "password": data.password,
                "first_name": data.first_name,
                "last_name": data.last_name,
            },
        )
        return result

    except AuthServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 400,
            detail=e.message,
        )
