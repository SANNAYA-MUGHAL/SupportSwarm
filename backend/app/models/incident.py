from sqlalchemy import Column, String, Integer, Float, Numeric, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Incident(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incidents"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_number = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    severity = Column(String(10), default="S1", nullable=False)  # S1, S2, S3
    status = Column(String(50), default="emerging", nullable=False)  # emerging, investigating, confirmed, mitigated, resolved
    affected_services_json = Column(JSON, default=list, nullable=False)
    affected_regions_json = Column(JSON, default=list, nullable=False)
    affected_customers_count = Column(Integer, default=0, nullable=False)
    estimated_revenue_impact = Column(Numeric(12, 2), default=0.0, nullable=False)
    baseline_volume_rate = Column(Float, default=1.0, nullable=False)
    spike_volume_rate = Column(Float, default=5.0, nullable=False)
    commander_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    declared_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    tickets = relationship("IncidentTicket", back_populates="incident", cascade="all, delete-orphan")
    bug_reports = relationship("BugReport", back_populates="incident", cascade="all, delete-orphan")

class IncidentTicket(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "incident_tickets"

    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_confidence = Column(Float, default=0.95, nullable=False)

    incident = relationship("Incident", back_populates="tickets")
    ticket = relationship("Ticket")

class BugReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bug_reports"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    business_impact = Column(Text, nullable=False)
    customer_impact = Column(Text, nullable=False)
    environment = Column(String(50), default="production", nullable=False)
    preconditions = Column(Text, nullable=False)
    steps_to_reproduce_json = Column(JSON, default=list, nullable=False)
    expected_result = Column(Text, nullable=False)
    actual_result = Column(Text, nullable=False)
    technical_evidence_json = Column(JSON, default=dict, nullable=False)
    logs_and_events_json = Column(JSON, default=list, nullable=False)
    severity_recommendation = Column(String(20), default="critical", nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    suggested_owner = Column(String(100), nullable=False)
    external_tracker = Column(String(50), default="internal", nullable=False)  # internal, jira, linear, github, trello
    external_issue_id = Column(String(100), nullable=True)
    external_issue_url = Column(String(500), nullable=True)

    incident = relationship("Incident", back_populates="bug_reports")
