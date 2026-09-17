from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class SlaPolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sla_policies"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    priority = Column(String(20), default="s2_high", nullable=False)
    first_response_time_minutes = Column(Integer, default=30, nullable=False)
    resolution_time_minutes = Column(Integer, default=240, nullable=False)

class ModelUsage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "model_usage"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class Feedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "feedback"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # ticket, draft_response, similar_case, article
    entity_id = Column(String(36), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, default=5, nullable=False)  # 1-5 or 0/1
    comment = Column(String(500), nullable=True)
