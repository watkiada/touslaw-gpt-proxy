"""
WatkiBot Security Module - Simplified Version

This module handles authentication, password hashing, and JWT token generation.
Uses pure-Python password hashing for Windows compatibility.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.hash import pbkdf2_sha256  # Using pbkdf2_sha256 instead of bcrypt for Windows compatibility
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def verify_password(plain_password, hashed_password):
    """Verify a password against a hash."""
    return pbkdf2_sha256.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate a password hash."""
    return pbkdf2_sha256.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from a JWT token."""
    from src.models.user import User
    from src.core.database import SessionLocal
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    finally:
        db.close()

def get_current_active_user(current_user = Depends(get_current_user)):
    """Get the current active user."""
    return current_user
