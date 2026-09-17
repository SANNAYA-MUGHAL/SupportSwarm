from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AuditEventResponse(BaseModel):
    id: str
    organization_id: str
    actor_type: str
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    old_state_json: Optional[Dict[str, Any]] = None
    new_state_json: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
