import uuid
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Organization(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    domain = Column(String(255), nullable=True)
    plan = Column(String(50), default="enterprise", nullable=False)
    settings = Column(JSON, default=dict, nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")

class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="support_agent", nullable=False)  # admin, support_lead, support_agent, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(String(500), nullable=True)

    organization = relationship("Organization", back_populates="users")
    user_teams = relationship("UserTeam", back_populates="user", cascade="all, delete-orphan")

class Team(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "teams"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    organization = relationship("Organization", back_populates="teams")
    members = relationship("UserTeam", back_populates="team", cascade="all, delete-orphan")

class UserTeam(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_teams"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id = Column(String(36), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="user_teams")
    team = relationship("Team", back_populates="members")
