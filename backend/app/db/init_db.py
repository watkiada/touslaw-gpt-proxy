"""
Database initialization script
"""
import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.core.config import settings
from app.models.models import User, AIModel
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models to be created in the database
MODELS = [
    {"name": "GPT-4", "provider": "openai", "model_id": "gpt-4", "description": "OpenAI GPT-4 model"},
    {"name": "GPT-3.5 Turbo", "provider": "openai", "model_id": "gpt-3.5-turbo", "description": "OpenAI GPT-3.5 Turbo model"},
    {"name": "Claude 3 Opus", "provider": "anthropic", "model_id": "claude-3-opus-20240229", "description": "Anthropic Claude 3 Opus model"},
    {"name": "Gemini Pro", "provider": "google", "model_id": "gemini-pro", "description": "Google Gemini Pro model"}
]

def init_db(db: Session) -> None:
    """Initialize database with tables and initial data"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if admin user exists
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        logger.info("Creating admin user")
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            full_name="Admin User",
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
    
    # Check if AI models exist
    model_count = db.query(AIModel).count()
    if model_count == 0:
        logger.info("Creating AI models")
        for model_data in MODELS:
            model = AIModel(**model_data)
            db.add(model)
        db.commit()
    
    logger.info("Database initialization completed")
