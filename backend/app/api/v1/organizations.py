from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.organization import OrganizationSetupRequest, OrganizationResponse, OrganizationMemberResponse
from app.schemas.auth import CurrentUser
from app.services.org_service import OrgService
from app.services.auth_service import get_current_user
from app.core.rbac import require_roles, UserRole

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/setup", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def setup_org(req: OrganizationSetupRequest, db: AsyncSession = Depends(get_db)):
    """Set up a new organization with an initial admin user."""
    org, _ = await OrgService.setup_organization(db, req)
    return org

@router.get("/current", response_model=OrganizationResponse, status_code=status.HTTP_200_OK)
async def get_current_org(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve details for current authenticated user's organization."""
    org = await OrgService.get_by_id(db, current_user.organization_id)
    return org

@router.get("/members", response_model=List[OrganizationMemberResponse], status_code=status.HTTP_200_OK)
async def get_org_members(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Retrieve all team members in current user's organization."""
    members = await OrgService.get_members(db, current_user.organization_id)
    return members

