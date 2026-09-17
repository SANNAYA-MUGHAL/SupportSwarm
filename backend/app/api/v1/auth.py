from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.auth import LoginRequest, DemoLoginRequest, TokenResponse, CurrentUser
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password."""
    return await AuthService.authenticate(db, req)

@router.post("/demo-login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def demo_login(req: DemoLoginRequest, db: AsyncSession = Depends(get_db)):
    """Instant 1-click login for any demo role."""
    return await AuthService.demo_login(db, req)

@router.get("/me", response_model=CurrentUser, status_code=status.HTTP_200_OK)
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """Get current authenticated user details."""
    return current_user
