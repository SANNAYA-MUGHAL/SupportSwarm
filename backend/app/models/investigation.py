from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Investigation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "investigations"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    status = Column(String(50), default="completed", nullable=False)  # running, completed, failed
    summary = Column(Text, nullable=False)
    root_cause_hypothesis = Column(Text, nullable=False)
    expected_state_json = Column(JSON, default=dict, nullable=False)
    actual_state_json = Column(JSON, default=dict, nullable=False)
    discrepancy = Column(Text, nullable=False)
    verified_facts_json = Column(JSON, default=list, nullable=False)
    assumptions_json = Column(JSON, default=list, nullable=False)
    recommended_action = Column(Text, nullable=False)
    confidence = Column(Float, default=0.92, nullable=False)

    ticket = relationship("Ticket", back_populates="investigation")
    events = relationship("InvestigationEvent", back_populates="investigation", cascade="all, delete-orphan", order_by="InvestigationEvent.event_sequence")

class InvestigationEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "investigation_events"

    investigation_id = Column(String(36), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False, index=True)
    event_sequence = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source_system = Column(String(50), nullable=False)  # order_svc, payment_gateway, refund_mgr, notification_svc, core_db
    event_type = Column(String(100), nullable=False)
    status = Column(String(20), default="success", nullable=False)  # success, warning, failure
    correlation_id = Column(String(100), index=True, nullable=True)
    evidence_summary = Column(Text, nullable=False)
    raw_payload_json = Column(JSON, default=dict, nullable=False)

    investigation = relationship("Investigation", back_populates="events")
