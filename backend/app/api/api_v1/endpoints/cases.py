"""
API router for cases endpoints
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, Case
from app.schemas.case import Case as CaseSchema, CaseCreate, CaseUpdate
from app.services.case_service import CaseService
from app.services.office_service import OfficeService

router = APIRouter()


@router.get("/", response_model=List[CaseSchema])
async def read_cases(
    office_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve cases for an office.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    case_service = CaseService(db)
    cases = case_service.get_by_office(office_id=office_id, skip=skip, limit=limit)
    return cases


@router.post("/", response_model=CaseSchema)
async def create_case(
    case_in: CaseCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Create new case.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=case_in.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    case_service = CaseService(db)
    case = case_service.create(case_in=case_in, user_id=current_user.id)
    return case


@router.get("/{case_id}", response_model=CaseSchema)
async def read_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get case by ID.
    """
    case_service = CaseService(db)
    case = case_service.get(case_id=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=case.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return case


@router.put("/{case_id}", response_model=CaseSchema)
async def update_case(
    case_id: int,
    case_in: CaseUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update case.
    """
    case_service = CaseService(db)
    case = case_service.get(case_id=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=case.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    case = case_service.update(case_id=case_id, case_in=case_in)
    return case


@router.delete("/{case_id}", response_model=CaseSchema)
async def delete_case(
    case_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete case.
    """
    case_service = CaseService(db)
    case = case_service.get(case_id=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=case.office_id, role="admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    case = case_service.delete(case_id=case_id)
    return case
