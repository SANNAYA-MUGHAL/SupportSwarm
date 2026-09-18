export type TicketStatus =
  | 'new'
  | 'triaged'
  | 'investigating'
  | 'waiting_for_approval'
  | 'waiting_for_customer'
  | 'waiting_for_internal_team'
  | 'resolved'
  | 'closed';

export type TicketPriority = 's1_critical' | 's2_high' | 's3_medium' | 's4_low';
export type TicketSeverity = 'S1' | 'S2' | 'S3' | 'S4';
export type TicketChannel = 'web_chat' | 'voice_note' | 'email' | 'support_form' | 'whatsapp';

export interface CustomerSummary {
  id: string;
  external_id?: string;
  full_name: string;
  email: string;
  phone?: string;
  segment: string;
  risk_score: number;
  metadata_json: Record<string, any>;
}

export interface OrderSummary {
  id: string;
  order_number: string;
  status: string;
  total_amount: number;
  currency: string;
  items_json: Array<{ item: string; qty: number; price: number }>;
  shipping_address?: string;
  created_at: string;
}

export interface PaymentSummary {
  id: string;
  transaction_id: string;
  provider: string;
  status: string;
  amount: number;
  currency: string;
  failure_code?: string;
  correlation_id?: string;
  created_at: string;
}

export interface ClassificationSummary {
  id: string;
  category: string;
  subcategory?: string;
  severity: TicketSeverity;
  confidence: number;
  reasoning: string;
  fraud_risk_score: number;
}

export interface VoiceTranscriptSummary {
  id: string;
  audio_storage_url: string;
  audio_format: string;
  duration_seconds: number;
  detected_language: string;
  transcript_raw: string;
  transcript_edited?: string;
  segments_json: Array<{ start: number; end: number; text: string }>;
  confidence_score: number;
  is_edited: boolean;
}

export interface ExtractedEntitySummary {
  id: string;
  entity_type: string;
  entity_value: string;
  confidence: number;
  is_masked: boolean;
}

export interface InvestigationSummary {
  id: string;
  status: string;
  summary: string;
  root_cause_hypothesis: string;
  expected_state_json: Record<string, any>;
  actual_state_json: Record<string, any>;
  discrepancy: string;
  verified_facts_json: string[];
  assumptions_json: string[];
  recommended_action: string;
  confidence: number;
  events_count: number;
}

export interface MessageItem {
  id: string;
  ticket_id: string;
  sender_type: 'customer' | 'user' | 'agent';
  sender_id?: string;
  sender_name?: string;
  content: string;
  language: string;
  is_internal_note: boolean;
  created_at: string;
}

export interface AttachmentItem {
  id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  storage_url: string;
  created_at: string;
}

export interface TicketListItem {
  id: string;
  ticket_number: string;
  channel: TicketChannel;
  status: TicketStatus;
  priority: TicketPriority;
  urgency: string;
  sentiment: string;
  subject: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_segment: string;
  assigned_user_id?: string;
  assigned_user_name?: string;
  category?: string;
  severity?: TicketSeverity;
  has_voice: boolean;
  reopened_count: number;
  sla_due_at?: string;
  resolved_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface TicketListResponse {
  items: TicketListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
  status_counts: Record<string, number>;
}

export interface TicketDetailResponse {
  id: string;
  organization_id: string;
  ticket_number: string;
  channel: TicketChannel;
  status: TicketStatus;
  priority: TicketPriority;
  urgency: string;
  sentiment: string;
  subject: string;
  description: string;
  assigned_user_id?: string;
  assigned_user_name?: string;
  assigned_agent_id?: string;
  reopened_count: number;
  sla_due_at?: string;
  resolved_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;

  customer: CustomerSummary;
  messages: MessageItem[];
  attachments: AttachmentItem[];
  classification?: ClassificationSummary;
  voice_transcript?: VoiceTranscriptSummary;
  entities: ExtractedEntitySummary[];
  investigation?: InvestigationSummary;
  order?: OrderSummary;
  payment?: PaymentSummary;
  allowed_transitions: string[];
}
