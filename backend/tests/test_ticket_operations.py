import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.models.audit import AuditEvent

@pytest.mark.asyncio
async def test_ticket_creation_and_detail(async_client: AsyncClient):
    # 1. Login as Support Agent
    login_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_agent", "organization_slug": "demo-fintech"}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Ticket
    create_payload = {
        "customer_name": "Hamza Ali",
        "customer_email": "hamza.ali@example.com",
        "customer_phone": "+923001122334",
        "channel": "web_chat",
        "subject": "Payment deducted for Order ORD-20015 but pending",
        "description": "I paid PKR 3,500 using JazzCash but status is stuck. Card: 4532 1234 5678 9012.",
        "priority": "s1_critical",
        "urgency": "critical",
        "category": "payment_pending",
        "order_number": "ORD-20015",
        "transaction_id": "TXN-80015"
    }
    res = await async_client.post("/api/v1/tickets", json=create_payload, headers=headers)
    assert res.status_code == 201, res.text
    ticket = res.json()
    assert ticket["ticket_number"].startswith("TCK-")
    assert ticket["status"] == "new"
    assert ticket["priority"] == "s1_critical"
    # Verify card masking in description
    assert "4532" not in ticket["description"]
    assert "****-****-****-9012" in ticket["description"]
    assert ticket["customer"]["email"] == "hamza.ali@example.com"
    assert len(ticket["entities"]) >= 1

    # 3. Retrieve Detail
    detail_res = await async_client.get(f"/api/v1/tickets/{ticket['id']}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == ticket["id"]
    assert "triaged" in detail["allowed_transitions"]

@pytest.mark.asyncio
async def test_user_journey_1_create_assign_note_resolve_close(async_client: AsyncClient, db_session):
    # Setup Support Lead
    lead_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "demo-fintech"}
    )
    lead_token = lead_res.json()["access_token"]
    lead_id = lead_res.json()["user"]["id"]
    headers = {"Authorization": f"Bearer {lead_token}"}

    # Step 1: Create Ticket
    create_res = await async_client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Tariq Jamil",
            "customer_email": "tariq.j@example.com",
            "channel": "support_form",
            "subject": "Discount Voucher Error",
            "description": "Voucher FLASH50 was rejected at checkout.",
            "priority": "s3_medium"
        },
        headers=headers
    )
    t_id = create_res.json()["id"]

    # Step 2: Assign Agent
    assign_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/assign",
        json={"user_id": lead_id},
        headers=headers
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["assigned_user_id"] == lead_id

    # Step 3: Transition to Triaged then Investigating
    triage_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "triaged"},
        headers=headers
    )
    assert triage_res.status_code == 200
    assert triage_res.json()["status"] == "triaged"

    inv_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "investigating"},
        headers=headers
    )
    assert inv_res.status_code == 200
    assert inv_res.json()["status"] == "investigating"

    # Step 4: Add Internal Note
    note_res = await async_client.post(
        f"/api/v1/tickets/{t_id}/messages",
        json={"content": "Checked customer cart: minimum spend PKR 3000 was not met.", "is_internal_note": True},
        headers=headers
    )
    assert note_res.status_code == 201
    assert note_res.json()["is_internal_note"] is True

    # Step 5: Resolve Ticket
    resolve_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "resolved", "reason": "Customer advised of coupon minimum cart requirement."},
        headers=headers
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"
    assert resolve_res.json()["resolved_at"] is not None

    # Step 6: Close Ticket
    close_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "closed"},
        headers=headers
    )
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "closed"
    assert close_res.json()["closed_at"] is not None

    # Verify Audit Events were recorded for this ticket
    audit_events = (await db_session.execute(
        select(AuditEvent).where(AuditEvent.entity_id == t_id)
    )).scalars().all()
    actions = [e.action for e in audit_events]
    assert "ticket.created" in actions
    assert "ticket.assigned" in actions
    assert "ticket.status_change" in actions
    assert "ticket.note_added" in actions

