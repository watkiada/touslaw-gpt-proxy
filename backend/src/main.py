"""
WatkiBot Main Application - Simplified Version

This module is the entry point for the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import Base, engine
from src.routes import auth, cases, documents

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="WatkiBot Law Assistant",
    description="A simplified document management system for legal professionals",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(cases.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Welcome to WatkiBot API"}

# Create initial admin user if not exists
from sqlalchemy.orm import Session
from src.models.user import User
from src.core.database import SessionLocal

def init_db():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            # Create admin user
            User.create(
                db=db,
                email="admin@example.com",
                password="password123",
                is_admin=True
            )
            print("Admin user created successfully")
    finally:
        db.close()

# Initialize database with admin user
init_db()
