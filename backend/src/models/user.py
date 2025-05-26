"""
WatkiBot User Model - Simplified Version

This module defines a simplified User model for authentication.
Uses pure-Python password hashing for Windows compatibility.
"""
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256  # Using pbkdf2_sha256 instead of bcrypt for Windows compatibility

from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pbkdf2_sha256.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pbkdf2_sha256.hash(password)

    @classmethod
    def create(cls, db: Session, email: str, password: str, is_admin: bool = False):
        hashed_password = cls.get_password_hash(password)
        db_user = cls(
            email=email, 
            hashed_password=hashed_password, 
            is_admin=is_admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user or not User.verify_password(password, user.hashed_password):
            return None
        return user
