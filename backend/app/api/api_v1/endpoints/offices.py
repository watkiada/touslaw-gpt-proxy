"""
API router for offices endpoints
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, Office
from app.schemas.office import Office as OfficeSchema, OfficeCreate, OfficeUpdate
from app.services.office_service import OfficeService

router = APIRouter()


@router.get("/", response_model=List[OfficeSchema])
async def read_offices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve offices accessible to current user.
    """
    office_service = OfficeService(db)
    offices = office_service.get_user_offices(user_id=current_user.id, skip=skip, limit=limit)
    return offices


@router.post("/", response_model=OfficeSchema)
async def create_office(
    office_in: OfficeCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Create new office.
    """
    office_service = OfficeService(db)
    office = office_service.create(office_in=office_in, user_id=current_user.id)
    return office


@router.get("/{office_id}", response_model=OfficeSchema)
async def read_office(
    office_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get office by ID.
    """
    office_service = OfficeService(db)
    office = office_service.get(office_id=office_id)
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found"
        )
    
    # Check if user has access to office
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return office


@router.put("/{office_id}", response_model=OfficeSchema)
async def update_office(
    office_id: int,
    office_in: OfficeUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update office.
    """
    office_service = OfficeService(db)
    
    # Check if user has admin access to office
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id, role="admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    office = office_service.update(office_id=office_id, office_in=office_in)
    return office


@router.delete("/{office_id}", response_model=OfficeSchema)
async def delete_office(
    office_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete office.
    """
    office_service = OfficeService(db)
    
    # Check if user has admin access to office
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id, role="admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    office = office_service.delete(office_id=office_id)
    return office
