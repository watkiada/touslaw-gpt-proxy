"""
API router for documents endpoints
"""
from typing import Any, List, Optional
import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, Document
from app.schemas.document import (
    Document as DocumentSchema, 
    DocumentCreate, 
    DocumentUpdate,
    DocumentWithMetadata,
    PDFForm,
    PDFFormFillRequest,
    PDFFormFillResponse
)
from app.services.document_service import DocumentProcessor
from app.services.pdf_form_service import PDFFormService
from app.services.office_service import OfficeService
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.ocr_service import OCRService
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[DocumentSchema])
async def read_documents(
    office_id: int,
    case_id: Optional[int] = None,
    folder_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve documents.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Build query
    query = db.query(Document).filter(Document.office_id == office_id)
    
    if case_id:
        query = query.filter(Document.case_id == case_id)
    
    if folder_id:
        query = query.filter(Document.folder_id == folder_id)
    
    # Get documents
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    office_id: int = Form(...),
    case_id: Optional[int] = Form(None),
    folder_id: Optional[int] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Upload a document.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check file size
    file_size = 0
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Seek back to start
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB"
        )
    
    # Create storage path
    office_path = os.path.join(settings.STORAGE_PATH, "offices", str(office_id))
    os.makedirs(office_path, exist_ok=True)
    
    if case_id:
        case_path = os.path.join(office_path, "cases", str(case_id), "documents")
        os.makedirs(case_path, exist_ok=True)
        save_path = case_path
    elif folder_id:
        folder_path = os.path.join(office_path, "folders", str(folder_id))
        os.makedirs(folder_path, exist_ok=True)
        save_path = folder_path
    else:
        shared_path = os.path.join(office_path, "shared", "documents")
        os.makedirs(shared_path, exist_ok=True)
        save_path = shared_path
    
    # Generate unique filename
    filename = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    full_path = os.path.join(save_path, filename + file_extension)
    
    # Save file
    with open(full_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    document_in = DocumentCreate(
        original_filename=file.filename,
        file_path=full_path,
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        office_id=office_id,
        case_id=case_id,
        folder_id=folder_id
    )
    
    # Create document
    document = Document(
        filename=filename + file_extension,
        original_filename=document_in.original_filename,
        file_path=document_in.file_path,
        file_size=document_in.file_size,
        mime_type=document_in.mime_type,
        office_id=document_in.office_id,
        case_id=document_in.case_id,
        folder_id=document_in.folder_id,
        is_ocr_processed=False,
        is_indexed=False,
        created_by_id=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document in background
    background_tasks.add_task(
        process_document_background,
        document_id=document.id,
        db=db
    )
    
    return document


@router.get("/{document_id}", response_model=DocumentWithMetadata)
async def read_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get document by ID.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=document.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return document


@router.delete("/{document_id}", response_model=DocumentSchema)
async def delete_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete document.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=document.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception:
        pass
    
    # Delete document
    db.delete(document)
    db.commit()
    
    return document


@router.get("/{document_id}/form", response_model=PDFForm)
async def get_pdf_form(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get PDF form fields.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=document.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if document is a PDF
    if not document.mime_type.lower().endswith('pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not a PDF"
        )
    
    # Initialize PDF form service
    pdf_form_service = PDFFormService(db)
    
    # Extract form fields
    try:
        form = await pdf_form_service.extract_form_fields(document_id=document_id)
        return form
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting form fields: {str(e)}"
        )


@router.post("/{document_id}/fill-form", response_model=PDFFormFillResponse)
async def fill_pdf_form(
    document_id: int,
    form_data: PDFFormFillRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Fill PDF form with provided values.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=document.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if document is a PDF
    if not document.mime_type.lower().endswith('pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not a PDF"
        )
    
    # Initialize PDF form service
    pdf_form_service = PDFFormService(db)
    
    # Fill form
    try:
        # Update request with document ID
        form_data.document_id = document_id
        
        # Fill form
        filled_document = await pdf_form_service.fill_form(request=form_data)
        
        return PDFFormFillResponse(
            filled_document_id=filled_document.id,
            success=True,
            message="Form filled successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filling form: {str(e)}"
        )


@router.post("/{document_id}/suggest-form-values")
async def suggest_form_values(
    document_id: int,
    case_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Suggest values for form fields based on case documents.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=document.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if document is a PDF
    if not document.mime_type.lower().endswith('pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not a PDF"
        )
    
    # Initialize services
    openai_service = OpenAIService()
    pinecone_service = PineconeService()
    pdf_form_service = PDFFormService(db, openai_service, pinecone_service)
    
    # Suggest form values
    try:
        suggestions = await pdf_form_service.suggest_form_values(
            document_id=document_id,
            case_id=case_id or document.case_id
        )
        return suggestions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error suggesting form values: {str(e)}"
        )


async def process_document_background(document_id: int, db: Session) -> None:
    """
    Process document in background
    
    Args:
        document_id: Document ID
        db: Database session
    """
    # Initialize services
    openai_service = OpenAIService()
    pinecone_service = PineconeService()
    ocr_service = OCRService()
    
    # Initialize document processor
    document_processor = DocumentProcessor(
        db=db,
        openai_service=openai_service,
        pinecone_service=pinecone_service,
        ocr_service=ocr_service
    )
    
    # Process document
    try:
        await document_processor.process_document(document_id=document_id)
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