@pytest.mark.asyncio
async def test_user_journey_2_wait_for_customer_and_resume(async_client: AsyncClient, db_session):
    lead_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "demo-fintech"}
    )
    headers = {"Authorization": f"Bearer {lead_res.json()['access_token']}"}

    # 1. Create Ticket
    create_res = await async_client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Sara Ahmed",
            "customer_email": "sara.a@example.com",
            "channel": "email",
            "subject": "Missing OTP for password reset",
            "description": "Did not get verification SMS."
        },
        headers=headers
    )
    t_id = create_res.json()["id"]

    # 2. Transition New -> Investigating -> Waiting for Customer
    await async_client.patch(f"/api/v1/tickets/{t_id}/status", json={"target_status": "investigating"}, headers=headers)
    wait_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "waiting_for_customer", "reason": "Asked customer for phone network info"},
        headers=headers
    )
    assert wait_res.status_code == 200
    assert wait_res.json()["status"] == "waiting_for_customer"

    # 3. Customer replies: Ticket should resume to 'investigating'
    from app.services.ticket_service import TicketService
    await TicketService.add_message(
        db=db_session,
        organization_id=create_res.json()["organization_id"],
        ticket_id=t_id,
        actor_id=None,
        actor_name="Sara Ahmed",
        sender_type="customer",
        content="My network is Jazz and number is ported.",
        is_internal_note=False
    )
    await db_session.flush()

    # Verify status transitioned automatically to 'investigating'
    updated = await async_client.get(f"/api/v1/tickets/{t_id}", headers=headers)
    assert updated.json()["status"] == "investigating"

    # 4. Resolve
    resolve_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "resolved"},
        headers=headers
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"

@pytest.mark.asyncio
async def test_user_journey_3_close_reopen_and_resolve(async_client: AsyncClient):
    lead_res = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "demo-fintech"}
    )
    headers = {"Authorization": f"Bearer {lead_res.json()['access_token']}"}

    create_res = await async_client.post(
        "/api/v1/tickets",
        json={
            "customer_name": "Imran Khan",
            "customer_email": "imran.k@example.com",
            "channel": "web_chat",
            "subject": "Delivery delay inquiry",
            "description": "Where is my parcel?"
        },
        headers=headers
    )
    t_id = create_res.json()["id"]

    # Close directly from new
    await async_client.patch(f"/api/v1/tickets/{t_id}/status", json={"target_status": "closed"}, headers=headers)

    # Reopen from closed to investigating
    reopen_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "investigating", "reason": "Customer re-contacted saying parcel still not received."},
        headers=headers
    )
    assert reopen_res.status_code == 200
    detail = reopen_res.json()
    assert detail["status"] == "investigating"
    assert detail["reopened_count"] == 1
    assert detail["closed_at"] is None

    # Resolve again
    res2 = await async_client.patch(f"/api/v1/tickets/{t_id}/status", json={"target_status": "resolved"}, headers=headers)
    assert res2.json()["status"] == "resolved"

@pytest.mark.asyncio
async def test_organization_isolation(async_client: AsyncClient):
    # User in Org 1
    org1_login = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "demo-fintech"}
    )
    org1_headers = {"Authorization": f"Bearer {org1_login.json()['access_token']}"}

    # Create ticket in Org 1
    t_res = await async_client.post(
        "/api/v1/tickets",
        json={"customer_name": "Org1 User", "customer_email": "u1@org1.com", "subject": "Private Org 1 Ticket", "description": "Secret ticket"},
        headers=org1_headers
    )
    org1_ticket_id = t_res.json()["id"]

    # User in Org 2
    org2_login = await async_client.post(
        "/api/v1/auth/demo-login",
        json={"role": "support_lead", "organization_slug": "different-competitor-org"}
    )
    org2_headers = {"Authorization": f"Bearer {org2_login.json()['access_token']}"}

    # Org 2 user tries to fetch Org 1 ticket
    unauthorized_fetch = await async_client.get(f"/api/v1/tickets/{org1_ticket_id}", headers=org2_headers)
    assert unauthorized_fetch.status_code == 404

    # Org 2 user tries to modify Org 1 ticket status
    unauthorized_mod = await async_client.patch(
        f"/api/v1/tickets/{org1_ticket_id}/status",
        json={"target_status": "resolved"},
        headers=org2_headers
    )
    assert unauthorized_mod.status_code == 404

