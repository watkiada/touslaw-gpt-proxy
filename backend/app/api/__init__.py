"""
Initialize API routes
"""
from fastapi import APIRouter

from app.api.api_v1.api import api_router

# Create main API router
router = APIRouter()

# Include API v1 router
router.include_router(api_router, prefix="/api/v1")
