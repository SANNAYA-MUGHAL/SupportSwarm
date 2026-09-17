from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class KnowledgeArticle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_articles"

    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    status = Column(String(50), default="published", nullable=False)  # draft, published, archived
    usefulness_count = Column(Integer, default=0, nullable=False)
    not_useful_count = Column(Integer, default=0, nullable=False)
    embedding_json = Column(JSON, nullable=True)  # Stores vector embedding array for similarity search

    versions = relationship("KnowledgeArticleVersion", back_populates="article", cascade="all, delete-orphan", order_by="KnowledgeArticleVersion.version_number")

class KnowledgeArticleVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_article_versions"

    article_id = Column(String(36), ForeignKey("knowledge_articles.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    changed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    article = relationship("KnowledgeArticle", back_populates="versions")

class TicketSimilarity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ticket_similarities"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    similar_ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    matching_root_cause = Column(Text, nullable=False)
    feedback_useful = Column(Boolean, nullable=True)  # True = marked useful, False = marked irrelevant
