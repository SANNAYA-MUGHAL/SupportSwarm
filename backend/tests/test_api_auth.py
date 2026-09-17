import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "SupportSwarm"

@pytest.mark.asyncio
async def test_organization_setup_and_login(async_client: AsyncClient):
    # Setup new org
    setup_payload = {
        "name": "Apex Ecommerce",
        "slug": "apex-ecommerce",
        "admin_email": "apex_admin@example.com",
        "admin_name": "Farhan CEO",
        "admin_password": "StrongPassword123!"
    }
    setup_res = await async_client.post("/api/v1/organizations/setup", json=setup_payload)
    assert setup_res.status_code == 201
    org_data = setup_res.json()
    assert org_data["slug"] == "apex-ecommerce"

    # Login with admin credentials
    login_payload = {
        "email": "apex_admin@example.com",
        "password": "StrongPassword123!"
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["user"]["email"] == "apex_admin@example.com"
    assert token_data["user"]["role"] == "admin"

    # Test /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "apex_admin@example.com"
    assert me_data["role"] == "admin"

@pytest.mark.asyncio
async def test_demo_login_all_six_roles(async_client: AsyncClient):
    roles = [
        "admin",
        "support_lead",
        "support_agent",
        "qa_engineer",
        "product_manager",
        "viewer"
    ]
    for role in roles:
        demo_payload = {
            "role": role,
            "organization_slug": "demo-fintech"
        }
        res = await async_client.post("/api/v1/auth/demo-login", json=demo_payload)
        assert res.status_code == 200, f"Demo login failed for role {role}: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert data["user"]["role"] == role
        assert data["organization"]["slug"] == "demo-fintech"

@pytest.mark.asyncio
async def test_audit_logs_rbac(async_client: AsyncClient):
    # Login as Support Lead
    lead_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "demo-fintech"}
    )
    lead_token = lead_res.json()["access_token"]
    lead_headers = {"Authorization": f"Bearer {lead_token}"}

    # Support Lead should be allowed to view audit logs
    audit_res = await async_client.get("/api/v1/audit/logs", headers=lead_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert isinstance(logs, list)
    assert len(logs) >= 1  # Login event was logged

    # Login as Viewer
    viewer_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "viewer", "organization_slug": "demo-fintech"}
    )
    viewer_token = viewer_res.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # Viewer should be forbidden from accessing audit logs
    viewer_audit_res = await async_client.get("/api/v1/audit/logs", headers=viewer_headers)
    assert viewer_audit_res.status_code == 403

@pytest.mark.asyncio
async def test_unauthorized_endpoints(async_client: AsyncClient):
    # No token provided
    res = await async_client.get("/api/v1/auth/me")
    assert res.status_code == 401

    # Bad token
    bad_headers = {"Authorization": "Bearer bad.token.here"}
    res_bad = await async_client.get("/api/v1/auth/me", headers=bad_headers)
    assert res_bad.status_code == 401
