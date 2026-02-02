from unittest.mock import AsyncMock, patch
import pytest

# ============================================
# REGISTER TESTS
# ============================================

@patch("backend.app.services.auth_client.auth_client.create_organization_with_admin", new_callable=AsyncMock)
def test_register_success(mock_register, client):
    """Test successful user registration"""
    mock_register.return_value = {
        "organization": {"id": 1, "name": "Test Company", "slug": "test-company"},
        "admin_user": {
            "id": 1,
            "email": "newuser@test.com",
            "first_name": "Test",
            "last_name": "User"
        }
    }

    response = client.post(
        "/auth/register",
        json={
            "organization_name": "Test Company",
            "slug": "test-company",
            "domain": "test.com",
            "cnpj": "12345678901234",
            "address_street": "Test St",
            "address_city": "Test City",
            "address_state": "SP",
            "address_country": "Brazil",
            "address_postal_code": "12345-678",
            "admin_email": "newuser@test.com",
            "admin_password": "password123",
            "admin_first_name": "Test",
            "admin_last_name": "User"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert "organization" in body
    assert body["admin_user"]["email"] == "newuser@test.com"


@patch("backend.app.services.auth_client.auth_client.create_organization_with_admin", new_callable=AsyncMock)
def test_register_duplicate_email(mock_register, client):
    """Test registration with duplicate email"""
    from backend.app.core.exceptions import AuthServiceError

    mock_register.side_effect = AuthServiceError(
        message="Email já está cadastrado",
        status_code=400
    )

    response = client.post(
        "/auth/register",
        json={
            "organization_name": "Test Company",
            "cnpj": "12345678901234",
            "address_street": "Test St",
            "address_city": "Test City",
            "address_state": "SP",
            "address_country": "Brazil",
            "address_postal_code": "12345-678",
            "admin_email": "duplicate@test.com",
            "admin_password": "password123",
            "admin_first_name": "Test",
            "admin_last_name": "User"
        }
    )

    assert response.status_code == 400


# ============================================
# WEB LOGIN TESTS
# ============================================

@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_success_sets_cookies(mock_login, client):
    """Test successful web login sets HttpOnly cookies"""
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": "user-123"},
        "tokens": {
            "access_token": "mock-access-token-web",
            "csrf_token": "mock-csrf-token-web"
        }
    }

    response = client.post(
        "/auth/login/web",
        json={"email": "web@test.com", "password": "password123"}
    )

    assert response.status_code == 200
    body = response.json()

    # Tokens should NOT be in body (security)
    assert body["access_token"] is None
    assert body["csrf_token"] is None
    assert body["message"] == "Login realizado com sucesso"

    # Cookies SHOULD be set
    assert "session_token" in response.cookies
    assert response.cookies["session_token"] == "mock-access-token-web"
    assert "csrf_token" in response.cookies
    assert response.cookies["csrf_token"] == "mock-csrf-token-web"

    # Verify auth_client.login was called with correct params
    mock_login.assert_called_once_with(
        email="web@test.com",
        password="password123",
        client_type="web"
    )


@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_2fa_no_cookies(mock_login, client):
    """Test web login with 2FA does NOT set cookies yet"""
    mock_login.return_value = {
        "data": {"requires_2fa": True, "user_id": "user-123"},
        "tokens": {"access_token": None, "csrf_token": None}
    }

    response = client.post(
        "/auth/login/web",
        json={"email": "2fa@test.com", "password": "password123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["requires_2fa"] == True
    assert body["user_id"] == "user-123"
    assert "session_token" not in response.cookies
    assert "csrf_token" not in response.cookies


@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_invalid_email(mock_login, client):
    """Test web login with non-existent email"""
    from backend.app.core.exceptions import AuthenticationError

    mock_login.side_effect = AuthenticationError(
        message="Invalid credentials"
    )

    response = client.post(
        "/auth/login/web",
        json={
            "email": "nonexistent@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401


@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_invalid_password(mock_login, client):
    """Test web login with wrong password"""
    from backend.app.core.exceptions import AuthenticationError

    mock_login.side_effect = AuthenticationError(
        message="Invalid credentials"
    )

    response = client.post(
        "/auth/login/web",
        json={
            "email": "web@test.com",
            "password": "wrong123"
        }
    )

    assert response.status_code == 401


# ============================================
# DESKTOP LOGIN TESTS
# ============================================

@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_desktop_success(mock_login, client):
    """Test successful desktop login - should return access token without cookies"""
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": None},
        "tokens": {
            "access_token": "mock-access-token-desktop",
            "csrf_token": None
        }
    }

    response = client.post(
        "/auth/login/desktop",
        json={
            "email": "desktop@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    body = response.json()

    # Check LoginResponse structure
    assert body["message"] == "Login realizado com sucesso"
    assert body["requires_2fa"] == False
    assert body["access_token"] == "mock-access-token-desktop"
    assert body["csrf_token"] is None
    assert body["user_id"] is None

    # Verify NO cookies were set for desktop
    assert "session_token" not in response.cookies
    assert "csrf_token" not in response.cookies

    # Verify auth_client.login was called with desktop client type
    mock_login.assert_called_once_with(
        email="desktop@test.com",
        password="password123",
        client_type="desktop"
    )


@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_desktop_invalid_credentials(mock_login, client):
    """Test desktop login with invalid credentials"""
    from backend.app.core.exceptions import AuthenticationError

    mock_login.side_effect = AuthenticationError(
        message="Invalid credentials"
    )

    response = client.post(
        "/auth/login/desktop",
        json={
            "email": "desktop@test.com",
            "password": "wrong123"
        }
    )

    assert response.status_code == 401


@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_desktop_with_2fa(mock_login, client):
    """Test desktop login when 2FA is required"""
    mock_login.return_value = {
        "data": {
            "requires_2fa": True,
            "user_id": "mock-user-id-123"
        },
        "tokens": {
            "access_token": None,
            "csrf_token": None
        }
    }

    response = client.post(
        "/auth/login/desktop",
        json={
            "email": "desktop2fa@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    body = response.json()

    assert body["requires_2fa"] == True
    assert body["user_id"] == "mock-user-id-123"
    assert body["access_token"] is None
    assert body["csrf_token"] is None
    assert "Codigo 2FA" in body["message"]


# ============================================
# /ME ENDPOINT TESTS (WEB - COOKIE AUTHENTICATION)
# ============================================

@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_with_cookie_authentication(mock_proxy, client):
    """Test /me endpoint reads session from cookie"""
    mock_proxy.return_value = {
        "id": "user-123",
        "email": "web@test.com",
        "first_name": "Test",
        "last_name": "User"
    }

    response = client.get(
        "/auth/me",
        cookies={"session_token": "mock-session-token"},
        headers={"X-CSRF-Token": "mock-csrf-token"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "web@test.com"

    # Verify proxy was called with Authorization header
    mock_proxy.assert_called_once()
    call_kwargs = mock_proxy.call_args.kwargs
    assert "headers" in call_kwargs
    assert "Authorization" in call_kwargs["headers"]
    assert call_kwargs["headers"]["Authorization"] == "Bearer mock-session-token"


def test_me_without_cookie_returns_401(client):
    """Test /me endpoint returns 401 when no session cookie"""
    response = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": "mock-csrf"}
    )

    assert response.status_code == 401
    assert "Nao autenticado" in response.json()["detail"]


# ============================================
# /ME ENDPOINT TESTS (DESKTOP) - REMOVED
# ============================================
# Desktop clients do not use the /me endpoint via this API.
# Desktop authentication is handled differently.


# ============================================
# LOGOUT TESTS (COOKIE-BASED)
# ============================================

@patch("backend.app.services.auth_client.auth_client.logout", new_callable=AsyncMock)
def test_logout_reads_cookie_and_clears(mock_logout, client):
    """Test logout reads session from cookie and clears cookies"""
    mock_logout.return_value = True

    response = client.post(
        "/auth/logout",
        cookies={"session_token": "mock-session-token", "csrf_token": "mock-csrf"}
    )

    assert response.status_code == 200
    assert "Logout realizado com sucesso" in response.json()["message"]

    # Verify logout was called with correct token
    mock_logout.assert_called_once_with("mock-session-token")


@patch("backend.app.services.auth_client.auth_client.logout", new_callable=AsyncMock)
def test_logout_without_cookie_still_succeeds(mock_logout, client):
    """Test logout succeeds even without session cookie"""
    response = client.post("/auth/logout")

    assert response.status_code == 200
    # logout should NOT be called since no token
    mock_logout.assert_not_called()


# ============================================
# INTEGRATION TEST - FULL COOKIE AUTH FLOW
# ============================================

@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
@patch("backend.app.services.auth_client.auth_client.logout", new_callable=AsyncMock)
def test_full_cookie_auth_flow(mock_logout, mock_proxy, mock_login, client):
    """Test complete authentication flow with cookies"""
    # 1. Login
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": "user-123"},
        "tokens": {"access_token": "session-abc", "csrf_token": "csrf-xyz"}
    }

    login_response = client.post(
        "/auth/login/web",
        json={"email": "test@test.com", "password": "pass123"}
    )
    assert login_response.status_code == 200
    session_token = login_response.cookies.get("session_token")
    csrf_token = login_response.cookies.get("csrf_token")
    assert session_token == "session-abc"
    assert csrf_token == "csrf-xyz"

    # 2. Access /me with cookies
    mock_proxy.return_value = {"id": "user-123", "email": "test@test.com"}

    me_response = client.get(
        "/auth/me",
        cookies={"session_token": session_token},
        headers={"X-CSRF-Token": csrf_token}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "test@test.com"

    # Verify Authorization header was constructed from cookie
    call_kwargs = mock_proxy.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "Bearer session-abc"

    # 3. Logout
    mock_logout.return_value = True
    logout_response = client.post(
        "/auth/logout",
        cookies={"session_token": session_token}
    )
    assert logout_response.status_code == 200
    mock_logout.assert_called_once_with("session-abc")


# ============================================
# DEBUG FLAG COOKIE SECURITY TESTS
# ============================================

@patch("backend.app.api.routes.auth.DEBUG", True)
@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_cookies_not_secure_in_debug_mode(mock_login, client):
    """Test cookies have secure=False when DEBUG=True (development)"""
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": "user-123"},
        "tokens": {
            "access_token": "mock-access-token",
            "csrf_token": "mock-csrf-token"
        }
    }

    response = client.post(
        "/auth/login/web",
        json={"email": "test@test.com", "password": "password123"}
    )

    assert response.status_code == 200

    # Parse Set-Cookie headers to check secure flag
    set_cookie_headers = response.headers.get_list("set-cookie")

    session_cookie = next(
        (h for h in set_cookie_headers if h.startswith("session_token=")), None
    )
    csrf_cookie = next(
        (h for h in set_cookie_headers if h.startswith("csrf_token=")), None
    )

    assert session_cookie is not None, "session_token cookie not found"
    assert csrf_cookie is not None, "csrf_token cookie not found"

    # In debug mode (DEBUG=True), secure flag should NOT be present
    assert "secure" not in session_cookie.lower(), \
        f"session_token should NOT have secure flag in debug mode: {session_cookie}"
    assert "secure" not in csrf_cookie.lower(), \
        f"csrf_token should NOT have secure flag in debug mode: {csrf_cookie}"


@patch("backend.app.api.routes.auth.DEBUG", False)
@patch("backend.app.services.auth_client.auth_client.login", new_callable=AsyncMock)
def test_login_web_cookies_secure_in_production_mode(mock_login, client):
    """Test cookies have secure=True when DEBUG=False (production)"""
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": "user-123"},
        "tokens": {
            "access_token": "mock-access-token",
            "csrf_token": "mock-csrf-token"
        }
    }

    response = client.post(
        "/auth/login/web",
        json={"email": "test@test.com", "password": "password123"}
    )

    assert response.status_code == 200

    # Parse Set-Cookie headers to check secure flag
    set_cookie_headers = response.headers.get_list("set-cookie")

    session_cookie = next(
        (h for h in set_cookie_headers if h.startswith("session_token=")), None
    )
    csrf_cookie = next(
        (h for h in set_cookie_headers if h.startswith("csrf_token=")), None
    )

    assert session_cookie is not None, "session_token cookie not found"
    assert csrf_cookie is not None, "csrf_token cookie not found"

    # In production mode (DEBUG=False), secure flag SHOULD be present
    assert "secure" in session_cookie.lower(), \
        f"session_token should have secure flag in production mode: {session_cookie}"
    assert "secure" in csrf_cookie.lower(), \
        f"csrf_token should have secure flag in production mode: {csrf_cookie}"
