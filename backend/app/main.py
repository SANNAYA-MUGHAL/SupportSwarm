from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import async_engine
from app.database.base import Base
import app.models  # Register all models on Base.metadata

from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as org_router
from app.api.v1.audit import router as audit_router
from app.api.v1.tickets import router as tickets_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize schema in development SQLite mode if needed
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SupportSwarm: AI Customer Support & Product Intelligence Platform API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Mount v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(org_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(tickets_router, prefix=settings.API_V1_STR)

