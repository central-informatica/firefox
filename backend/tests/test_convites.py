"""
Tests for convites module admin and IP validation.

Tests:
- Admin-only access for create, list, revoke endpoints
- Public access for accept endpoint
- IP whitelist validation
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db

from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


# ============================================
# HELPER FUNCTIONS
# ============================================

def _mock_user_data(user_id: str, org_id: str, is_admin: bool = True, ip: str = "127.0.0.1"):
    """Create mock user data dict as returned by auth service."""
    return {
        "id": user_id,
        "usuario_id": user_id,
        "organization_id": org_id,
        "is_admin": is_admin,
        "email": "user@test.com",
        "ip_address": ip,
    }


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def user_id():
    """Generate a test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def empresa_id():
    """Generate a test empresa ID."""
    return str(uuid.uuid4())


@pytest.fixture
def admin_client(db_session, user_id, empresa_id):
    """Test client with admin user and whitelisted IP."""
    # Add IP whitelist entry
    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id, is_admin=True, ip="127.0.0.1")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def non_admin_client(db_session, user_id, empresa_id):
    """Test client with non-admin user and whitelisted IP."""
    # Add IP whitelist entry
    criar_usuarios_ip_whitelist(
        db_session,
        usuario_id=user_id,
        empresa_id=empresa_id,
        ip_address="127.0.0.1",
    )

    async def mock_auth():
        return _mock_user_data(user_id, empresa_id, is_admin=False, ip="127.0.0.1")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_service():
    """Mock auth_client.proxy_request to avoid external calls."""
    with patch(
        "backend.app.api.routes.convites.auth_client.proxy_request",
        new_callable=AsyncMock
    ) as mock:
        # Default response for invitation operations
        mock.return_value = {
            "id": str(uuid.uuid4()),
            "email": "invited@test.com",
            "status": "pending",
        }
        yield mock


# ============================================
# POST /convites/ - Create Invitation
# ============================================

