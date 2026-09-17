from sqlalchemy import Column, String, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class VoiceTranscript(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "voice_transcripts"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    audio_storage_url = Column(String(500), nullable=False)
    audio_format = Column(String(10), default="mp3", nullable=False)  # mp3, wav, m4a, ogg
    duration_seconds = Column(Float, default=0.0, nullable=False)
    detected_language = Column(String(20), default="en", nullable=False)  # en, ur, ur-Latn
    transcript_raw = Column(Text, nullable=False)
    transcript_edited = Column(Text, nullable=True)
    segments_json = Column(JSON, default=list, nullable=False)  # timestamped sentences
    confidence_score = Column(Float, default=0.95, nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)

    ticket = relationship("Ticket", back_populates="voice_transcript")

class ExtractedEntity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "extracted_entities"

    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False)  # order_id, transaction_id, email, phone, amount, currency, date
    entity_value = Column(String(255), nullable=False)
    confidence = Column(Float, default=0.90, nullable=False)
    is_masked = Column(Boolean, default=False, nullable=False)

    ticket = relationship("Ticket", back_populates="entities")
