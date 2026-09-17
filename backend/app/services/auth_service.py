from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.organization import Organization, User
from app.schemas.auth import LoginRequest, DemoLoginRequest, TokenResponse, CurrentUser
from app.schemas.user import UserResponse
from app.schemas.organization import OrganizationResponse
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.rbac import UserRole
from app.services.audit_service import AuditService
from app.database.session import get_db

security_bearer = HTTPBearer(auto_error=False)

# Standard demo personas
DEMO_PERSONAS = {
    UserRole.ADMIN.value: {
        "email": "admin@supportswarm.demo",
        "full_name": "Sarah Khan (Admin)",
        "role": UserRole.ADMIN.value
    },
    UserRole.SUPPORT_LEAD.value: {
        "email": "lead@supportswarm.demo",
        "full_name": "Hamza Tariq (Support Lead)",
        "role": UserRole.SUPPORT_LEAD.value
    },
    UserRole.SUPPORT_AGENT.value: {
        "email": "agent@supportswarm.demo",
        "full_name": "Bilal Ahmed (Support Agent)",
        "role": UserRole.SUPPORT_AGENT.value
    },
    UserRole.QA_ENGINEER.value: {
        "email": "qa@supportswarm.demo",
        "full_name": "Zainab Malik (QA Engineer)",
        "role": UserRole.QA_ENGINEER.value
    },
    UserRole.PRODUCT_MANAGER.value: {
        "email": "pm@supportswarm.demo",
        "full_name": "Omar Farooq (Product Manager)",
        "role": UserRole.PRODUCT_MANAGER.value
    },
    UserRole.VIEWER.value: {
        "email": "viewer@supportswarm.demo",
        "full_name": "Amina Hassan (Executive Viewer)",
        "role": UserRole.VIEWER.value
    },
}

class AuthService:
    @staticmethod
    async def authenticate(db: AsyncSession, req: LoginRequest) -> TokenResponse:
        stmt = select(User).where(User.email == req.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is deactivated."
            )

        # Fetch org
        org_result = await db.execute(select(Organization).where(Organization.id == user.organization_id))
        org = org_result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found.")

        token = create_access_token({
            "sub": user.id,
            "org_id": org.id,
            "role": user.role,
            "email": user.email,
            "name": user.full_name
        })

        await AuditService.log_event(
            db=db,
            organization_id=org.id,
            actor_type="user",
            actor_id=user.id,
            actor_name=user.full_name,
            action="auth.login",
            entity_type="user",
            entity_id=user.id
        )

        return TokenResponse(
            access_token=token,
            expires_in_minutes=60 * 24,
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(org)
        )

    @staticmethod
    async def demo_login(db: AsyncSession, req: DemoLoginRequest) -> TokenResponse:
        role = req.role.lower()
        if role not in DEMO_PERSONAS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid demo role '{req.role}'. Valid roles: {list(DEMO_PERSONAS.keys())}"
            )

        persona = DEMO_PERSONAS[role]
        org_slug = req.organization_slug or "demo-fintech"

        # Ensure demo org exists
        org_result = await db.execute(select(Organization).where(Organization.slug == org_slug))
        org = org_result.scalar_one_or_none()
        if not org:
            org = Organization(
                name="SwiftPay FinTech",
                slug=org_slug,
                plan="enterprise",
                settings={"demo_mode": True, "currency": "PKR"}
            )
            db.add(org)
            await db.flush()

        # Ensure demo user exists
        user_result = await db.execute(select(User).where(User.email == persona["email"]))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                organization_id=org.id,
                email=persona["email"],
                full_name=persona["full_name"],
                hashed_password=get_password_hash("DemoSecret123!"),
                role=persona["role"],
                is_active=True
            )
            db.add(user)
            await db.flush()

        token = create_access_token({
            "sub": user.id,
            "org_id": org.id,
            "role": user.role,
            "email": user.email,
            "name": user.full_name
        })

        await AuditService.log_event(
            db=db,
            organization_id=org.id,
            actor_type="user",
            actor_id=user.id,
            actor_name=user.full_name,
            action="auth.demo_login",
            entity_type="user",
            entity_id=user.id,
            new_state={"role": user.role}
        )

        return TokenResponse(
            access_token=token,
            expires_in_minutes=60 * 24,
            user=UserResponse.model_validate(user),
            organization=OrganizationResponse.model_validate(org)
        )

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> CurrentUser:
    """Dependency to extract authenticated user from Bearer JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token."
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token."
        )

    return CurrentUser(
        user_id=payload.get("sub", ""),
        organization_id=payload.get("org_id", ""),
        email=payload.get("email", ""),
        role=payload.get("role", ""),
        full_name=payload.get("name", "")
    )
