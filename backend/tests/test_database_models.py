import pytest
from sqlalchemy import select
from app.models import (
    Organization, User, Team, UserTeam, Customer, Order, Payment, Refund,
    Ticket, TicketMessage, TicketClassification, VoiceTranscript,
    ExtractedEntity, Investigation, InvestigationEvent, KnowledgeArticle,
    Incident, BugReport, ProductOpportunity, ApprovalRequest, Agent,
    AuditEvent
)

@pytest.mark.asyncio
async def test_create_organization_and_user(db_session):
    org = Organization(name="FinTech Corp", slug="fintech-corp")
    db_session.add(org)
    await db_session.flush()

    user = User(
        organization_id=org.id,
        email="lead@fintech.com",
        full_name="Hamza Support Lead",
        hashed_password="hashed_secret",
        role="support_lead"
    )
    db_session.add(user)
    await db_session.flush()

    result = await db_session.execute(select(User).where(User.email == "lead@fintech.com"))
    fetched_user = result.scalar_one_or_none()
    assert fetched_user is not None
    assert fetched_user.role == "support_lead"
    assert fetched_user.organization_id == org.id

@pytest.mark.asyncio
async def test_create_ticket_with_full_hierarchy(db_session):
    org = Organization(name="MegaStore", slug="megastore")
    db_session.add(org)
    await db_session.flush()

    customer = Customer(
        organization_id=org.id,
        email="customer@example.com",
        full_name="Ayesha Khan",
        segment="vip"
    )
    db_session.add(customer)
    await db_session.flush()

    ticket = Ticket(
        organization_id=org.id,
        ticket_number="TCK-1001",
        customer_id=customer.id,
        subject="Payment Deducted but Order Pending",
        description="Amount of 4500 PKR was charged from JazzCash but order is still not confirmed."
    )
    db_session.add(ticket)
    await db_session.flush()

    # Add Message
    msg = TicketMessage(
        ticket_id=ticket.id,
        sender_type="customer",
        content="Please check urgently!",
        language="en"
    )
    db_session.add(msg)

    # Add Classification
    classification = TicketClassification(
        ticket_id=ticket.id,
        category="payment_pending",
        severity="S1",
        confidence=0.96,
        reasoning="Payment captured without order creation; financial discrepancy."
    )
    db_session.add(classification)

    # Add Extracted Entity
    entity = ExtractedEntity(
        ticket_id=ticket.id,
        entity_type="amount",
        entity_value="4500 PKR",
        confidence=0.99
    )
    db_session.add(entity)
    await db_session.flush()

    # Query Ticket with relationships
    result = await db_session.execute(select(Ticket).where(Ticket.ticket_number == "TCK-1001"))
    fetched_ticket = result.scalar_one_or_none()
    assert fetched_ticket is not None
    assert fetched_ticket.subject == "Payment Deducted but Order Pending"

@pytest.mark.asyncio
async def test_audit_event_logging(db_session):
    org = Organization(name="AuditCorp", slug="audit-corp")
    db_session.add(org)
    await db_session.flush()

    audit = AuditEvent(
        organization_id=org.id,
        actor_type="agent",
        actor_name="Intake Agent",
        action="ticket.created",
        entity_type="ticket",
        entity_id="mock-ticket-id",
        new_state_json={"status": "new"}
    )
    db_session.add(audit)
    await db_session.flush()

    result = await db_session.execute(select(AuditEvent).where(AuditEvent.organization_id == org.id))
    events = result.scalars().all()
    assert len(events) == 1
    assert events[0].action == "ticket.created"
    assert events[0].actor_type == "agent"
