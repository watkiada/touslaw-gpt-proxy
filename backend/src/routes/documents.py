"""
WatkiBot Documents Routes - Simplified Version

This module defines the documents API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("/")
def read_documents(
    case_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents, optionally filtered by case_id."""
    # Simplified version - just return mock data
    documents = [
        {
            "id": 1,
            "title": "Initial Filing",
            "document_type": "Legal Brief",
            "case_id": 1,
            "created_at": "2025-05-20T10:30:00Z"
        },
        {
            "id": 2,
            "title": "Client Statement",
            "document_type": "Testimony",
            "case_id": 1,
            "created_at": "2025-05-21T14:00:00Z"
        },
        {
            "id": 3,
            "title": "Will Document",
            "document_type": "Legal Document",
            "case_id": 2,
            "created_at": "2025-05-22T15:00:00Z"
        }
    ]
    
    if case_id:
        documents = [doc for doc in documents if doc["case_id"] == case_id]
        
    return documents

@router.get("/{document_id}")
def read_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document."""
    # Simplified version - just return mock data
    return {
        "id": document_id,
        "title": f"Document #{document_id}",
        "content": "This is the content of the document. It contains legal information relevant to the case.",
        "document_type": "Legal Document",
        "case_id": 1,
        "created_at": "2025-05-20T10:30:00Z"
    }
