export type UserRole =
  | 'admin'
  | 'support_lead'
  | 'support_agent'
  | 'qa_engineer'
  | 'product_manager'
  | 'viewer';

export interface User {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  domain?: string;
  plan: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  user: User;
  organization: Organization;
}
