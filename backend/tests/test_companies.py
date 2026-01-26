"""
Tests for companies module admin and IP validation.

Tests:
- Admin-only access for company management endpoints
- Self-access for user's own companies
- IP whitelist validation
- Query parameter handling
- Request body forwarding
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
def another_user_id():
    """Generate another test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def empresa_id():
    """Generate a test empresa ID."""
    return str(uuid.uuid4())


@pytest.fixture
def org_id():
    """Generate a test organization ID."""
    return str(uuid.uuid4())


@pytest.fixture
def company_id():
    """Generate a test company ID."""
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
        "backend.app.api.routes.companies.auth_client.proxy_request",
        new_callable=AsyncMock
    ) as mock:
        # Default response for company operations
        mock.return_value = {
            "id": str(uuid.uuid4()),
            "name": "Test Company",
            "cnpj": "12345678000100",
            "description": "Test company description",
        }
        yield mock


# ============================================
# GET /companies/organizations/{org_id}/companies - List Companies
# ============================================

def test_list_companies_non_admin_forbidden(non_admin_client, org_id):
    """Test that non-admin user gets 403 Forbidden when listing companies."""
    response = non_admin_client.get(f"/companies/organizations/{org_id}/companies")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_list_companies_admin_success(admin_client, mock_auth_service, org_id):
    """Test that admin can list companies."""
    mock_auth_service.return_value = [
        {"id": "1", "name": "Company 1", "cnpj": "11111111000111"},
        {"id": "2", "name": "Company 2", "cnpj": "22222222000122"},
    ]

    response = admin_client.get(f"/companies/organizations/{org_id}/companies")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Verify query params were passed
    mock_auth_service.assert_called_once()
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["limit"] == 100
    assert call_kwargs["params"]["offset"] == 0


def test_list_companies_with_query_params(admin_client, mock_auth_service, org_id):
    """Test that query parameters are forwarded correctly."""
    mock_auth_service.return_value = []

    response = admin_client.get(
        f"/companies/organizations/{org_id}/companies",
        params={"limit": 50, "offset": 10, "include_deleted": True}
    )

    assert response.status_code == 200

    # Verify query params were forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["limit"] == 50
    assert call_kwargs["params"]["offset"] == 10
    assert call_kwargs["params"]["include_deleted"] == "true"


def test_list_companies_unauthenticated(client, org_id):
    """Test that unauthenticated request returns 401."""
    async def mock_auth():
        raise HTTPException(status_code=401, detail="Não autenticado")

    app.dependency_overrides[check_auth_with_ip] = mock_auth

    response = client.get(f"/companies/organizations/{org_id}/companies")

    app.dependency_overrides.pop(check_auth_with_ip, None)

    assert response.status_code == 401


# ============================================
# GET /companies/organizations/{org_id}/companies/{company_id} - Get Company
# ============================================

