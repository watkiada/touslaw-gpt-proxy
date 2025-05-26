"""
API endpoints for AI chat and document interaction
"""
from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import json

from app.api import deps
from app.models.models import User, Document, Chat, ChatMessage
from app.services.ai.openai_service import OpenAIService
from app.services.ai.pinecone_service import PineconeService
from app.services.ai.chat_service import AIChatService
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/chat")
async def chat_with_ai(
    message: str,
    chat_id: Optional[int] = None,
    case_id: Optional[int] = None,
    office_id: Optional[int] = None,
    stream: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Chat with AI using document context
    """
    # Initialize services
    chat_service = AIChatService()
    
    # Get or create chat
    if chat_id:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
        
        # Check if user has access to chat
        if chat.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    else:
        # Create new chat
        chat = Chat(
            user_id=current_user.id,
            office_id=office_id,
            case_id=case_id,
            title=message[:50] + "..." if len(message) > 50 else message
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    # Get chat history
    chat_messages = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    chat_history = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in chat_messages
    ]
    
    # Save user message
    user_message = ChatMessage(
        chat_id=chat.id,
        role="user",
        content=message
    )
    db.add(user_message)
    db.commit()
    
    # Generate AI response
    try:
        if stream:
            # For streaming, return generator
            async def response_generator():
                async for chunk in await chat_service.chat(
                    message=message,
                    chat_history=chat_history,
                    user_id=current_user.id,
                    office_id=office_id,
                    case_id=case_id,
                    stream=True
                ):
                    yield {"chunk": chunk}
                
                # Save complete response at the end
                complete_response = "".join([chunk async for chunk in await chat_service.chat(
                    message=message,
                    chat_history=chat_history,
                    user_id=current_user.id,
                    office_id=office_id,
                    case_id=case_id,
                    stream=False
                )])
                
                # Save AI message
                ai_message = ChatMessage(
                    chat_id=chat.id,
                    role="assistant",
                    content=complete_response
                )
                db.add(ai_message)
                db.commit()
            
            return response_generator()
        else:
            # For non-streaming, return complete response
            response = await chat_service.chat(
                message=message,
                chat_history=chat_history,
                user_id=current_user.id,
                office_id=office_id,
                case_id=case_id
            )
            
            # Save AI message
            ai_message = ChatMessage(
                chat_id=chat.id,
                role="assistant",
                content=response
            )
            db.add(ai_message)
            db.commit()
            
            return {
                "chat_id": chat.id,
                "message": response
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating chat response: {str(e)}"
        )


@router.get("/chats")
async def get_chats(
    office_id: Optional[int] = None,
    case_id: Optional[int] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get user's chats
    """
    query = db.query(Chat).filter(Chat.user_id == current_user.id)
    
    if office_id:
        query = query.filter(Chat.office_id == office_id)
    
    if case_id:
        query = query.filter(Chat.case_id == case_id)
    
    chats = query.order_by(Chat.updated_at.desc()).all()
    
    return {
        "chats": [
            {
                "id": chat.id,
                "title": chat.title,
                "created_at": chat.created_at,
                "updated_at": chat.updated_at,
                "office_id": chat.office_id,
                "case_id": chat.case_id
            }
            for chat in chats
        ]
    }


@router.get("/chat/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get chat messages
    """
    # Check if chat exists
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user has access to chat
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get chat messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return {
        "chat_id": chat_id,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }


@router.post("/fill-form")
async def fill_form_with_ai(
    form_fields: List[Dict[str, str]],
    case_id: Optional[int] = None,
    office_id: Optional[int] = None,
    document_ids: Optional[List[int]] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Fill form fields with AI using document context
    """
    # Initialize services
    chat_service = AIChatService()
    
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
    
    # Check if user has access to documents
    if document_ids:
        document_service = DocumentService(db)
        
        for doc_id in document_ids:
            if not document_service.user_has_access(user_id=current_user.id, document_id=doc_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions for document {doc_id}"
                )
    
    # Fill form fields
    try:
        field_values = await chat_service.fill_form_with_ai(
            form_fields=form_fields,
            case_id=case_id,
            office_id=office_id,
            document_ids=document_ids
        )
        
        return {
            "success": True,
            "field_values": field_values
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filling form: {str(e)}"
        )


@router.post("/generate-letter")
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
    # Initialize services
    chat_service = AIChatService()
    
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
    
    # Generate letter
    try:
        letter_content = await chat_service.generate_letter(
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


@router.post("/index-document")
async def index_document(
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Index document in vector database
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
    
    # Check if document is OCR processed
    if not document.is_ocr_processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be OCR processed before indexing"
        )
    
    # Check if document is already indexed
    if document.is_indexed:
        return {
            "success": True,
            "message": "Document already indexed",
            "document_id": document_id
        }
    
    # Index document in background
    background_tasks.add_task(
        index_document_background,
        db=db,
        document_id=document_id
    )
    
    return {
        "success": True,
        "message": "Document indexing started",
        "document_id": document_id
    }


@router.delete("/delete-document-index")
async def delete_document_index(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Delete document from vector database
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
    
    # Delete document from vector database
    try:
        pinecone_service = PineconeService()
        success = await pinecone_service.delete_document(str(document_id))
        
        if success:
            # Update document status
            document.is_indexed = False
            db.commit()
            
            return {
                "success": True,
                "message": "Document deleted from index",
                "document_id": document_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting document from index"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document from index: {str(e)}"
        )


@router.post("/search-documents")
async def search_documents(
    query: str,
    office_id: Optional[int] = None,
    case_id: Optional[int] = None,
    top_k: int = 5,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Search documents in vector database
    """
    # Initialize services
    pinecone_service = PineconeService()
    
    # Prepare filter
    filter_dict = {}
    
    if office_id:
        filter_dict["office_id"] = office_id
    
    if case_id:
        filter_dict["case_id"] = case_id
    
    # Search documents
    try:
        search_results = await pinecone_service.search_documents(
            query=query,
            filter=filter_dict,
            top_k=top_k
        )
        
        # Format results
        formatted_results = []
        for result in search_results:
            if "metadata" in result:
                metadata = result["metadata"]
                
                # Get document details
                document_id = metadata.get("document_id")
                if document_id:
                    document = db.query(Document).filter(Document.id == document_id).first()
                    
                    if document and document_service.user_has_access(user_id=current_user.id, document_id=document.id):
                        formatted_results.append({
                            "document_id": document.id,
                            "filename": document.filename,
                            "score": result["score"],
                            "chunk_text": metadata.get("chunk_text", ""),
                            "chunk_index": metadata.get("chunk_index", 0),
                            "total_chunks": metadata.get("total_chunks", 1)
                        })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}"
        )


@router.get("/summarize-document/{document_id}")
async def summarize_document(
    document_id: int,
    max_length: int = 1000,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Summarize document with AI
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
    
    # Check if document has OCR text
    if not document.ocr_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no OCR text"
        )
    
    # Summarize document
    try:
        openai_service = OpenAIService()
        summary = await openai_service.summarize_document(
            text=document.ocr_text,
            max_length=max_length
        )
        
        return {
            "success": True,
            "document_id": document_id,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summarizing document: {str(e)}"
        )


async def index_document_background(db: Session, document_id: int):
    """
    Index document in vector database in background
    """
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error(f"Document not found: {document_id}")
            return
        
        # Initialize services
        pinecone_service = PineconeService()
        document_service = DocumentService(db)
        
        # Prepare metadata
        metadata = {
            "document_id": str(document_id),
            "filename": document.filename,
            "title": document.filename,
            "office_id": document.office_id,
            "case_id": document.case_id,
            "folder_id": document.folder_id,
            "mime_type": document.mime_type,
            "created_at": document.created_at.isoformat() if document.created_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None
        }
        
        # Add extracted metadata if available
        if document.metadata:
            try:
                doc_metadata = json.loads(document.metadata)
                metadata.update(doc_metadata)
            except:
                pass
        
        # Index document
        success = await pinecone_service.index_document(
            document_id=str(document_id),
            document_text=document.ocr_text,
            metadata=metadata
        )
        
        # Update document status
        document_service.update_document_status(
            document_id=document_id,
            is_indexed=success
        )
    
    except Exception as e:
        logger.error(f"Error indexing document {document_id}: {str(e)}")
        
        # Update document status with error
        document_service = DocumentService(db)
        document_service.update_document_status(
            document_id=document_id,
            is_indexed=False,
            indexing_error=str(e)
        )
