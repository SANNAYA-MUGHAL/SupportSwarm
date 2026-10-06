from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.organization import Organization, User
from app.schemas.organization import OrganizationSetupRequest
from app.core.security import get_password_hash
from app.core.rbac import UserRole
from app.services.audit_service import AuditService

class OrgService:
    @staticmethod
    async def get_by_id(db: AsyncSession, org_id: str) -> Optional[Organization]:
        result = await db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Organization]:
        result = await db.execute(select(Organization).where(Organization.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def setup_organization(db: AsyncSession, req: OrganizationSetupRequest) -> tuple[Organization, User]:
        # Check slug collision
        existing = await OrgService.get_by_slug(db, req.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with slug '{req.slug}' already exists."
            )

        # Create Org
        org = Organization(
            name=req.name,
            slug=req.slug,
            plan="enterprise",
            settings={
                "support_email": req.admin_email,
                "default_currency": "PKR",
                "default_language": "en"
            }
        )
        db.add(org)
        await db.flush()

        # Create Admin User
        admin_user = User(
            organization_id=org.id,
            email=req.admin_email,
            full_name=req.admin_name,
            hashed_password=get_password_hash(req.admin_password),
            role=UserRole.ADMIN.value,
            is_active=True
        )
        db.add(admin_user)
        await db.flush()

        # Audit event
        await AuditService.log_event(
            db=db,
            organization_id=org.id,
            actor_type="user",
            actor_id=admin_user.id,
            actor_name=admin_user.full_name,
            action="organization.setup",
            entity_type="organization",
            entity_id=org.id,
            new_state={"org_name": org.name, "admin_email": admin_user.email}
        )

        return org, admin_user

    @staticmethod
    async def get_members(db: AsyncSession, org_id: str) -> list[User]:
        """Fetch all active users in the organization."""
        result = await db.execute(
            select(User)
            .where(User.organization_id == org_id)
            .order_by(User.full_name)
        )
        return list(result.scalars().all())