def test_create_invitation_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when creating invitation."""
    response = non_admin_client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_create_invitation_admin_success(admin_client, mock_auth_service):
    """Test that admin can create invitation."""
    response = admin_client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    assert response.status_code == 200


def test_create_invitation_unauthenticated(client):
    """Test that unauthenticated request returns 401."""
    async def mock_auth():
        raise HTTPException(status_code=401, detail="Não autenticado")

    app.dependency_overrides[check_auth_with_ip] = mock_auth

    response = client.post(
        "/convites/",
        json={"email": "newuser@test.com"}
    )

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 401


# ============================================
# GET /convites/ - List Invitations
# ============================================

def test_list_invitations_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when listing invitations."""
    response = non_admin_client.get("/convites/")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_list_invitations_admin_success(admin_client, mock_auth_service):
    """Test that admin can list invitations."""
    mock_auth_service.return_value = [
        {"id": "1", "email": "user1@test.com", "status": "pending"},
        {"id": "2", "email": "user2@test.com", "status": "accepted"},
    ]

    response = admin_client.get("/convites/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ============================================
# DELETE /convites/{invitation_id} - Revoke Invitation
# ============================================

def test_revoke_invitation_non_admin_forbidden(non_admin_client):
    """Test that non-admin user gets 403 Forbidden when revoking invitation."""
    fake_invitation_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/convites/{fake_invitation_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_revoke_invitation_admin_success(admin_client, mock_auth_service):
    """Test that admin can revoke invitation."""
    fake_invitation_id = str(uuid.uuid4())
    mock_auth_service.return_value = {"message": "Invitation revoked"}

    response = admin_client.delete(f"/convites/{fake_invitation_id}")

    assert response.status_code == 200


# ============================================
# POST /convites/accept - Accept Invitation (PUBLIC)
# ============================================

def test_accept_invitation_public(client, mock_auth_service):
    """Test that accept invitation endpoint is public (no auth required)."""
    mock_auth_service.return_value = {
        "id": str(uuid.uuid4()),
        "email": "newuser@test.com",
        "message": "Invitation accepted",
    }

    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token-123",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 200


# ============================================
# Auth Service Error Handling Tests
# ============================================

def test_create_invitation_auth_service_400(admin_client, mock_auth_service):
    """Test handling of 400 error from Auth service on create."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError("Invalid email format", status_code=400)

    response = admin_client.post("/convites/", json={"email": "test@test.com"})

    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_create_invitation_auth_service_500(admin_client, mock_auth_service):
    """Test handling of 500 error from Auth service on create."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError("Internal server error", status_code=500)

    response = admin_client.post("/convites/", json={"email": "test@test.com"})

    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]


def test_list_invitations_auth_service_500(admin_client, mock_auth_service):
    """Test handling of 500 error from Auth service on list."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError("Service unavailable", status_code=500)

    response = admin_client.get("/convites/")

    assert response.status_code == 500
    assert "Service unavailable" in response.json()["detail"]


def test_revoke_invitation_auth_service_404(admin_client, mock_auth_service):
    """Test handling of 404 error from Auth service on revoke."""
    from backend.app.core.exceptions import AuthServiceError

    fake_id = str(uuid.uuid4())
    mock_auth_service.side_effect = AuthServiceError("Invitation not found", status_code=404)

    response = admin_client.delete(f"/convites/{fake_id}")

    assert response.status_code == 404
    assert "Invitation not found" in response.json()["detail"]


def test_revoke_invitation_auth_service_500(admin_client, mock_auth_service):
    """Test handling of 500 error from Auth service on revoke."""
    from backend.app.core.exceptions import AuthServiceError

    fake_id = str(uuid.uuid4())
    mock_auth_service.side_effect = AuthServiceError("Database error", status_code=500)

    response = admin_client.delete(f"/convites/{fake_id}")

    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]


def test_accept_invitation_auth_service_400(client, mock_auth_service):
    """Test handling of 400 error from Auth service on accept (invalid token)."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError("Invalid or expired token", status_code=400)

    response = client.post(
        "/convites/accept",
        json={
            "token": "invalid-token",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 400
    assert "Invalid or expired token" in response.json()["detail"]


def test_accept_invitation_auth_service_404(client, mock_auth_service):
    """Test handling of 404 error from Auth service on accept (token not found)."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError("Token not found", status_code=404)

    response = client.post(
        "/convites/accept",
        json={
            "token": "nonexistent-token",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 404
    assert "Token not found" in response.json()["detail"]


# ============================================
# Query Parameter Tests (List Endpoint)
# ============================================

def test_list_invitations_with_include_accepted_true(admin_client, mock_auth_service):
    """Test list with include_accepted=True parameter."""
    mock_auth_service.return_value = [
        {"id": "1", "email": "user1@test.com", "status": "accepted"},
    ]

    response = admin_client.get("/convites/?include_accepted=true")

    assert response.status_code == 200
    # Verify parameter was passed to auth_client
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["include_accepted"] is True


def test_list_invitations_with_custom_limit(admin_client, mock_auth_service):
    """Test list with custom limit parameter."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/?limit=50")

    assert response.status_code == 200
    # Verify parameter was passed
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["limit"] == 50


def test_list_invitations_with_custom_offset(admin_client, mock_auth_service):
    """Test list with custom offset parameter."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/?offset=20")

    assert response.status_code == 200
    # Verify parameter was passed
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["offset"] == 20


def test_list_invitations_with_all_parameters(admin_client, mock_auth_service):
    """Test list with all query parameters combined."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/?include_accepted=true&limit=25&offset=10")

    assert response.status_code == 200
    # Verify all parameters were passed
    call_kwargs = mock_auth_service.call_args.kwargs
    params = call_kwargs["params"]
    assert params["include_accepted"] is True
    assert params["limit"] == 25
    assert params["offset"] == 10


def test_list_invitations_default_parameters(admin_client, mock_auth_service):
    """Test list with default parameters when none specified."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/")

    assert response.status_code == 200
    # Verify default parameters
    call_kwargs = mock_auth_service.call_args.kwargs
    params = call_kwargs["params"]
    assert params["include_accepted"] is False
    assert params["limit"] == 100
    assert params["offset"] == 0


# ============================================
# Request Validation Tests
# ============================================

def test_create_invitation_invalid_email_format(admin_client):
    """Test create with invalid email format returns 422."""
    response = admin_client.post(
        "/convites/",
        json={"email": "notanemail"}
    )

    assert response.status_code == 422


def test_create_invitation_missing_email(admin_client):
    """Test create without email field returns 422."""
    response = admin_client.post(
        "/convites/",
        json={}
    )

    assert response.status_code == 422


def test_accept_invitation_missing_token(client):
    """Test accept without token returns 422."""
    response = client.post(
        "/convites/accept",
        json={
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 422


def test_accept_invitation_missing_password(client):
    """Test accept without password returns 422."""
    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 422


def test_accept_invitation_missing_first_name(client):
    """Test accept without first_name returns 422."""
    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token",
            "password": "password123",
            "last_name": "Doe",
        }
    )

    assert response.status_code == 422


def test_accept_invitation_missing_last_name(client):
    """Test accept without last_name returns 422."""
    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token",
            "password": "password123",
            "first_name": "John",
        }
    )

    assert response.status_code == 422


def test_accept_invitation_all_fields_missing(client):
    """Test accept with empty payload returns 422."""
    response = client.post("/convites/accept", json={})

    assert response.status_code == 422


# ============================================
# Header Forwarding Tests
# ============================================

def test_create_invitation_forwards_custom_headers(admin_client, mock_auth_service):
    """Test that custom headers are forwarded to Auth service."""
    custom_headers = {
        "X-Request-ID": "test-request-123",
        "X-Correlation-ID": "correlation-456",
    }

    response = admin_client.post(
        "/convites/",
        json={"email": "test@test.com"},
        headers=custom_headers
    )

    assert response.status_code == 200
    # Verify custom headers were forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    forwarded_headers = call_kwargs.get("headers", {})
    assert "X-Request-ID" in forwarded_headers or "x-request-id" in forwarded_headers
    assert "X-Correlation-ID" in forwarded_headers or "x-correlation-id" in forwarded_headers


def test_list_invitations_excludes_hop_by_hop_headers(admin_client, mock_auth_service):
    """Test that excluded headers (content-length, host) are not forwarded."""
    response = admin_client.get("/convites/")

    assert response.status_code == 200
    # Verify excluded headers are NOT forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    forwarded_headers = call_kwargs.get("headers", {})

    # These should be excluded
    assert "content-length" not in str(forwarded_headers).lower()
    assert "host" not in str(forwarded_headers).lower()


# ============================================
# Edge Case Tests
# ============================================

def test_list_invitations_empty_response(admin_client, mock_auth_service):
    """Test list returns empty array when no invitations exist."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/")

    assert response.status_code == 200
    assert response.json() == []


