import json
from tests.factories.usuario_factory import criar_usuario

# ============================================
# REGISTER TESTS
# ============================================

def test_register_success(client, db_session):
    """Test successful user registration"""
    response = client.post(
        "/auth/register",
        json={
            "nome": "Test User",
            "email": "newuser@test.com",
            "senha": "password123",
            "telefone": "+5511999999999"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "newuser@test.com"
    assert body["nome"] == "Test User"
    assert "id" in body


def test_register_duplicate_email(client, db_session):
    """Test registration with duplicate email"""
    criar_usuario(db_session, email="duplicate@test.com")

    response = client.post(
        "/auth/register",
        json={
            "nome": "Test User",
            "email": "duplicate@test.com",
            "senha": "password123"
        }
    )

    assert response.status_code == 400
    assert "já está cadastrado" in response.json()["detail"]


# ============================================
# WEB LOGIN TESTS
# ============================================

def test_login_web_success(client, db_session):
    """Test successful web login - should return cookies"""
    criar_usuario(db_session, email="web@test.com", senha="password123")

    response = client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "password123"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "web@test.com"
    assert "id" in body

    # Check that cookies were set
    assert "session_token" in response.cookies
    assert "csrf_token" in response.cookies


def test_login_web_invalid_email(client, db_session):
    """Test web login with non-existent email"""
    response = client.post(
        "/auth/login-web",
        json={
            "email": "nonexistent@test.com",
            "senha": "password123"
        }
    )

    assert response.status_code == 403
    assert "credenciais não conferem" in response.json()["detail"]


def test_login_web_invalid_password(client, db_session):
    """Test web login with wrong password"""
    criar_usuario(db_session, email="web@test.com", senha="correct123")

    response = client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "wrong123"
        }
    )

    assert response.status_code == 403
    assert "credenciais não conferem" in response.json()["detail"]


# ============================================
# DESKTOP LOGIN TESTS
# ============================================

def test_login_desktop_success(client, db_session):
    """Test successful desktop login - should return access token"""
    criar_usuario(db_session, email="desktop@test.com", senha="password123")

    response = client.post(
        "/auth/login-desktop",
        json={
            "email": "desktop@test.com",
            "senha": "password123"
        }
    )

    assert response.status_code == 200
    body = response.json()

    # Check response structure
    assert "access_token" in body
    assert "token_type" in body
    assert body["token_type"] == "Bearer"
    assert "expires_in" in body
    assert body["expires_in"] == 900  # 15 minutes

    # Check user data
    assert "user" in body
    assert body["user"]["email"] == "desktop@test.com"

    # Verify token format (selector.validator)
    token = body["access_token"]
    assert "." in token
    parts = token.split(".")
    assert len(parts) == 2

    # Check that NO cookies were set for desktop
    assert "session_token" not in response.cookies
    assert "csrf_token" not in response.cookies


def test_login_desktop_invalid_credentials(client, db_session):
    """Test desktop login with invalid credentials"""
    criar_usuario(db_session, email="desktop@test.com", senha="correct123")

    response = client.post(
        "/auth/login-desktop",
        json={
            "email": "desktop@test.com",
            "senha": "wrong123"
        }
    )

    assert response.status_code == 403


# ============================================
# /ME ENDPOINT TESTS (WEB)
# ============================================

def test_me_web_authenticated(client, db_session):
    """Test /me endpoint with valid WEB authentication"""
    criar_usuario(db_session, email="web@test.com", senha="password123")

    # Login to get cookies
    login_response = client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "password123"
        }
    )

    csrf_token = login_response.cookies.get("csrf_token")

    # Call /me with cookies and CSRF header
    response = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "web@test.com"


def test_me_web_missing_csrf(client, db_session):
    """Test /me endpoint without CSRF header"""
    criar_usuario(db_session, email="web@test.com", senha="password123")

    # Login to get cookies
    client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "password123"
        }
    )

    # Call /me WITHOUT CSRF header
    response = client.get("/auth/me")

    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]


def test_me_web_unauthenticated(client):
    """Test /me endpoint without authentication"""
    response = client.get("/auth/me")

    assert response.status_code == 401


