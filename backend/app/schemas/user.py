from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str
    is_active: bool = True
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str
    organization_id: str

class UserResponse(UserBase):
    id: str
    organization_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