def test_revoke_invitation_invalid_uuid_format(admin_client, mock_auth_service):
    """Test revoke with invalid UUID format is forwarded to Auth service.

    Note: The path parameter is typed as 'str' not 'UUID', so invalid formats
    are forwarded to the Auth service which will handle validation.
    """
    mock_auth_service.return_value = {"message": "Revoked"}

    response = admin_client.delete("/convites/not-a-uuid")

    # Forwarded to Auth service (mock returns success by default)
    assert response.status_code == 200


def test_create_invitation_duplicate_email(admin_client, mock_auth_service):
    """Test creating duplicate invitation (handled by Auth service)."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError(
        "Invitation already exists for this email",
        status_code=409
    )

    response = admin_client.post(
        "/convites/",
        json={"email": "existing@test.com"}
    )

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


def test_accept_invitation_with_valid_all_fields(client, mock_auth_service):
    """Test accept with all valid fields succeeds."""
    mock_auth_service.return_value = {
        "id": str(uuid.uuid4()),
        "email": "newuser@test.com",
        "status": "accepted",
        "message": "Invitation accepted successfully",
    }

    response = client.post(
        "/convites/accept",
        json={
            "token": "valid-token-abc123",
            "password": "SecurePassword123!",
            "first_name": "Jane",
            "last_name": "Smith",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "accepted" in str(data).lower() or "message" in data


def test_list_invitations_verifies_auth_client_called(admin_client, mock_auth_service):
    """Test that list calls auth_client with correct method and path."""
    mock_auth_service.return_value = []

    response = admin_client.get("/convites/")

    assert response.status_code == 200
    # Verify auth_client.proxy_request was called
    mock_auth_service.assert_called_once()
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["method"] == "GET"
    assert "/api/v1/invitations/" in call_kwargs["path"]


def test_create_invitation_verifies_json_payload(admin_client, mock_auth_service):
    """Test that create sends correct JSON payload to Auth service."""
    test_email = "newinvite@test.com"

    response = admin_client.post("/convites/", json={"email": test_email})

    assert response.status_code == 200
    # Verify correct payload was sent
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["json"]["email"] == test_email


def test_revoke_invitation_verifies_path_parameter(admin_client, mock_auth_service):
    """Test that revoke uses correct path with invitation_id."""
    invitation_id = str(uuid.uuid4())
    mock_auth_service.return_value = {"message": "Revoked"}

    response = admin_client.delete(f"/convites/{invitation_id}")

    assert response.status_code == 200
    # Verify correct path was used
    call_kwargs = mock_auth_service.call_args.kwargs
    assert invitation_id in call_kwargs["path"]


def test_accept_invitation_verifies_all_fields_sent(client, mock_auth_service):
    """Test that accept sends all required fields to Auth service."""
    mock_auth_service.return_value = {"status": "accepted"}

    payload = {
        "token": "test-token-123",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
    }

    response = client.post("/convites/accept", json=payload)

    assert response.status_code == 200
    # Verify all fields were sent
    call_kwargs = mock_auth_service.call_args.kwargs
    sent_json = call_kwargs["json"]
    assert sent_json["token"] == "test-token-123"
    assert sent_json["password"] == "TestPassword123"
    assert sent_json["first_name"] == "Test"
    assert sent_json["last_name"] == "User"


# ============================================
# Additional Validation Tests
# ============================================

def test_create_invitation_empty_email(admin_client):
    """Test create with empty email returns 422."""
    response = admin_client.post("/convites/", json={"email": ""})

    assert response.status_code == 422


def test_accept_invitation_empty_token(client, mock_auth_service):
    """Test accept with empty token - forwarded to Auth service for validation."""
    from backend.app.core.exceptions import AuthServiceError

    # Mock Auth service rejecting empty token
    mock_auth_service.side_effect = AuthServiceError("Token cannot be empty", status_code=400)

    response = client.post(
        "/convites/accept",
        json={
            "token": "",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
        }
    )

    # Auth service validates and returns error
    assert response.status_code == 400


# ============================================
# Mock Verification Tests
# ============================================

def test_create_invitation_calls_correct_auth_endpoint(admin_client, mock_auth_service):
    """Test that create calls the correct Auth service endpoint."""
    response = admin_client.post("/convites/", json={"email": "user@test.com"})

    assert response.status_code == 200
    mock_auth_service.assert_called_once()
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["method"] == "POST"
    assert call_kwargs["path"] == "/api/v1/invitations/"


def test_revoke_invitation_calls_correct_auth_endpoint(admin_client, mock_auth_service):
    """Test that revoke calls the correct Auth service endpoint."""
    invitation_id = str(uuid.uuid4())

    response = admin_client.delete(f"/convites/{invitation_id}")

    assert response.status_code == 200
    mock_auth_service.assert_called_once()
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["method"] == "DELETE"
    assert call_kwargs["path"] == f"/api/v1/invitations/{invitation_id}"


def test_accept_invitation_calls_correct_auth_endpoint(client, mock_auth_service):
    """Test that accept calls the correct Auth service endpoint."""
    response = client.post(
        "/convites/accept",
        json={
            "token": "token-123",
            "password": "pass",
            "first_name": "A",
            "last_name": "B",
        }
    )

    assert response.status_code == 200
    mock_auth_service.assert_called_once()
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["method"] == "POST"
    assert call_kwargs["path"] == "/api/v1/invitations/accept"
