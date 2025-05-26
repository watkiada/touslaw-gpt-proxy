"""
API endpoints for letter generation and saving
"""
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import os
import json

from app.api import deps
from app.models.models import User, Document, Case, Office
from app.services.letter_service import LetterService
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/generate")
async def generate_letter(
    letter_type: str,
    recipient: str,
    subject: str,
    content_instructions: str,
    letterhead: Optional[Dict[str, str]] = None,
    case_id: Optional[int] = None,
    office_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Generate letter with AI using document context
    """
    # Check if user has access to case/office
    if case_id or office_id:
        document_service = DocumentService(db)
        
        if case_id and not document_service.user_has_access_to_case(user_id=current_user.id, case_id=case_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions for case"
            )
        
        if office_id and not document_service.user_has_access_to_office(user_id=current_user.id, office_id=office_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions for office"
            )
    
    # Initialize letter service
    letter_service = LetterService()
    
    # Generate letter
    try:
        letter_content = await letter_service.generate_letter(
            letter_type=letter_type,
            recipient=recipient,
            subject=subject,
            content_instructions=content_instructions,
            letterhead=letterhead,
            case_id=case_id,
            office_id=office_id
        )
        
        return {
            "success": True,
            "letter_content": letter_content
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating letter: {str(e)}"
        )


@router.post("/save")
async def save_letter(
    letter_content: str,
    case_id: int,
    office_id: int,
    filename: str,
    format: str = "docx",
    letterhead: Optional[Dict[str, str]] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Save letter to case folder
    """
    # Check if user has access to case/office
    document_service = DocumentService(db)
    
    if not document_service.user_has_access_to_case(user_id=current_user.id, case_id=case_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for case"
        )
    
    if not document_service.user_has_access_to_office(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for office"
        )
    
    # Check if case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Check if office exists
    office = db.query(Office).filter(Office.id == office_id).first()
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found"
        )
    
    # Initialize letter service
    letter_service = LetterService()
    
    # Save letter
    try:
        result = await letter_service.save_letter_to_case(
            letter_content=letter_content,
            case_id=case_id,
            office_id=office_id,
            filename=filename,
            format=format,
            letterhead=letterhead
        )
        
        # Create document record in database
        file_path = result["file_path"]
        file_format = result["format"]
        
        # Determine MIME type
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" if file_format == "docx" else "application/pdf"
        
        # Create document
        document = await document_service.save_document(
            db=db,
            file_path=file_path,
            filename=os.path.basename(file_path),
            user_id=current_user.id,
            office_id=office_id,
            case_id=case_id,
            mime_type=mime_type,
            document_type="letter"
        )
        
        return {
            "success": True,
            "document_id": document.id,
            "file_path": file_path,
            "format": file_format,
            "case_id": case_id,
            "office_id": office_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving letter: {str(e)}"
        )


@router.get("/letterhead")
async def get_letterhead(
    office_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get letterhead for office
    """
    # If office_id is provided, check if user has access
    if office_id:
        document_service = DocumentService(db)
        
        if not document_service.user_has_access_to_office(user_id=current_user.id, office_id=office_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions for office"
            )
        
        # Get office
        office = db.query(Office).filter(Office.id == office_id).first()
        if not office:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Office not found"
            )
        
        # Get letterhead from office settings
        letterhead = {}
        if office.settings:
            try:
                settings = json.loads(office.settings)
                if "letterhead" in settings:
                    letterhead = settings["letterhead"]
            except:
                pass
        
        return {
            "success": True,
            "office_id": office_id,
            "letterhead": letterhead
        }
    
    # If no office_id, get letterhead for all offices user has access to
    else:
        # Get offices user has access to
        offices = db.query(Office).filter(
            Office.id.in_(
                db.query(Office.id).join(
                    Office.users
                ).filter(
                    User.id == current_user.id
                )
            )
        ).all()
        
        # Get letterhead for each office
        office_letterheads = {}
        for office in offices:
            letterhead = {}
            if office.settings:
                try:
                    settings = json.loads(office.settings)
                    if "letterhead" in settings:
                        letterhead = settings["letterhead"]
                except:
                    pass
            
            office_letterheads[office.id] = {
                "office_id": office.id,
                "office_name": office.name,
                "letterhead": letterhead
            }
        
        return {
            "success": True,
            "office_letterheads": office_letterheads
        }


@router.post("/letterhead")
async def update_letterhead(
    office_id: int,
    letterhead: Dict[str, str],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update letterhead for office
    """
    # Check if user has access to office
    document_service = DocumentService(db)
    
    if not document_service.user_has_access_to_office(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for office"
        )
    
    # Get office
    office = db.query(Office).filter(Office.id == office_id).first()
    if not office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Office not found"
        )
    
    # Update letterhead in office settings
    settings = {}
    if office.settings:
        try:
            settings = json.loads(office.settings)
        except:
            pass
    
    settings["letterhead"] = letterhead
    office.settings = json.dumps(settings)
    
    db.commit()
    
    return {
        "success": True,
        "office_id": office_id,
        "letterhead": letterhead
    }
