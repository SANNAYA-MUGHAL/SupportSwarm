"""
Main entrypoint for Vercel deployment and local execution.
Re-exports the FastAPI application instance from app.main.
"""
from app.main import app

__all__ = ["app"]
