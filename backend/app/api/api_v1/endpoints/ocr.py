"""
API endpoints for OCR and data extraction
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
import os
import tempfile
import shutil

from app.api import deps
from app.models.models import User, Document
from app.services.ocr.ocr_service import OCRService
from app.services.ocr.data_extraction_service import DataExtractionService
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/process")
async def process_document_ocr(
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Process document with OCR
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to document
    document_service = DocumentService(db)
    if not document_service.user_has_access(user_id=current_user.id, document_id=document_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if document is already processed
    if document.is_ocr_processed:
        return {
            "success": True,
            "message": "Document already processed with OCR",
            "document_id": document_id
        }
    
    # Process document in background
    background_tasks.add_task(
        process_document_background,
        db=db,
        document_id=document_id,
        file_path=document.file_path
    )
    
    return {
        "success": True,
        "message": "Document OCR processing started",
        "document_id": document_id
    }


@router.post("/upload-and-process")
async def upload_and_process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    case_id: Optional[int] = None,
    folder_id: Optional[int] = None,
    office_id: int = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Upload document and process with OCR
    """
    if not office_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Office ID is required"
        )
    
    # Check if user has access to office
    document_service = DocumentService(db)
    if not document_service.user_has_access_to_office(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Save uploaded file
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Copy content
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Save document to storage
        document = await document_service.save_document(
            db=db,
            file_path=temp_path,
            filename=file.filename,
            user_id=current_user.id,
            office_id=office_id,
            case_id=case_id,
            folder_id=folder_id
        )
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            db=db,
            document_id=document.id,
            file_path=document.file_path
        )
        
        return {
            "success": True,
            "message": "Document uploaded and OCR processing started",
            "document_id": document.id
        }
    
    except Exception as e:
        # Clean up temp file
        if 'temp_path' in locals():
            os.unlink(temp_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading document: {str(e)}"
        )
    finally:
        # Close file
        file.file.close()


@router.get("/status/{document_id}")
async def get_ocr_status(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get OCR processing status for document
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to document
    document_service = DocumentService(db)
    if not document_service.user_has_access(user_id=current_user.id, document_id=document_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return {
        "document_id": document_id,
        "is_ocr_processed": document.is_ocr_processed,
        "is_indexed": document.is_indexed
    }


@router.get("/extract-form-fields/{document_id}")
async def extract_form_fields(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Extract form fields from document
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to document
    document_service = DocumentService(db)
    if not document_service.user_has_access(user_id=current_user.id, document_id=document_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Extract form fields
    try:
        ocr_service = OCRService()
        result = await ocr_service.extract_form_fields(document.file_path)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error extracting form fields: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "form_fields": result['form_fields']
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting form fields: {str(e)}"
        )


@router.get("/extract-data/{document_id}")
async def extract_document_data(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Extract structured data from document
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to document
    document_service = DocumentService(db)
    if not document_service.user_has_access(user_id=current_user.id, document_id=document_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Extract data
    try:
        extraction_service = DataExtractionService()
        result = await extraction_service.extract_data_from_document(document.file_path)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error extracting data: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "extracted_data": result['extracted_data']
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting data: {str(e)}"
        )


@router.get("/categorize/{document_id}")
async def categorize_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Categorize document type
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has access to document
    document_service = DocumentService(db)
    if not document_service.user_has_access(user_id=current_user.id, document_id=document_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Categorize document
    try:
        extraction_service = DataExtractionService()
        result = await extraction_service.categorize_document(document.file_path)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error categorizing document: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "category": result['category'],
            "confidence": result['confidence'],
            "subcategory": result.get('subcategory'),
            "keywords": result.get('keywords', [])
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error categorizing document: {str(e)}"
        )


async def process_document_background(db: Session, document_id: int, file_path: str):
    """
    Process document with OCR in background
    """
    try:
        # Initialize services
        ocr_service = OCRService()
        document_service = DocumentService(db)
        
        # Process document with OCR
        ocr_result = await ocr_service.process_document(file_path)
        
        if not ocr_result['success']:
            # Update document status
            document_service.update_document_status(
                document_id=document_id,
                is_ocr_processed=False,
                ocr_error=ocr_result.get('error', 'OCR processing failed')
            )
            return
        
        # Extract metadata
        extraction_service = DataExtractionService()
        extraction_result = await extraction_service.extract_data_from_document(file_path)
        
        # Update document with OCR results
        document_service.update_document_with_ocr_results(
            document_id=document_id,
            ocr_text=ocr_result['text'],
            metadata=extraction_result.get('extracted_data', {})
        )
        
        # Update document status
        document_service.update_document_status(
            document_id=document_id,
            is_ocr_processed=True
        )
    
    except Exception as e:
        # Update document status with error
        document_service = DocumentService(db)
        document_service.update_document_status(
            document_id=document_id,
            is_ocr_processed=False,
            ocr_error=str(e)
        )
