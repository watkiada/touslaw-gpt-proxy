"""
API router for chat endpoints
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSession as ChatSessionSchema,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatMessage as ChatMessageSchema,
    ChatCompletionRequest,
    ChatCompletionResponse
)
from app.services.chat_service import AIChatService
from app.services.office_service import OfficeService
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.pdf_form_service import PDFFormService

router = APIRouter()


@router.get("/sessions", response_model=List[ChatSessionSchema])
async def read_chat_sessions(
    office_id: int,
    case_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve chat sessions.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Build query
    query = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.office_id == office_id
    )
    
    if case_id:
        query = query.filter(ChatSession.case_id == case_id)
    
    # Get chat sessions
    chat_sessions = query.offset(skip).limit(limit).all()
    return chat_sessions


@router.post("/sessions", response_model=ChatSessionSchema)
async def create_chat_session(
    chat_session_in: ChatSessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Create new chat session.
    """
    # Check if user has access to office
    office_service = OfficeService(db)
    if not office_service.user_has_access(user_id=current_user.id, office_id=chat_session_in.office_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Initialize services
    openai_service = OpenAIService()
    pinecone_service = PineconeService()
    
    # Initialize chat service
    chat_service = AIChatService(
        db=db,
        openai_service=openai_service,
        pinecone_service=pinecone_service
    )
    
    # Create chat session
    try:
        chat_session = await chat_service.create_chat_session(
            user_id=current_user.id,
            office_id=chat_session_in.office_id,
            ai_model_id=chat_session_in.ai_model_id,
            title=chat_session_in.title,
            case_id=chat_session_in.case_id,
            document_ids=chat_session_in.document_ids
        )
        return chat_session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chat session: {str(e)}"
        )


@router.get("/sessions/{chat_session_id}", response_model=ChatSessionSchema)
async def read_chat_session(
    chat_session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get chat session by ID.
    """
    chat_session = db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check if user has access to chat session
    if chat_session.user_id != current_user.id:
        # Check if user has access to office
        office_service = OfficeService(db)
        if not office_service.user_has_access(user_id=current_user.id, office_id=chat_session.office_id, role="admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return chat_session


@router.get("/sessions/{chat_session_id}/messages", response_model=List[ChatMessageSchema])
async def read_chat_messages(
    chat_session_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Retrieve chat messages for a session.
    """
    chat_session = db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check if user has access to chat session
    if chat_session.user_id != current_user.id:
        # Check if user has access to office
        office_service = OfficeService(db)
        if not office_service.user_has_access(user_id=current_user.id, office_id=chat_session.office_id, role="admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Get chat messages
    chat_messages = db.query(ChatMessage).filter(
        ChatMessage.chat_session_id == chat_session_id
    ).order_by(ChatMessage.id).offset(skip).limit(limit).all()
    
    return chat_messages


@router.post("/completion", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Process chat message and get AI response.
    """
    chat_session = db.query(ChatSession).filter(ChatSession.id == request.chat_session_id).first()
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Check if user has access to chat session
    if chat_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Initialize services
    openai_service = OpenAIService()
    pinecone_service = PineconeService()
    
    # Initialize PDF form service if needed
    pdf_form_service = None
    if request.form_fill_request and request.form_document_id:
        pdf_form_service = PDFFormService(db, openai_service, pinecone_service)
    
    # Initialize chat service
    chat_service = AIChatService(
        db=db,
        openai_service=openai_service,
        pinecone_service=pinecone_service,
        pdf_form_service=pdf_form_service
    )
    
    # Process message
    try:
        message, suggested_form_values = await chat_service.send_message(
            chat_session_id=request.chat_session_id,
            message_text=request.message,
            document_ids=request.document_ids,
            form_fill_request=request.form_fill_request,
            form_document_id=request.form_document_id
        )
        
        return ChatCompletionResponse(
            message=message,
            suggested_form_values=suggested_form_values
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )
