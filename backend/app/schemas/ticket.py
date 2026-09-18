from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict

class TicketCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: Optional[str] = None
    channel: str = "web_chat"  # web_chat, voice_note, email, support_form, whatsapp
    subject: str
    description: str
    priority: Optional[str] = "s3_medium"
    urgency: Optional[str] = "medium"
    category: Optional[str] = None
    order_number: Optional[str] = None
    transaction_id: Optional[str] = None

class TicketStateTransitionRequest(BaseModel):
    target_status: str
    reason: Optional[str] = None

class TicketAssignmentRequest(BaseModel):
    user_id: Optional[str] = None
    agent_id: Optional[str] = None

class MessageCreateRequest(BaseModel):
    content: str
    is_internal_note: bool = False
    language: str = "en"

class MessageResponse(BaseModel):
    id: str
    ticket_id: str
    sender_type: str  # customer, user, agent
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    content: str
    language: str = "en"
    is_internal_note: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AttachmentResponse(BaseModel):
    id: str
    file_name: str
    file_type: str
    file_size: int
    storage_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClassificationResponse(BaseModel):
    id: str
    category: str
    subcategory: Optional[str] = None
    severity: str
    confidence: float
    reasoning: str
    fraud_risk_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class VoiceTranscriptResponse(BaseModel):
    id: str
    audio_storage_url: str
    audio_format: str
    duration_seconds: float
    detected_language: str
    transcript_raw: str
    transcript_edited: Optional[str] = None
    segments_json: List[Dict[str, Any]] = []
    confidence_score: float
    is_edited: bool

    model_config = ConfigDict(from_attributes=True)

class ExtractedEntityResponse(BaseModel):
    id: str
    entity_type: str
    entity_value: str
    confidence: float
    is_masked: bool

    model_config = ConfigDict(from_attributes=True)

class CustomerSummary(BaseModel):
    id: str
    external_id: Optional[str] = None
    full_name: str
    email: str
    phone: Optional[str] = None
    segment: str
    risk_score: float
    metadata_json: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class OrderSummary(BaseModel):
    id: str
    order_number: str
    status: str
    total_amount: float
    currency: str
    items_json: List[Dict[str, Any]] = []
    shipping_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaymentSummary(BaseModel):
    id: str
    transaction_id: str
    provider: str
    status: str
    amount: float
    currency: str
    failure_code: Optional[str] = None
    correlation_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvestigationSummaryResponse(BaseModel):
    id: str
    status: str
    summary: str
    root_cause_hypothesis: str
    expected_state_json: Dict[str, Any] = {}
    actual_state_json: Dict[str, Any] = {}
    discrepancy: str
    verified_facts_json: List[str] = []
    assumptions_json: List[str] = []
    recommended_action: str
    confidence: float
    events_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class TicketListItem(BaseModel):
    id: str
    ticket_number: str
    channel: str
    status: str
    priority: str
    urgency: str
    sentiment: str
    subject: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_segment: str
    assigned_user_id: Optional[str] = None
    assigned_user_name: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    has_voice: bool = False
    reopened_count: int = 0
    sla_due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TicketListResponse(BaseModel):
    items: List[TicketListItem]
    total: int
    page: int
    limit: int
    pages: int
    status_counts: Dict[str, int]

class TicketDetailResponse(BaseModel):
    id: str
    organization_id: str
    ticket_number: str
    channel: str
    status: str
    priority: str
    urgency: str
    sentiment: str
    subject: str
    description: str
    assigned_user_id: Optional[str] = None
    assigned_user_name: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    reopened_count: int = 0
    sla_due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    customer: CustomerSummary
    messages: List[MessageResponse] = []
    attachments: List[AttachmentResponse] = []
    classification: Optional[ClassificationResponse] = None
    voice_transcript: Optional[VoiceTranscriptResponse] = None
    entities: List[ExtractedEntityResponse] = []
    investigation: Optional[InvestigationSummaryResponse] = None
    order: Optional[OrderSummary] = None
    payment: Optional[PaymentSummary] = None
    allowed_transitions: List[str] = []

    model_config = ConfigDict(from_attributes=True)
