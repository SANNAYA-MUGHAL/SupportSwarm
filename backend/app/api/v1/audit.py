from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.audit import AuditEventResponse
from app.schemas.auth import CurrentUser
from app.services.audit_service import AuditService
from app.services.auth_service import get_current_user
from app.core.rbac import require_roles, UserRole

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/logs", response_model=List[AuditEventResponse], status_code=status.HTTP_200_OK)
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve immutable audit events for the organization."""
    require_roles(
        [UserRole.ADMIN, UserRole.SUPPORT_LEAD, UserRole.QA_ENGINEER, UserRole.PRODUCT_MANAGER],
        current_user.role
    )
    return await AuditService.get_org_audit_logs(
        db=db,
        organization_id=current_user.organization_id,
        limit=limit,
        offset=offset
    )
