"""
Case service for case management
"""
from typing import Optional, List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.models import Case
from app.schemas.case import CaseCreate, CaseUpdate


class CaseService:
    """Service for case management operations"""
    
    def __init__(self, db: Session):
        """
        Initialize case service
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get(self, case_id: int) -> Optional[Case]:
        """
        Get case by ID
        
        Args:
            case_id: Case ID
            
        Returns:
            Case object or None if not found
        """
        return self.db.query(Case).filter(Case.id == case_id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[Case]:
        """
        Get multiple cases
        
        Args:
            skip: Number of cases to skip
            limit: Maximum number of cases to return
            
        Returns:
            List of case objects
        """
        return self.db.query(Case).offset(skip).limit(limit).all()
    
    def get_by_office(self, office_id: int, skip: int = 0, limit: int = 100) -> List[Case]:
        """
        Get cases for an office
        
        Args:
            office_id: Office ID
            skip: Number of cases to skip
            limit: Maximum number of cases to return
            
        Returns:
            List of case objects
        """
        return self.db.query(Case).filter(Case.office_id == office_id).offset(skip).limit(limit).all()
    
    def create(self, case_in: CaseCreate, user_id: int) -> Case:
        """
        Create new case
        
        Args:
            case_in: Case creation data
            user_id: User ID of creator
            
        Returns:
            Created case object
            
        Raises:
            HTTPException: If case creation fails
        """
        try:
            # Create case
            case = Case(
                name=case_in.name,
                description=case_in.description,
                status=case_in.status,
                office_id=case_in.office_id,
                created_by_id=user_id
            )
            self.db.add(case)
            self.db.commit()
            self.db.refresh(case)
            return case
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating case: {str(e)}"
            )
    
    def update(self, case_id: int, case_in: CaseUpdate) -> Case:
        """
        Update case
        
        Args:
            case_id: Case ID
            case_in: Case update data
            
        Returns:
            Updated case object
            
        Raises:
            HTTPException: If case update fails
        """
        try:
            # Get case
            case = self.get(case_id=case_id)
            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Case not found"
                )
            
            # Update case fields
            update_data = case_in.dict(exclude_unset=True)
            
            # Update case
            for field, value in update_data.items():
                setattr(case, field, value)
            
            self.db.commit()
            self.db.refresh(case)
            return case
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating case: {str(e)}"
            )
    
    def delete(self, case_id: int) -> Case:
        """
        Delete case
        
        Args:
            case_id: Case ID
            
        Returns:
            Deleted case object
            
        Raises:
            HTTPException: If case deletion fails
        """
        try:
            # Get case
            case = self.get(case_id=case_id)
            if not case:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Case not found"
                )
            
            # Delete case
            self.db.delete(case)
            self.db.commit()
            return case
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting case: {str(e)}"
            )
