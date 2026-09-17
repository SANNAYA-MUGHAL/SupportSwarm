from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from app.database.base import Base, UUIDPrimaryKeyMixin

class AuditEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "audit_events"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    actor_type = Column(String(20), nullable=False)  # user, agent, system
    actor_id = Column(String(36), nullable=True)
    actor_name = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False, index=True)  # ticket.create, ticket.status_change, response.approved, etc.
    entity_type = Column(String(50), nullable=False, index=True)  # ticket, response, refund, incident, bug_report, opportunity
    entity_id = Column(String(36), nullable=False, index=True)
    old_state_json = Column(JSON, nullable=True)
    new_state_json = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
