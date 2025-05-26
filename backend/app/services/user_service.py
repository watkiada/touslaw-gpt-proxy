"""
User service for user management
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user management operations"""
    
    def __init__(self, db: Session):
        """
        Initialize user service
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User object or None if not found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get multiple users
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            
        Returns:
            List of user objects
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self, user_in: UserCreate) -> User:
        """
        Create new user
        
        Args:
            user_in: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If user creation fails
        """
        try:
            # Check if user with this email already exists
            db_user = self.get_by_email(email=user_in.email)
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create user
            user = User(
                email=user_in.email,
                hashed_password=get_password_hash(user_in.password),
                full_name=user_in.full_name,
                is_active=user_in.is_active,
                is_superuser=user_in.is_superuser
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )
    
    def update(self, user_id: int, user_in: UserUpdate) -> User:
        """
        Update user
        
        Args:
            user_id: User ID
            user_in: User update data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If user update fails
        """
        try:
            # Get user
            user = self.get(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update user fields
            update_data = user_in.dict(exclude_unset=True)
            
            # Hash password if provided
            if "password" in update_data:
                hashed_password = get_password_hash(update_data["password"])
                del update_data["password"]
                update_data["hashed_password"] = hashed_password
            
            # Update user
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {str(e)}"
            )
    
    def delete(self, user_id: int) -> User:
        """
        Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            Deleted user object
            
        Raises:
            HTTPException: If user deletion fails
        """
        try:
            # Get user
            user = self.get(user_id=user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Delete user
            self.db.delete(user)
            self.db.commit()
            return user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user: {str(e)}"
            )
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_last_login(self, user_id: int) -> None:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
        """
        try:
            user = self.get(user_id=user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.db.commit()
        except Exception:
            self.db.rollback()
