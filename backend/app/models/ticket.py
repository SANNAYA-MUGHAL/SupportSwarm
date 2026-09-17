from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Ticket(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tickets"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), default="web_chat", nullable=False)  # web_chat, voice_note, email, support_form, whatsapp
    status = Column(String(50), default="new", nullable=False, index=True)  # new, triaged, investigating, waiting_for_approval, waiting_for_customer, waiting_for_internal_team, resolved, closed
    priority = Column(String(20), default="s3_medium", nullable=False)  # s1_critical, s2_high, s3_medium, s4_low
    urgency = Column(String(20), default="medium", nullable=False)  # critical, high, medium, low
    sentiment = Column(String(50), default="neutral", nullable=False)  # frustrated, angry, neutral, anxious, satisfied
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    assigned_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_agent_id = Column(String(36), nullable=True)
    reopened_count = Column(Integer, default=0, nullable=False)
    sla_due_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="tickets")
    assigned_user = relationship("User")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    classification = relationship("TicketClassification", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    investigation = relationship("Investigation", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    voice_transcript = relationship("VoiceTranscript", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    entities = relationship("ExtractedEntity", back_populates="ticket", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ticket_messages"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False)  # customer, user, agent
    sender_id = Column(String(36), nullable=True)
    content = Column(Text, nullable=False)
    language = Column(String(10), default="en", nullable=False)
    is_internal_note = Column(Boolean, default=False, nullable=False)

    ticket = relationship("Ticket", back_populates="messages")

class TicketAttachment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ticket_attachments"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_url = Column(String(500), nullable=False)

    ticket = relationship("Ticket", back_populates="attachments")

class TicketClassification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ticket_classifications"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False)  # payment_pending, duplicate_payment, refund_delay, etc.
    subcategory = Column(String(100), nullable=True)
    severity = Column(String(10), default="S3", nullable=False)  # S1, S2, S3, S4
    confidence = Column(Float, default=0.90, nullable=False)
    reasoning = Column(Text, nullable=False)
    fraud_risk_score = Column(Float, default=0.0, nullable=False)
    missing_info = Column(JSON, default=list, nullable=False)

    ticket = relationship("Ticket", back_populates="classification")