# ============================================
# /ME ENDPOINT TESTS (DESKTOP)
# ============================================

def test_me_desktop_authenticated(client, db_session):
    """Test /me endpoint with valid DESKTOP authentication (Bearer token)"""
    criar_usuario(db_session, email="desktop@test.com", senha="password123")

    # Login to get access token
    login_response = client.post(
        "/auth/login-desktop",
        json={
            "email": "desktop@test.com",
            "senha": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    # Call /me with Authorization header
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "desktop@test.com"


def test_me_desktop_invalid_token(client):
    """Test /me endpoint with invalid Bearer token"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token"}
    )

    assert response.status_code == 401


def test_me_desktop_malformed_authorization(client):
    """Test /me endpoint with malformed Authorization header"""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "NotBearer token"}
    )

    assert response.status_code == 401


# ============================================
# LOGOUT TESTS (WEB)
# ============================================

def test_logout_web_success(client, db_session):
    """Test successful web logout - should delete cookies and revoke token"""
    criar_usuario(db_session, email="web@test.com", senha="password123")

    # Login
    login_response = client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "password123"
        }
    )

    csrf_token = login_response.cookies.get("csrf_token")
    session_token = login_response.cookies.get("session_token")

    # Verify /me works before logout
    me_before = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": csrf_token}
    )
    assert me_before.status_code == 200

    # Logout
    logout_response = client.post(
        "/auth/logout",
        headers={"X-CSRF-Token": csrf_token}
    )

    assert logout_response.status_code == 200
    assert "Logout realizado com sucesso" in logout_response.json()["detail"]

    # Manually set the cookies back to test that the token was revoked
    # (logout deletes cookies, but we want to verify the token is actually revoked in DB)
    client.cookies.set("session_token", session_token)
    client.cookies.set("csrf_token", csrf_token)

    # Verify token is revoked - /me should fail with "revogado" message
    me_response = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": csrf_token}
    )

    assert me_response.status_code == 401
    assert "revogado" in me_response.json()["detail"].lower()


# ============================================
# LOGOUT TESTS (DESKTOP)
# ============================================

def test_logout_desktop_success(client, db_session):
    """Test successful desktop logout - should revoke token"""
    criar_usuario(db_session, email="desktop@test.com", senha="password123")

    # Login
    login_response = client.post(
        "/auth/login-desktop",
        json={
            "email": "desktop@test.com",
            "senha": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    # Logout
    logout_response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert logout_response.status_code == 200

    # Verify token is revoked - /me should fail
    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert me_response.status_code == 401
    assert "revogado" in me_response.json()["detail"].lower()


# ============================================
# TOKEN VALIDATION TESTS
# ============================================

def test_web_token_cannot_be_used_as_bearer(client, db_session):
    """Test that WEB tokens cannot be used with Authorization header"""
    criar_usuario(db_session, email="web@test.com", senha="password123")

    # Login via web
    login_response = client.post(
        "/auth/login-web",
        json={
            "email": "web@test.com",
            "senha": "password123"
        }
    )

    # Extract session token from cookies
    session_token = login_response.cookies.get("session_token")

    # Try to use it as Bearer token
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {session_token}"}
    )

    assert response.status_code == 401
    assert "Tipo de cliente inválido" in response.json()["detail"]


def test_desktop_token_cannot_be_used_in_cookie(client, db_session):
    """Test that DESKTOP tokens cannot be used via cookies"""
    criar_usuario(db_session, email="desktop@test.com", senha="password123")

    # Login via desktop
    login_response = client.post(
        "/auth/login-desktop",
        json={
            "email": "desktop@test.com",
            "senha": "password123"
        }
    )

    access_token = login_response.json()["access_token"]

    # Manually set the desktop token as a cookie
    client.cookies.set("session_token", access_token)
    client.cookies.set("csrf_token", "fake-csrf")

    # Try to use it as web token
    response = client.get(
        "/auth/me",
        headers={"X-CSRF-Token": "fake-csrf"}
    )

    assert response.status_code == 401
    assert "Tipo de cliente inválido" in response.json()["detail"]
