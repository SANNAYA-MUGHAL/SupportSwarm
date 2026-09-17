from sqlalchemy import Column, String, Integer, Float, Numeric, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class ProductOpportunity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_opportunities"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    problem_statement = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(String(50), default="new", nullable=False)  # new, investigate, monitor, rejected, merged, discovery, initiative
    frequency_score = Column(Integer, default=1, nullable=False)
    affected_users_count = Column(Integer, default=0, nullable=False)
    affected_segments_json = Column(JSON, default=list, nullable=False)
    estimated_revenue_impact = Column(Numeric(12, 2), default=0.0, nullable=False)
    trend_direction = Column(String(20), default="increasing", nullable=False)  # increasing, stable, decreasing
    confidence_level = Column(Float, default=0.85, nullable=False)
    existing_workaround = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=False)
    recommended_discovery_action = Column(Text, nullable=False)
    suggested_experiment = Column(Text, nullable=False)
    pm_decision = Column(String(50), nullable=True)
    pm_notes = Column(Text, nullable=True)

    evidence_items = relationship("OpportunityEvidence", back_populates="opportunity", cascade="all, delete-orphan")
    quotes = relationship("CustomerQuote", back_populates="opportunity", cascade="all, delete-orphan")

class OpportunityEvidence(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "opportunity_evidence"

    opportunity_id = Column(String(36), ForeignKey("product_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)  # ticket_summary, investigation_fact, telemetry_metric
    description = Column(Text, nullable=False)

    opportunity = relationship("ProductOpportunity", back_populates="evidence_items")
    ticket = relationship("Ticket")

class CustomerQuote(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customer_quotes"

    opportunity_id = Column(String(36), ForeignKey("product_opportunities.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    quote_text = Column(Text, nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)

    opportunity = relationship("ProductOpportunity", back_populates="quotes")
