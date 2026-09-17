from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Integration(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "integrations"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(50), nullable=False)  # jira, linear, github, trello, whatsapp, zendesk, freshdesk, intercom, gmail
    is_enabled = Column(Boolean, default=False, nullable=False)
    config_json = Column(JSON, default=dict, nullable=False)

    credentials = relationship("ApiCredential", back_populates="integration", cascade="all, delete-orphan")

class ApiCredential(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "api_credentials"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    integration_id = Column(String(36), ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False, index=True)
    key_name = Column(String(100), nullable=False)
    encrypted_secret = Column(String(500), nullable=False)

    integration = relationship("Integration", back_populates="credentials")
