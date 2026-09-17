from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPPORT_LEAD = "support_lead"
    SUPPORT_AGENT = "support_agent"
    QA_ENGINEER = "qa_engineer"
    PRODUCT_MANAGER = "product_manager"
    VIEWER = "viewer"

class Permission(str, Enum):
    # Tickets
    TICKETS_READ = "tickets:read"
    TICKETS_CREATE = "tickets:create"
    TICKETS_UPDATE = "tickets:update"
    TICKETS_ASSIGN = "tickets:assign"
    TICKETS_CLOSE = "tickets:close"
    
    # Customer Communication & Approvals
    RESPONSES_DRAFT = "responses:draft"
    RESPONSES_APPROVE = "responses:approve"
    REFUNDS_REQUEST = "refunds:request"
    REFUNDS_APPROVE = "refunds:approve"
    ORDERS_MODIFY = "orders:modify"
    
    # Incidents
    INCIDENTS_VIEW = "incidents:view"
    INCIDENTS_DECLARE = "incidents:declare"
    INCIDENTS_RESOLVE = "incidents:resolve"
    
    # Bug Reports & QA
    BUGS_VIEW = "bugs:view"
    BUGS_CREATE = "bugs:create"
    BUGS_EXPORT = "bugs:export"
    
    # Product Intelligence
    PRODUCT_VIEW = "product:view"
    PRODUCT_DECISION = "product:decision"
    
    # Knowledge Base
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_EDIT = "knowledge:edit"
    
    # Analytics & Observability
    ANALYTICS_VIEW = "analytics:view"
    AGENTS_VIEW = "agents:view"
    AGENTS_TRIGGER = "agents:trigger"
    
    # Settings & Audit
    AUDIT_VIEW = "audit:view"
    SETTINGS_MANAGE = "settings:manage"

# Mapping of roles to their granted permissions
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: set(Permission),  # All permissions
    
    UserRole.SUPPORT_LEAD: {
        Permission.TICKETS_READ, Permission.TICKETS_CREATE, Permission.TICKETS_UPDATE,
        Permission.TICKETS_ASSIGN, Permission.TICKETS_CLOSE,
        Permission.RESPONSES_DRAFT, Permission.RESPONSES_APPROVE,
        Permission.REFUNDS_REQUEST, Permission.REFUNDS_APPROVE,
        Permission.ORDERS_MODIFY,
        Permission.INCIDENTS_VIEW, Permission.INCIDENTS_DECLARE, Permission.INCIDENTS_RESOLVE,
        Permission.BUGS_VIEW, Permission.BUGS_CREATE, Permission.BUGS_EXPORT,
        Permission.PRODUCT_VIEW,
        Permission.KNOWLEDGE_READ, Permission.KNOWLEDGE_EDIT,
        Permission.ANALYTICS_VIEW, Permission.AGENTS_VIEW, Permission.AGENTS_TRIGGER,
        Permission.AUDIT_VIEW
    },
    
    UserRole.SUPPORT_AGENT: {
        Permission.TICKETS_READ, Permission.TICKETS_CREATE, Permission.TICKETS_UPDATE,
        Permission.RESPONSES_DRAFT, Permission.REFUNDS_REQUEST,
        Permission.INCIDENTS_VIEW, Permission.BUGS_VIEW,
        Permission.PRODUCT_VIEW,
        Permission.KNOWLEDGE_READ, Permission.KNOWLEDGE_EDIT,
        Permission.ANALYTICS_VIEW
    },
    
    UserRole.QA_ENGINEER: {
        Permission.TICKETS_READ,
        Permission.INCIDENTS_VIEW,
        Permission.BUGS_VIEW, Permission.BUGS_CREATE, Permission.BUGS_EXPORT,
        Permission.KNOWLEDGE_READ,
        Permission.ANALYTICS_VIEW, Permission.AUDIT_VIEW
    },
    
    UserRole.PRODUCT_MANAGER: {
        Permission.TICKETS_READ,
        Permission.INCIDENTS_VIEW,
        Permission.BUGS_VIEW,
        Permission.PRODUCT_VIEW, Permission.PRODUCT_DECISION,
        Permission.KNOWLEDGE_READ,
        Permission.ANALYTICS_VIEW, Permission.AUDIT_VIEW
    },
    
    UserRole.VIEWER: {
        Permission.TICKETS_READ,
        Permission.INCIDENTS_VIEW,
        Permission.BUGS_VIEW,
        Permission.PRODUCT_VIEW,
        Permission.KNOWLEDGE_READ,
        Permission.ANALYTICS_VIEW
    }
}

def has_permission(role: UserRole, permission: Permission) -> bool:
    """Check if a specific role grants a permission."""
    perms = ROLE_PERMISSIONS.get(role, set())
    return permission in perms

def require_roles(allowed_roles: List[UserRole], user_role: str):
    """Enforce role check or raise 403 Forbidden."""
    if user_role not in [r.value for r in allowed_roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted for role: {user_role}. Requires one of: {[r.value for r in allowed_roles]}"
        )
