from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    slug: str
    domain: Optional[str] = None
    plan: str = "enterprise"
    settings: Dict[str, Any] = {}

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationSetupRequest(BaseModel):
    name: str
    slug: str
    admin_email: str
    admin_name: str
    admin_password: str

class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
