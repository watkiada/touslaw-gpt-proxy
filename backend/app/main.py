"""
Main application initialization module for MyAIDrive Clone
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create the FastAPI app
app = FastAPI(
    title="MyAIDrive Clone API",
    description="API for MyAIDrive Clone - Document Management with AI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routers
from app.api.api_v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Create startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize services and connections on startup
    """
    # Ensure storage directories exist
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_PATH, "offices"), exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_PATH, "temp", "uploads"), exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_PATH, "temp", "ocr"), exist_ok=True)

# Create shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown
    """
    # Close any open connections or resources
    pass

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {
        "status": "online",
        "message": "MyAIDrive Clone API is running",
        "version": "1.0.0"
    }
