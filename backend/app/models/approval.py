from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class ApprovalRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "approval_requests"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    opportunity_id = Column(String(36), ForeignKey("product_opportunities.id", ondelete="CASCADE"), nullable=True, index=True)
    request_type = Column(String(50), nullable=False)  # send_response, issue_refund, change_order, update_payment, declare_incident, create_bug_report, add_product_opportunity, close_ticket, sensitive_access
    proposed_action_json = Column(JSON, nullable=False)
    recommendation_reasoning = Column(Text, nullable=False)
    evidence_summary_json = Column(JSON, default=list, nullable=False)
    confidence_score = Column(Float, default=0.95, nullable=False)
    risk_level = Column(String(20), default="low", nullable=False)  # low, medium, high, critical
    risk_explanation = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected, edited_and_approved

    ticket = relationship("Ticket", back_populates="approval_requests")
    decision = relationship("ApprovalDecision", back_populates="approval_request", uselist=False, cascade="all, delete-orphan")

class ApprovalDecision(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "approval_decisions"

    approval_request_id = Column(String(36), ForeignKey("approval_requests.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    decided_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision = Column(String(50), nullable=False)  # approved, rejected, edited
    edited_action_json = Column(JSON, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    approval_request = relationship("ApprovalRequest", back_populates="decision")
    decided_by_user = relationship("User")
