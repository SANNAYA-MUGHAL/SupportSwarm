from sqlalchemy import Column, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customers"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(100), index=True, nullable=True)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), index=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    segment = Column(String(50), default="standard", nullable=False)  # enterprise, vip, standard, high_risk
    risk_score = Column(Float, default=0.0, nullable=False)
    metadata_json = Column(JSON, default=dict, nullable=False)

    tickets = relationship("Ticket", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

class CustomerSegment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customer_segments"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    criteria_json = Column(JSON, default=dict, nullable=False)
