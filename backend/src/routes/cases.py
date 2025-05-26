"""
WatkiBot Cases Routes - Simplified Version

This module defines the cases API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/cases", tags=["cases"])

@router.get("/")
def read_cases(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all cases."""
    # Simplified version - just return mock data
    return [
        {
            "id": 1,
            "title": "Smith vs. Jones",
            "description": "Contract dispute case",
            "status": "Open",
            "created_at": "2025-05-20T10:00:00Z"
        },
        {
            "id": 2,
            "title": "Johnson Estate",
            "description": "Estate planning and will execution",
            "status": "In Progress",
            "created_at": "2025-05-22T14:30:00Z"
        }
    ]

@router.get("/{case_id}")
def read_case(
    case_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific case."""
    # Simplified version - just return mock data
    return {
        "id": case_id,
        "title": f"Case #{case_id}",
        "description": "This is a sample case description",
        "status": "Open",
        "created_at": "2025-05-20T10:00:00Z",
        "documents": [
            {
                "id": 1,
                "title": "Initial Filing",
                "document_type": "Legal Brief"
            },
            {
                "id": 2,
                "title": "Client Statement",
                "document_type": "Testimony"
            }
        ]
    }
