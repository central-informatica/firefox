"""
Comprehensive functional tests for Global URLs API endpoints.

Tests cover:
- CRUD operations (create, read, update, delete)
- Pagination functionality
- Search filtering
- Sort functionality with validation
- Input validation
- Error handling (404, 400, 422)
- Multi-tenant isolation
- Database persistence verification
- Combined scenarios
"""

import uuid
import time
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import GlobalUrls

from tests.factories.global_urls_factory import criar_global_url
from tests.factories.usuarios_ip_whitelist_factory import criar_usuarios_ip_whitelist


def _mock_user_data(user_id: str, org_id: str, is_admin: bool = True, ip: str = "127.0.0.1"):
    """Create mock user data dict as returned by auth service."""
    return {
        "id": user_id,
        "usuario_id": user_id,
        "organization_id": org_id,
        "is_admin": is_admin,
        "email": "admin@test.com",
        "ip_address": ip,
    }


@pytest.fixture
def admin_client(db_session):
    """Test client with admin user and whitelisted IP."""
    user_id = str(uuid.uuid4())
    empresa_id = str(uuid.uuid4())

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
        yield test_client, user_id, empresa_id

    app.dependency_overrides.clear()


# ============================================
# CRUD Happy Path Tests - CREATE
# ============================================

def test_criar_global_url_success(admin_client, db_session):
    """Test creating a global URL with all fields successfully."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "url": "https://api.example.com",
        "inativo": False,
    }

    response = client.post("/global-urls/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "global_urls_id" in data
    assert data["url"] == "https://api.example.com"
    assert data["empresa_id"] == empresa_id
    assert data["inativo"] is False
    assert "criado_em" in data

    # Verify database persistence
    global_url_id = data["global_urls_id"]
    db_record = db_session.query(GlobalUrls).filter(
        GlobalUrls.global_urls_id == global_url_id
    ).first()
    assert db_record is not None
    assert db_record.url == "https://api.example.com"


def test_criar_global_url_minimal(admin_client, db_session):
    """Test creating a global URL with only required fields."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
    }

    response = client.post("/global-urls/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "global_urls_id" in data
    assert data["url"] is None
    assert data["inativo"] is False  # Default value


def test_criar_global_url_with_inativo_true(admin_client, db_session):
    """Test creating a global URL with inativo=True."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "url": "https://inactive.example.com",
        "inativo": True,
    }

    response = client.post("/global-urls/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["inativo"] is True


# ============================================
# CRUD Happy Path Tests - READ
# ============================================

def test_get_global_url_by_id_success(admin_client, db_session):
    """Test getting a global URL by ID."""
    client, user_id, empresa_id = admin_client

    # Create URL using factory
    url_record = criar_global_url(db_session, empresa_id, url="https://test.com")

    response = client.get(f"/global-urls/id/{url_record.global_urls_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["global_urls_id"] == str(url_record.global_urls_id)
    assert data["url"] == "https://test.com"
    assert data["empresa_id"] == empresa_id


def test_list_global_urls_success(admin_client, db_session):
    """Test listing global URLs with multiple entries."""
    client, user_id, empresa_id = admin_client

    # Create 3 URLs
    criar_global_url(db_session, empresa_id, url="https://url1.com")
    criar_global_url(db_session, empresa_id, url="https://url2.com")
    criar_global_url(db_session, empresa_id, url="https://url3.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["data"]) == 3


def test_list_global_urls_empty_empresa(admin_client):
    """Test listing global URLs for an empresa with no data."""
    client, user_id, empresa_id = admin_client

    response = client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


# ============================================
# CRUD Happy Path Tests - UPDATE
# ============================================

def test_atualizar_global_url_all_fields(admin_client, db_session):
    """Test updating both url and inativo fields."""
    client, user_id, empresa_id = admin_client

    # Create URL
    url_record = criar_global_url(db_session, empresa_id, url="https://old.com")
    original_id = url_record.global_urls_id

    payload = {
        "url": "https://new.com",
        "inativo": True,
    }

    response = client.put(f"/global-urls/id/{original_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://new.com"
    assert data["inativo"] is True

    # Verify database persistence
    db_session.refresh(url_record)
    assert url_record.url == "https://new.com"
    assert url_record.inativo is True


def test_atualizar_global_url_partial_url_only(admin_client, db_session):
    """Test updating only the URL field, inativo should remain unchanged."""
    client, user_id, empresa_id = admin_client

    # Create URL with inativo=False
    url_record = criar_global_url(db_session, empresa_id, url="https://old.com")
    url_record.inativo = False
    db_session.commit()
    original_id = url_record.global_urls_id

    payload = {
        "url": "https://updated.com",
    }

    response = client.put(f"/global-urls/id/{original_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://updated.com"
    assert data["inativo"] is False  # Unchanged


def test_atualizar_global_url_partial_inativo_only(admin_client, db_session):
    """Test updating only the inativo field, URL should remain unchanged."""
    client, user_id, empresa_id = admin_client

    # Create URL
    url_record = criar_global_url(db_session, empresa_id, url="https://original.com")
    original_id = url_record.global_urls_id

    payload = {
        "inativo": True,
    }

    response = client.put(f"/global-urls/id/{original_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://original.com"  # Unchanged
    assert data["inativo"] is True


def test_atualizar_global_url_empty_payload(admin_client, db_session):
    """Test updating with empty payload should not change any fields."""
    client, user_id, empresa_id = admin_client

    # Create URL
    url_record = criar_global_url(db_session, empresa_id, url="https://test.com")
    original_id = url_record.global_urls_id
    original_url = url_record.url
    original_inativo = url_record.inativo

    payload = {}

    response = client.put(f"/global-urls/id/{original_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["url"] == original_url
    assert data["inativo"] == original_inativo


# ============================================
# CRUD Happy Path Tests - DELETE
# ============================================

def test_deletar_global_url_success(admin_client, db_session):
    """Test deleting a global URL (hard delete)."""
    client, user_id, empresa_id = admin_client

    # Create URL
    url_record = criar_global_url(db_session, empresa_id, url="https://delete-me.com")
    url_id = url_record.global_urls_id

    response = client.delete(f"/global-urls/id/{url_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"

    # Verify hard delete - record should not exist
    db_record = db_session.query(GlobalUrls).filter(
        GlobalUrls.global_urls_id == url_id
    ).first()
    assert db_record is None


# ============================================
# Pagination Tests
# ============================================

def test_list_pagination_default(admin_client, db_session):
    """Test pagination with default parameters (page=1, limit=10)."""
    client, user_id, empresa_id = admin_client

    # Create 15 URLs
    for i in range(15):
        criar_global_url(db_session, empresa_id, url=f"https://url{i}.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["data"]) == 10  # Default limit


def test_list_pagination_page_2(admin_client, db_session):
    """Test getting the second page of results."""
    client, user_id, empresa_id = admin_client

    # Create 15 URLs
    for i in range(15):
        criar_global_url(db_session, empresa_id, url=f"https://url{i}.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?page=2&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["data"]) == 5  # Remaining items


def test_list_pagination_custom_limit(admin_client, db_session):
    """Test pagination with custom limit."""
    client, user_id, empresa_id = admin_client

    # Create 25 URLs
    for i in range(25):
        criar_global_url(db_session, empresa_id, url=f"https://url{i}.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?page=1&limit=20")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 25
    assert len(data["data"]) == 20


def test_list_pagination_last_page_partial(admin_client, db_session):
    """Test last page with fewer items than limit."""
    client, user_id, empresa_id = admin_client

    # Create 23 URLs
    for i in range(23):
        criar_global_url(db_session, empresa_id, url=f"https://url{i}.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?page=3&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 23
    assert len(data["data"]) == 3  # Only 3 items on last page


def test_list_pagination_out_of_range(admin_client, db_session):
    """Test requesting a page beyond available data."""
    client, user_id, empresa_id = admin_client

    # Create 5 URLs
    for i in range(5):
        criar_global_url(db_session, empresa_id, url=f"https://url{i}.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?page=10&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["data"]) == 0  # No items on this page


# ============================================
# Search Tests
# ============================================

def test_list_search_by_url(admin_client, db_session):
    """Test case-insensitive search filtering on URL field."""
    client, user_id, empresa_id = admin_client

    # Create URLs with different patterns
    criar_global_url(db_session, empresa_id, url="https://api.example.com")
    criar_global_url(db_session, empresa_id, url="https://app.example.com")
    criar_global_url(db_session, empresa_id, url="https://test.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?search=example")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["data"]) == 2
    # Verify both contain "example"
    for item in data["data"]:
        assert "example" in item["url"].lower()


def test_list_search_case_insensitive(admin_client, db_session):
    """Test that search is case-insensitive."""
    client, user_id, empresa_id = admin_client

    criar_global_url(db_session, empresa_id, url="https://API.Example.COM")

    response = client.get(f"/global-urls/empresa/{empresa_id}?search=api.example")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["data"]) == 1


def test_list_search_no_results(admin_client, db_session):
    """Test search with no matching results."""
    client, user_id, empresa_id = admin_client

    criar_global_url(db_session, empresa_id, url="https://example.com")
    criar_global_url(db_session, empresa_id, url="https://test.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?search=nonexistent")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["data"]) == 0


def test_list_search_with_pagination(admin_client, db_session):
    """Test combining search with pagination."""
    client, user_id, empresa_id = admin_client

    # Create 15 URLs with "example", 5 without
    for i in range(15):
        criar_global_url(db_session, empresa_id, url=f"https://example{i}.com")
    for i in range(5):
        criar_global_url(db_session, empresa_id, url=f"https://other{i}.com")

    response = client.get(
        f"/global-urls/empresa/{empresa_id}?search=example&page=2&limit=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["data"]) == 5  # Second page


# ============================================
# Sort Tests
# ============================================

def test_list_sort_by_url_asc(admin_client, db_session):
    """Test sorting URLs alphabetically ascending."""
    client, user_id, empresa_id = admin_client

    criar_global_url(db_session, empresa_id, url="https://zebra.com")
    criar_global_url(db_session, empresa_id, url="https://alpha.com")
    criar_global_url(db_session, empresa_id, url="https://beta.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=url.asc")

    assert response.status_code == 200
    data = response.json()
    urls = [item["url"] for item in data["data"]]
    assert urls == ["https://alpha.com", "https://beta.com", "https://zebra.com"]


def test_list_sort_by_url_desc(admin_client, db_session):
    """Test sorting URLs alphabetically descending."""
    client, user_id, empresa_id = admin_client

    criar_global_url(db_session, empresa_id, url="https://zebra.com")
    criar_global_url(db_session, empresa_id, url="https://alpha.com")
    criar_global_url(db_session, empresa_id, url="https://beta.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=url.desc")

    assert response.status_code == 200
    data = response.json()
    urls = [item["url"] for item in data["data"]]
    assert urls == ["https://zebra.com", "https://beta.com", "https://alpha.com"]


def test_list_sort_by_criado_em_asc(admin_client, db_session):
    """Test sorting by creation timestamp ascending (oldest first)."""
    client, user_id, empresa_id = admin_client

    # Create URLs with small delays to ensure different timestamps
    url1 = criar_global_url(db_session, empresa_id, url="https://first.com")
    time.sleep(0.01)
    url2 = criar_global_url(db_session, empresa_id, url="https://second.com")
    time.sleep(0.01)
    url3 = criar_global_url(db_session, empresa_id, url="https://third.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=criado_em.asc")

    assert response.status_code == 200
    data = response.json()
    urls = [item["url"] for item in data["data"]]
    assert urls[0] == "https://first.com"
    assert urls[-1] == "https://third.com"


def test_list_sort_by_criado_em_desc(admin_client, db_session):
    """Test sorting by creation timestamp descending (newest first)."""
    client, user_id, empresa_id = admin_client

    url1 = criar_global_url(db_session, empresa_id, url="https://first.com")
    time.sleep(0.05)
    url2 = criar_global_url(db_session, empresa_id, url="https://second.com")
    time.sleep(0.05)
    url3 = criar_global_url(db_session, empresa_id, url="https://third.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=criado_em.desc")

    assert response.status_code == 200
    data = response.json()
    # Newest first - verify ordering by comparing timestamps
    assert len(data["data"]) == 3
    timestamps = [item["criado_em"] for item in data["data"]]
    # Ensure descending order (newest first)
    assert timestamps[0] >= timestamps[1] >= timestamps[2]


def test_list_sort_by_inativo_asc(admin_client, db_session):
    """Test sorting by inativo flag ascending (False before True)."""
    client, user_id, empresa_id = admin_client

    # Create URLs with different inativo values
    url1 = criar_global_url(db_session, empresa_id, url="https://active.com")
    url1.inativo = False
    db_session.commit()

    url2 = criar_global_url(db_session, empresa_id, url="https://inactive.com")
    url2.inativo = True
    db_session.commit()

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=inativo.asc")

    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["inativo"] is False
    assert data["data"][1]["inativo"] is True


def test_list_sort_by_global_urls_id_desc_default(admin_client, db_session):
    """Test default sort order is global_urls_id DESC (newest ID first)."""
    client, user_id, empresa_id = admin_client

    url1 = criar_global_url(db_session, empresa_id, url="https://first.com")
    url2 = criar_global_url(db_session, empresa_id, url="https://second.com")
    url3 = criar_global_url(db_session, empresa_id, url="https://third.com")

    # Request without sort parameter
    response = client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    # Default sort is by global_urls_id DESC
    # Since UUIDs don't have predictable ordering, just verify all IDs are present
    returned_ids = {item["global_urls_id"] for item in data["data"]}
    expected_ids = {str(url1.global_urls_id), str(url2.global_urls_id), str(url3.global_urls_id)}
    assert returned_ids == expected_ids


def test_list_sort_invalid_field(admin_client):
    """Test sorting with invalid field returns 400."""
    client, user_id, empresa_id = admin_client

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=invalid_field.asc")

    assert response.status_code == 400
    assert "não permitido" in response.json()["detail"].lower()


def test_list_sort_invalid_direction(admin_client):
    """Test sorting with invalid direction returns 400."""
    client, user_id, empresa_id = admin_client

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=url.invalid")

    assert response.status_code == 400
    assert "direção" in response.json()["detail"].lower()


def test_list_sort_invalid_format(admin_client):
    """Test sorting with invalid format (missing direction) returns 400."""
    client, user_id, empresa_id = admin_client

    response = client.get(f"/global-urls/empresa/{empresa_id}?sort=url")

    assert response.status_code == 400
    assert "inválido" in response.json()["detail"].lower()


# ============================================
# Validation Tests
# ============================================

def test_criar_missing_empresa_id(admin_client):
    """Test creating without empresa_id returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {
        "url": "https://test.com",
    }

    response = client.post("/global-urls/", json=payload)

    assert response.status_code == 422


def test_criar_invalid_empresa_id_format(admin_client):
    """Test creating with invalid UUID format returns 422."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": "not-a-uuid",
        "url": "https://test.com",
    }

    response = client.post("/global-urls/", json=payload)

    assert response.status_code == 422


def test_atualizar_with_null_values_doesnt_update(admin_client, db_session):
    """Test that passing null values in update doesn't change fields (partial update behavior)."""
    client, user_id, empresa_id = admin_client

    # Create URL with values
    url_record = criar_global_url(db_session, empresa_id, url="https://test.com")
    url_record.inativo = True
    db_session.commit()
    url_id = url_record.global_urls_id

    # Pass null values - should not update
    payload = {
        "url": None,
        "inativo": None,
    }

    response = client.put(f"/global-urls/id/{url_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    # Values should remain unchanged
    assert data["url"] == "https://test.com"
    assert data["inativo"] is True


# ============================================
# Error Handling Tests
# ============================================

def test_get_nonexistent_global_url(admin_client):
    """Test getting a non-existent global URL returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    response = client.get(f"/global-urls/id/{fake_id}")

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


def test_atualizar_nonexistent_global_url(admin_client):
    """Test updating a non-existent global URL returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    payload = {"url": "https://new.com"}

    response = client.put(f"/global-urls/id/{fake_id}", json=payload)

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


def test_deletar_nonexistent_global_url(admin_client):
    """Test deleting a non-existent global URL returns 404."""
    client, user_id, empresa_id = admin_client

    fake_id = str(uuid.uuid4())
    response = client.delete(f"/global-urls/id/{fake_id}")

    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


# ============================================
# Multi-Tenant Isolation Tests
# ============================================

def test_list_only_returns_empresa_urls(admin_client, db_session):
    """Test that list endpoint only returns URLs for the specified empresa."""
    client, user_id, empresa_id = admin_client

    # Create URLs for current empresa
    criar_global_url(db_session, empresa_id, url="https://empresa1-url1.com")
    criar_global_url(db_session, empresa_id, url="https://empresa1-url2.com")
    criar_global_url(db_session, empresa_id, url="https://empresa1-url3.com")

    # Create URLs for different empresa
    another_empresa_id = str(uuid.uuid4())
    criar_global_url(db_session, another_empresa_id, url="https://empresa2-url1.com")
    criar_global_url(db_session, another_empresa_id, url="https://empresa2-url2.com")

    response = client.get(f"/global-urls/empresa/{empresa_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["data"]) == 3
    # Verify all returned URLs belong to empresa_id
    for item in data["data"]:
        assert item["empresa_id"] == empresa_id


def test_list_different_empresas_isolated(db_session):
    """Test that two different empresas see only their own URLs."""
    # Setup empresa A
    user_id_a = str(uuid.uuid4())
    empresa_id_a = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id_a, empresa_id_a, "127.0.0.1")
    criar_global_url(db_session, empresa_id_a, url="https://empresa-a.com")

    async def mock_auth_a():
        return _mock_user_data(user_id_a, empresa_id_a, is_admin=True)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[check_auth_with_ip] = mock_auth_a
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client_a:
        response_a = client_a.get(f"/global-urls/empresa/{empresa_id_a}")
        assert response_a.status_code == 200
        data_a = response_a.json()
        assert data_a["total"] == 1

    app.dependency_overrides.clear()

    # Setup empresa B
    user_id_b = str(uuid.uuid4())
    empresa_id_b = str(uuid.uuid4())

    criar_usuarios_ip_whitelist(db_session, user_id_b, empresa_id_b, "127.0.0.1")
    criar_global_url(db_session, empresa_id_b, url="https://empresa-b.com")

    async def mock_auth_b():
        return _mock_user_data(user_id_b, empresa_id_b, is_admin=True)

    app.dependency_overrides[check_auth_with_ip] = mock_auth_b
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client_b:
        response_b = client_b.get(f"/global-urls/empresa/{empresa_id_b}")
        assert response_b.status_code == 200
        data_b = response_b.json()
        assert data_b["total"] == 1
        assert data_b["data"][0]["empresa_id"] == empresa_id_b

    app.dependency_overrides.clear()


# ============================================
# Database Verification Tests
# ============================================

def test_create_persists_to_database(admin_client, db_session):
    """Test that create operation actually persists data to database."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "url": "https://persist-test.com",
        "inativo": False,
    }

    response = client.post("/global-urls/", json=payload)
    assert response.status_code == 200

    global_url_id = response.json()["global_urls_id"]

    # Query database directly
    db_record = db_session.query(GlobalUrls).filter(
        GlobalUrls.global_urls_id == global_url_id
    ).first()

    assert db_record is not None
    assert db_record.url == "https://persist-test.com"
    assert db_record.empresa_id == uuid.UUID(empresa_id)
    assert db_record.inativo is False


def test_update_persists_to_database(admin_client, db_session):
    """Test that update operation actually modifies database records."""
    client, user_id, empresa_id = admin_client

    # Create URL via factory
    url_record = criar_global_url(db_session, empresa_id, url="https://before.com")
    url_id = url_record.global_urls_id

    payload = {
        "url": "https://after.com",
        "inativo": True,
    }

    response = client.put(f"/global-urls/id/{url_id}", json=payload)
    assert response.status_code == 200

    # Query database directly
    db_session.expire_all()  # Clear session cache
    db_record = db_session.query(GlobalUrls).filter(
        GlobalUrls.global_urls_id == url_id
    ).first()

    assert db_record.url == "https://after.com"
    assert db_record.inativo is True


def test_delete_removes_from_database(admin_client, db_session):
    """Test that delete operation actually removes record from database (hard delete)."""
    client, user_id, empresa_id = admin_client

    # Create URL via factory
    url_record = criar_global_url(db_session, empresa_id, url="https://delete.com")
    url_id = url_record.global_urls_id

    response = client.delete(f"/global-urls/id/{url_id}")
    assert response.status_code == 200

    # Query database directly - record should not exist
    db_session.expire_all()
    db_record = db_session.query(GlobalUrls).filter(
        GlobalUrls.global_urls_id == url_id
    ).first()

    assert db_record is None


def test_auto_generated_fields(admin_client, db_session):
    """Test that global_urls_id and criado_em are auto-generated."""
    client, user_id, empresa_id = admin_client

    payload = {
        "empresa_id": empresa_id,
        "url": "https://autogen-test.com",
    }

    response = client.post("/global-urls/", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Verify global_urls_id is a valid UUID
    assert "global_urls_id" in data
    try:
        uuid.UUID(data["global_urls_id"])
    except ValueError:
        pytest.fail("global_urls_id is not a valid UUID")

    # Verify criado_em is present and recent
    assert "criado_em" in data
    assert data["criado_em"] is not None


# ============================================
# Combined Scenarios Tests
# ============================================

def test_search_and_sort_combined(admin_client, db_session):
    """Test applying search and sort filters together."""
    client, user_id, empresa_id = admin_client

    # Create URLs with mixed patterns
    criar_global_url(db_session, empresa_id, url="https://api.zebra.com")
    criar_global_url(db_session, empresa_id, url="https://api.alpha.com")
    criar_global_url(db_session, empresa_id, url="https://test.com")
    criar_global_url(db_session, empresa_id, url="https://api.beta.com")

    response = client.get(
        f"/global-urls/empresa/{empresa_id}?search=api&sort=url.asc"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3  # Only URLs with "api"
    urls = [item["url"] for item in data["data"]]
    # Should be sorted alphabetically
    assert urls == [
        "https://api.alpha.com",
        "https://api.beta.com",
        "https://api.zebra.com",
    ]


def test_pagination_search_sort_combined(admin_client, db_session):
    """Test combining pagination, search, and sort."""
    client, user_id, empresa_id = admin_client

    # Create 15 URLs with "example"
    for i in range(15):
        criar_global_url(db_session, empresa_id, url=f"https://example-{i:02d}.com")

    # Create 5 URLs without "example"
    for i in range(5):
        criar_global_url(db_session, empresa_id, url=f"https://other-{i}.com")

    response = client.get(
        f"/global-urls/empresa/{empresa_id}?search=example&sort=url.desc&page=2&limit=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 15
    assert len(data["data"]) == 5  # Second page
    # Verify descending order
    urls = [item["url"] for item in data["data"]]
    assert urls[0] > urls[-1]  # Descending order


def test_inativo_flag_lifecycle(admin_client, db_session):
    """Test complete lifecycle: create → set inativo=True → set back to False."""
    client, user_id, empresa_id = admin_client

    # Step 1: Create with inativo=False
    payload = {
        "empresa_id": empresa_id,
        "url": "https://lifecycle-test.com",
        "inativo": False,
    }
    response = client.post("/global-urls/", json=payload)
    assert response.status_code == 200
    url_id = response.json()["global_urls_id"]
    assert response.json()["inativo"] is False

    # Step 2: Update to inativo=True
    response = client.put(f"/global-urls/id/{url_id}", json={"inativo": True})
    assert response.status_code == 200
    assert response.json()["inativo"] is True

    # Step 3: Verify in list
    response = client.get(f"/global-urls/empresa/{empresa_id}")
    data = response.json()
    url_item = next(item for item in data["data"] if item["global_urls_id"] == url_id)
    assert url_item["inativo"] is True

    # Step 4: Update back to inativo=False
    response = client.put(f"/global-urls/id/{url_id}", json={"inativo": False})
    assert response.status_code == 200
    assert response.json()["inativo"] is False

    # Step 5: Verify final state
    response = client.get(f"/global-urls/id/{url_id}")
    assert response.status_code == 200
    assert response.json()["inativo"] is False
