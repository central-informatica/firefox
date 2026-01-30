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
def test_login_web_success(mock_login, client):
    """Test successful web login - should return access token and csrf token"""
    mock_login.return_value = {
        "data": {"requires_2fa": False, "user_id": None},
        "tokens": {
            "access_token": "mock-access-token-web",
            "csrf_token": "mock-csrf-token-web"
        }
    }

    response = client.post(
        "/auth/login/web",
        json={
            "email": "web@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    body = response.json()

    # Check LoginResponse structure
    assert body["message"] == "Login realizado com sucesso"
    assert body["requires_2fa"] == False
    assert body["access_token"] == "mock-access-token-web"
    assert body["csrf_token"] == "mock-csrf-token-web"
    assert body["user_id"] is None

    # Verify auth_client.login was called with correct params
    mock_login.assert_called_once_with(
        email="web@test.com",
        password="password123",
        client_type="web"
    )


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
# /ME ENDPOINT TESTS (WEB)
# ============================================

@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_web_authenticated(mock_proxy, client):
    """Test /me endpoint with valid WEB authentication"""
    mock_proxy.return_value = {
        "id": "user-123",
        "email": "web@test.com",
        "first_name": "Test",
        "last_name": "User"
    }

    response = client.get(
        "/auth/me",
        headers={
            "X-CSRF-Token": "mock-csrf-token",
            "Authorization": "Bearer mock-token"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "web@test.com"


@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_web_missing_csrf(mock_proxy, client):
    """Test /me endpoint without CSRF header"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="CSRF token missing",
        status_code=403
    )

    response = client.get("/auth/me")

    assert response.status_code == 403


@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_web_unauthenticated(mock_proxy, client):
    """Test /me endpoint without authentication"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="Unauthorized",
        status_code=401
    )

    response = client.get("/auth/me")

    assert response.status_code == 401


# ============================================
# /ME ENDPOINT TESTS (DESKTOP)
# ============================================

@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_desktop_authenticated(mock_proxy, client):
    """Test /me endpoint with valid DESKTOP authentication (Bearer token)"""
    mock_proxy.return_value = {
        "id": "user-456",
        "email": "desktop@test.com",
        "first_name": "Desktop",
        "last_name": "User"
    }

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer mock-desktop-token"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "desktop@test.com"


@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_desktop_invalid_token(mock_proxy, client):
    """Test /me endpoint with invalid Bearer token"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="Invalid token",
        status_code=401
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token"}
    )

    assert response.status_code == 401


@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_me_desktop_malformed_authorization(mock_proxy, client):
    """Test /me endpoint with malformed Authorization header"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="Invalid authorization format",
        status_code=401
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": "NotBearer token"}
    )

    assert response.status_code == 401


# ============================================
# LOGOUT TESTS (WEB)
# ============================================

@patch("backend.app.services.auth_client.auth_client.logout", new_callable=AsyncMock)
def test_logout_web_success(mock_logout, client):
    """Test successful web logout - should revoke token"""
    mock_logout.return_value = True

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer mock-session-token"}
    )

    assert response.status_code == 200
    assert "Logout realizado com sucesso" in response.json()["message"]

    mock_logout.assert_called_once()


# ============================================
# LOGOUT TESTS (DESKTOP)
# ============================================

@patch("backend.app.services.auth_client.auth_client.logout", new_callable=AsyncMock)
def test_logout_desktop_success(mock_logout, client):
    """Test successful desktop logout - should revoke token"""
    mock_logout.return_value = True

    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer mock-desktop-token"}
    )

    assert response.status_code == 200

    mock_logout.assert_called_once()


# ============================================
# TOKEN VALIDATION TESTS
# ============================================

@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_web_token_cannot_be_used_as_bearer(mock_proxy, client):
    """Test that WEB tokens cannot be used with Authorization header"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="Tipo de cliente inválido",
        status_code=401
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer web-session-token"}
    )

    assert response.status_code == 401
    body = response.json()
    assert "Tipo de cliente inválido" in body["detail"]


@patch("backend.app.services.auth_client.auth_client.proxy_request", new_callable=AsyncMock)
def test_desktop_token_cannot_be_used_in_cookie(mock_proxy, client):
    """Test that DESKTOP tokens cannot be used via cookies"""
    from backend.app.core.exceptions import AuthServiceError

    mock_proxy.side_effect = AuthServiceError(
        message="Tipo de cliente inválido",
        status_code=401
    )

    response = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": "fake-csrf"}
    )

    assert response.status_code == 401
    body = response.json()
    assert "Tipo de cliente inválido" in body["detail"]