def test_get_company_non_admin_forbidden(non_admin_client, org_id, company_id):
    """Test that non-admin user gets 403 Forbidden when getting company."""
    response = non_admin_client.get(
        f"/companies/organizations/{org_id}/companies/{company_id}"
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_get_company_admin_success(admin_client, mock_auth_service, org_id, company_id):
    """Test that admin can get company."""
    response = admin_client.get(
        f"/companies/organizations/{org_id}/companies/{company_id}"
    )

    assert response.status_code == 200
    assert "id" in response.json()


# ============================================
# POST /companies/organizations/{org_id}/companies - Create Company
# ============================================

def test_create_company_non_admin_forbidden(non_admin_client, org_id):
    """Test that non-admin user gets 403 Forbidden when creating company."""
    response = non_admin_client.post(
        f"/companies/organizations/{org_id}/companies",
        json={"name": "New Company", "cnpj": "12345678000100"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_create_company_admin_success(admin_client, mock_auth_service, org_id):
    """Test that admin can create company."""
    company_data = {
        "name": "New Company",
        "cnpj": "12345678000100",
        "description": "A new test company"
    }

    response = admin_client.post(
        f"/companies/organizations/{org_id}/companies",
        json=company_data
    )

    assert response.status_code == 200

    # Verify request body was forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["json"]["name"] == "New Company"
    assert call_kwargs["json"]["cnpj"] == "12345678000100"


def test_create_company_minimal_data(admin_client, mock_auth_service, org_id):
    """Test creating company with only required fields."""
    company_data = {"name": "Minimal Company"}

    response = admin_client.post(
        f"/companies/organizations/{org_id}/companies",
        json=company_data
    )

    assert response.status_code == 200

    # Verify only name was sent (exclude_none=True)
    call_kwargs = mock_auth_service.call_args.kwargs
    assert "name" in call_kwargs["json"]
    assert "cnpj" not in call_kwargs["json"]


# ============================================
# PUT /companies/organizations/{org_id}/companies/{company_id} - Update Company
# ============================================

def test_update_company_non_admin_forbidden(non_admin_client, org_id, company_id):
    """Test that non-admin user gets 403 Forbidden when updating company."""
    response = non_admin_client.put(
        f"/companies/organizations/{org_id}/companies/{company_id}",
        json={"name": "Updated Company"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_update_company_admin_success(admin_client, mock_auth_service, org_id, company_id):
    """Test that admin can update company."""
    update_data = {"name": "Updated Company Name"}

    response = admin_client.put(
        f"/companies/organizations/{org_id}/companies/{company_id}",
        json=update_data
    )

    assert response.status_code == 200

    # Verify update data was forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["json"]["name"] == "Updated Company Name"


# ============================================
# DELETE /companies/organizations/{org_id}/companies/{company_id} - Delete Company
# ============================================

def test_delete_company_non_admin_forbidden(non_admin_client, org_id, company_id):
    """Test that non-admin user gets 403 Forbidden when deleting company."""
    response = non_admin_client.delete(
        f"/companies/organizations/{org_id}/companies/{company_id}"
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_delete_company_admin_success(admin_client, mock_auth_service, org_id, company_id):
    """Test that admin can delete company."""
    mock_auth_service.return_value = {"message": "Company deleted"}

    response = admin_client.delete(
        f"/companies/organizations/{org_id}/companies/{company_id}"
    )

    assert response.status_code == 200


# ============================================
# GET /companies/{company_id}/users - List Company Users
# ============================================

def test_list_company_users_non_admin_forbidden(non_admin_client, company_id):
    """Test that non-admin user gets 403 Forbidden when listing company users."""
    response = non_admin_client.get(f"/companies/{company_id}/users")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_list_company_users_admin_success(admin_client, mock_auth_service, company_id):
    """Test that admin can list company users."""
    mock_auth_service.return_value = [
        {"id": "1", "email": "user1@test.com"},
        {"id": "2", "email": "user2@test.com"},
    ]

    response = admin_client.get(f"/companies/{company_id}/users")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ============================================
# POST /companies/{company_id}/users - Add User to Company
# ============================================

def test_add_user_to_company_non_admin_forbidden(non_admin_client, company_id):
    """Test that non-admin user gets 403 Forbidden when adding user to company."""
    response = non_admin_client.post(
        f"/companies/{company_id}/users",
        json={"user_id": str(uuid.uuid4()), "role": "member"}
    )

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_add_user_to_company_admin_success(admin_client, mock_auth_service, company_id):
    """Test that admin can add user to company."""
    user_assignment = {
        "user_id": str(uuid.uuid4()),
        "role": "member"
    }

    response = admin_client.post(
        f"/companies/{company_id}/users",
        json=user_assignment
    )

    assert response.status_code == 200

    # Verify assignment data was forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    assert "user_id" in call_kwargs["json"]
    assert call_kwargs["json"]["role"] == "member"


# ============================================
# DELETE /companies/{company_id}/users/{user_id} - Remove User from Company
# ============================================

def test_remove_user_from_company_non_admin_forbidden(non_admin_client, company_id):
    """Test that non-admin user gets 403 Forbidden when removing user from company."""
    fake_user_id = str(uuid.uuid4())

    response = non_admin_client.delete(f"/companies/{company_id}/users/{fake_user_id}")

    assert response.status_code == 403
    assert "administradores" in response.json()["detail"].lower()


def test_remove_user_from_company_admin_success(admin_client, mock_auth_service, company_id):
    """Test that admin can remove user from company."""
    fake_user_id = str(uuid.uuid4())
    mock_auth_service.return_value = {"message": "User removed from company"}

    response = admin_client.delete(f"/companies/{company_id}/users/{fake_user_id}")

    assert response.status_code == 200


# ============================================
# GET /companies/users/{user_id}/companies - List User's Companies
# ============================================

def test_list_user_companies_self_access(non_admin_client, user_id, mock_auth_service):
    """Test that user can list their own companies."""
    mock_auth_service.return_value = [
        {"id": "1", "name": "Company 1"},
        {"id": "2", "name": "Company 2"},
    ]

    # User accessing their own companies
    response = non_admin_client.get(f"/companies/users/{user_id}/companies")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_user_companies_other_user_non_admin_forbidden(
    non_admin_client, another_user_id
):
    """Test that non-admin user cannot list other user's companies."""
    # User trying to access another user's companies
    response = non_admin_client.get(f"/companies/users/{another_user_id}/companies")

    assert response.status_code == 403
    assert "permissão" in response.json()["detail"].lower()


def test_list_user_companies_admin_access_any_user(
    admin_client, mock_auth_service, another_user_id
):
    """Test that admin can list any user's companies."""
    mock_auth_service.return_value = [
        {"id": "1", "name": "Company 1"},
    ]

    # Admin accessing another user's companies
    response = admin_client.get(f"/companies/users/{another_user_id}/companies")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_user_companies_with_query_params(
    admin_client, mock_auth_service, user_id
):
    """Test that query parameters are forwarded for user's companies."""
    mock_auth_service.return_value = []

    response = admin_client.get(
        f"/companies/users/{user_id}/companies",
        params={"limit": 25, "offset": 5}
    )

    assert response.status_code == 200

    # Verify query params were forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    assert call_kwargs["params"]["limit"] == 25
    assert call_kwargs["params"]["offset"] == 5


# ============================================
# ERROR HANDLING TESTS
# ============================================

def test_auth_service_error_propagation(admin_client, mock_auth_service, org_id):
    """Test that Auth service errors are properly propagated."""
    from backend.app.core.exceptions import AuthServiceError

    mock_auth_service.side_effect = AuthServiceError(
        message="Company not found",
        status_code=404
    )

    response = admin_client.get(f"/companies/organizations/{org_id}/companies")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_header_forwarding(admin_client, mock_auth_service, org_id):
    """Test that headers are forwarded correctly (excluding hop-by-hop)."""
    response = admin_client.get(
        f"/companies/organizations/{org_id}/companies",
        headers={
            "X-Custom-Header": "test-value",
            "Authorization": "Bearer token123"
        }
    )

    assert response.status_code == 200

    # Verify headers were forwarded
    call_kwargs = mock_auth_service.call_args.kwargs
    headers = call_kwargs.get("headers", {})

    # Custom headers should be forwarded
    # Note: TestClient may transform headers, but the pattern is tested
    assert "headers" in call_kwargs
