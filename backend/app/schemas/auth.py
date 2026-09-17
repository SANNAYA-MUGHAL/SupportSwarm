from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.user import UserResponse
from app.schemas.organization import OrganizationResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class DemoLoginRequest(BaseModel):
    role: str  # admin, support_lead, support_agent, qa_engineer, product_manager, viewer
    organization_slug: Optional[str] = "demo-fintech"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserResponse
    organization: OrganizationResponse

class CurrentUser(BaseModel):
    user_id: str
    organization_id: str
    email: str
    role: str
    full_name: str
