"""
Office service for office management
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.models import Office, OfficeUser
from app.schemas.office import OfficeCreate, OfficeUpdate


class OfficeService:
    """Service for office management operations"""
    
    def __init__(self, db: Session):
        """
        Initialize office service
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get(self, office_id: int) -> Optional[Office]:
        """
        Get office by ID
        
        Args:
            office_id: Office ID
            
        Returns:
            Office object or None if not found
        """
        return self.db.query(Office).filter(Office.id == office_id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Office]:
        """
        Get multiple offices
        
        Args:
            skip: Number of offices to skip
            limit: Maximum number of offices to return
            
        Returns:
            List of office objects
        """
        return self.db.query(Office).offset(skip).limit(limit).all()
    
    def get_user_offices(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Office]:
        """
        Get offices accessible to a user
        
        Args:
            user_id: User ID
            skip: Number of offices to skip
            limit: Maximum number of offices to return
            
        Returns:
            List of office objects
        """
        return self.db.query(Office).join(OfficeUser).filter(
            OfficeUser.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def create(self, office_in: OfficeCreate, user_id: int) -> Office:
        """
        Create new office
        
        Args:
            office_in: Office creation data
            user_id: User ID of creator
            
        Returns:
            Created office object
            
        Raises:
            HTTPException: If office creation fails
        """
        try:
            # Create office
            office = Office(
                name=office_in.name,
                description=office_in.description,
                created_by_id=user_id
            )
            self.db.add(office)
            self.db.commit()
            self.db.refresh(office)
            
            # Add creator as admin
            office_user = OfficeUser(
                office_id=office.id,
                user_id=user_id,
                role="admin"
            )
            self.db.add(office_user)
            self.db.commit()
            
            return office
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating office: {str(e)}"
            )
    
    def update(self, office_id: int, office_in: OfficeUpdate) -> Office:
        """
        Update office
        
        Args:
            office_id: Office ID
            office_in: Office update data
            
        Returns:
            Updated office object
            
        Raises:
            HTTPException: If office update fails
        """
        try:
            # Get office
            office = self.get(office_id=office_id)
            if not office:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Office not found"
                )
            
            # Update office fields
            update_data = office_in.dict(exclude_unset=True)
            
            # Update office
            for field, value in update_data.items():
                setattr(office, field, value)
            
            self.db.commit()
            self.db.refresh(office)
            return office
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating office: {str(e)}"
            )
    
    def delete(self, office_id: int) -> Office:
        """
        Delete office
        
        Args:
            office_id: Office ID
            
        Returns:
            Deleted office object
            
        Raises:
            HTTPException: If office deletion fails
        """
        try:
            # Get office
            office = self.get(office_id=office_id)
            if not office:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Office not found"
                )
            
            # Delete office
            self.db.delete(office)
            self.db.commit()
            return office
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting office: {str(e)}"
            )
    
    def user_has_access(self, user_id: int, office_id: int, role: Optional[str] = None) -> bool:
        """
        Check if user has access to office
        
        Args:
            user_id: User ID
            office_id: Office ID
            role: Optional role requirement ('admin' or 'member')
            
        Returns:
            True if user has access, False otherwise
        """
        query = self.db.query(OfficeUser).filter(
            OfficeUser.user_id == user_id,
            OfficeUser.office_id == office_id
        )
        
        if role:
            query = query.filter(OfficeUser.role == role)
        
        return query.first() is not None
    
    def add_user(self, office_id: int, user_id: int, role: str = "member") -> OfficeUser:
        """
        Add user to office
        
        Args:
            office_id: Office ID
            user_id: User ID
            role: User role ('admin' or 'member')
            
        Returns:
            Created office user relationship
            
        Raises:
            HTTPException: If adding user fails
        """
        try:
            # Check if office exists
            office = self.get(office_id=office_id)
            if not office:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Office not found"
                )
            
            # Check if user already in office
            existing = self.db.query(OfficeUser).filter(
                OfficeUser.office_id == office_id,
                OfficeUser.user_id == user_id
            ).first()
            
            if existing:
                # Update role if different
                if existing.role != role:
                    existing.role = role
                    self.db.commit()
                    self.db.refresh(existing)
                return existing
            
            # Add user to office
            office_user = OfficeUser(
                office_id=office_id,
                user_id=user_id,
                role=role
            )
            self.db.add(office_user)
            self.db.commit()
            self.db.refresh(office_user)
            return office_user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error adding user to office: {str(e)}"
            )
    
    def remove_user(self, office_id: int, user_id: int) -> None:
        """
        Remove user from office
        
        Args:
            office_id: Office ID
            user_id: User ID
            
        Raises:
            HTTPException: If removing user fails
        """
        try:
            # Get office user relationship
            office_user = self.db.query(OfficeUser).filter(
                OfficeUser.office_id == office_id,
                OfficeUser.user_id == user_id
            ).first()
            
            if not office_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not in office"
                )
            
            # Delete relationship
            self.db.delete(office_user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error removing user from office: {str(e)}"
            )
