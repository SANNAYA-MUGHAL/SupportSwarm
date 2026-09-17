from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "orders"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, confirmed, processing, shipped, delivered, cancelled, failed
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="PKR", nullable=False)
    items_json = Column(JSON, default=list, nullable=False)
    shipping_address = Column(String(500), nullable=True)

    customer = relationship("Customer", back_populates="orders")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(String(36), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    provider = Column(String(50), default="stripe", nullable=False)  # stripe, jazzcash, easypaisa, nayapay, hbl
    status = Column(String(50), default="initiated", nullable=False)  # initiated, authorized, captured, failed, refunded
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="PKR", nullable=False)
    failure_code = Column(String(100), nullable=True)
    correlation_id = Column(String(100), index=True, nullable=True)

    order = relationship("Order", back_populates="payments")
    refunds = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")

class Refund(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "refunds"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(String(36), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default="requested", nullable=False)  # requested, processing, completed, failed
    provider_reference = Column(String(100), nullable=True)
    failure_reason = Column(String(500), nullable=True)
    processed_at = Column(DateTime, nullable=True)

    payment = relationship("Payment", back_populates="refunds")