@pytest.mark.asyncio
async def test_role_based_permissions(async_client: AsyncClient):
    # Setup Lead to create ticket
    lead_res = await async_client.post("/api/v1/auth/demo-login", json={"role": "support_lead", "organization_slug": "demo-fintech"})
    lead_headers = {"Authorization": f"Bearer {lead_res.json()['access_token']}"}
    t_res = await async_client.post(
        "/api/v1/tickets",
        json={"customer_name": "Perm Test", "customer_email": "perm@test.com", "subject": "Testing Roles", "description": "Desc"},
        headers=lead_headers
    )
    t_id = t_res.json()["id"]

    # Login as Viewer (read-only)
    viewer_res = await async_client.post("/api/v1/auth/demo-login", json={"role": "viewer", "organization_slug": "demo-fintech"})
    viewer_headers = {"Authorization": f"Bearer {viewer_res.json()['access_token']}"}

    # Viewer CAN read ticket
    read_res = await async_client.get(f"/api/v1/tickets/{t_id}", headers=viewer_headers)
    assert read_res.status_code == 200

    # Viewer CANNOT change status (403 Forbidden)
    status_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/status",
        json={"target_status": "triaged"},
        headers=viewer_headers
    )
    assert status_res.status_code == 403

    # Viewer CANNOT assign ticket
    assign_res = await async_client.patch(
        f"/api/v1/tickets/{t_id}/assign",
        json={"user_id": viewer_res.json()["user"]["id"]},
        headers=viewer_headers
    )
    assert assign_res.status_code == 403

@pytest.mark.asyncio
async def test_get_organization_members(async_client: AsyncClient):
    login_res = await async_client.post("/api/v1/auth/demo-login", json={"role": "admin", "organization_slug": "demo-fintech"})
    headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    res = await async_client.get("/api/v1/organizations/members", headers=headers)
    assert res.status_code == 200
    members = res.json()
    assert len(members) >= 1
    assert any(m["role"] == "admin" for m in members)
    assert "id" in members[0]
    assert "full_name" in members[0]

@pytest.mark.asyncio
async def test_ticket_audit_trail_and_attachments(async_client: AsyncClient):
    # Setup Lead
    lead_res = await async_client.post("/api/v1/auth/demo-login", json={"role": "support_lead", "organization_slug": "demo-fintech"})
    lead_headers = {"Authorization": f"Bearer {lead_res.json()['access_token']}"}

    # 1. Create ticket
    t_res = await async_client.post(
        "/api/v1/tickets",
        json={"customer_name": "Audit Test User", "customer_email": "audit@test.com", "subject": "Audit & Attachment Flow", "description": "Testing audit logging and attachment upload."},
        headers=lead_headers
    )
    assert t_res.status_code == 201
    t_id = t_res.json()["id"]

    # 2. Add an attachment (simulating upload)
    files = {"file": ("test_evidence.pdf", b"%PDF-1.4 test evidence document content", "application/pdf")}
    att_res = await async_client.post(f"/api/v1/tickets/{t_id}/attachments", files=files, headers=lead_headers)
    assert att_res.status_code == 201
    att_data = att_res.json()
    assert att_data["file_name"] == "test_evidence.pdf"
    assert att_data["file_size"] > 0

    # 3. Add internal note
    note_res = await async_client.post(
        f"/api/v1/tickets/{t_id}/messages",
        json={"content": "Reviewed uploaded evidence and verified validity.", "is_internal_note": True},
        headers=lead_headers
    )
    assert note_res.status_code == 201

    # 4. Fetch ticket audit logs
    audit_res = await async_client.get(f"/api/v1/tickets/{t_id}/audit", headers=lead_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 3
    actions = [l["action"] for l in logs]
    assert "ticket.created" in actions
    assert "ticket.attachment_added" in actions
    assert "ticket.note_added" in actions

