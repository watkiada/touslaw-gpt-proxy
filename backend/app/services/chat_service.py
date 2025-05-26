"""
AI chat service for document-based conversations
"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import ChatSession, ChatMessage, Document, ChatSessionDocument
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.pdf_form_service import PDFFormService


class AIChatService:
    """Service for AI chat functionality"""
    
    def __init__(
        self,
        db: Session,
        openai_service: OpenAIService,
        pinecone_service: PineconeService,
        pdf_form_service: Optional[PDFFormService] = None
    ):
        """
        Initialize AI chat service
        
        Args:
            db: Database session
            openai_service: OpenAI service for AI chat
            pinecone_service: Pinecone service for document retrieval
            pdf_form_service: Optional PDF form service for form filling
        """
        self.db = db
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
        self.pdf_form_service = pdf_form_service
        self.max_context_chunks = settings.MAX_CONTEXT_CHUNKS
    
    async def create_chat_session(
        self,
        user_id: int,
        office_id: int,
        ai_model_id: int,
        title: Optional[str] = None,
        case_id: Optional[int] = None,
        document_ids: Optional[List[int]] = None
    ) -> ChatSession:
        """
        Create a new chat session
        
        Args:
            user_id: User ID
            office_id: Office ID
            ai_model_id: AI model ID
            title: Optional chat session title
            case_id: Optional case ID
            document_ids: Optional list of document IDs
            
        Returns:
            Created chat session
            
        Raises:
            ValueError: If creation fails
        """
        try:
            # Create chat session
            chat_session = ChatSession(
                user_id=user_id,
                office_id=office_id,
                ai_model_id=ai_model_id,
                title=title,
                case_id=case_id
            )
            self.db.add(chat_session)
            self.db.commit()
            self.db.refresh(chat_session)
            
            # Add documents if provided
            if document_ids:
                for document_id in document_ids:
                    # Check if document exists
                    document = self.db.query(Document).filter(Document.id == document_id).first()
                    if not document:
                        continue
                    
                    # Add document to chat session
                    chat_session_document = ChatSessionDocument(
                        chat_session_id=chat_session.id,
                        document_id=document_id
                    )
                    self.db.add(chat_session_document)
                
                self.db.commit()
            
            # Add system message
            system_message = ChatMessage(
                chat_session_id=chat_session.id,
                role="system",
                content="You are an AI assistant for document analysis and legal research. You can answer questions about documents, summarize content, and help with legal research."
            )
            self.db.add(system_message)
            self.db.commit()
            
            return chat_session
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error creating chat session: {str(e)}")
    
    async def send_message(
        self,
        chat_session_id: int,
        message_text: str,
        document_ids: Optional[List[int]] = None,
        form_fill_request: bool = False,
        form_document_id: Optional[int] = None
    ) -> Tuple[ChatMessage, Optional[Dict]]:
        """
        Process user message and generate AI response
        
        Args:
            chat_session_id: Chat session ID
            message_text: User message text
            document_ids: Optional list of document IDs to include in context
            form_fill_request: Whether this is a form fill request
            form_document_id: Optional document ID of the form to fill
            
        Returns:
            Tuple of (AI response message, suggested form values if requested)
            
        Raises:
            ValueError: If processing fails
        """
        try:
            # Get chat session
            chat_session = self.db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
            if not chat_session:
                raise ValueError(f"Chat session with ID {chat_session_id} not found")
            
            # Add user message
            user_message = ChatMessage(
                chat_session_id=chat_session_id,
                role="user",
                content=message_text
            )
            self.db.add(user_message)
            self.db.commit()
            self.db.refresh(user_message)
            
            # Get chat history
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.chat_session_id == chat_session_id
            ).order_by(ChatMessage.id).all()
            
            # Format messages for OpenAI
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Get document context
            context = await self._get_document_context(
                chat_session_id=chat_session_id,
                query=message_text,
                additional_document_ids=document_ids
            )
            
            # Add context to system message
            if context:
                # Find system message
                system_message_index = next(
                    (i for i, msg in enumerate(formatted_messages) if msg["role"] == "system"),
                    None
                )
                
                if system_message_index is not None:
                    # Update system message with context
                    formatted_messages[system_message_index]["content"] += f"\n\nRelevant document content:\n{context}"
                else:
                    # Add new system message with context
                    formatted_messages.insert(0, {
                        "role": "system",
                        "content": f"You are an AI assistant for document analysis. Here is relevant document content:\n{context}"
                    })
            
            # Handle form fill request
            suggested_form_values = None
            if form_fill_request and form_document_id and self.pdf_form_service:
                # Add form fill instructions
                formatted_messages.append({
                    "role": "system",
                    "content": "The user is asking for help filling out a PDF form. Please extract the necessary information from the context and suggest appropriate values for the form fields."
                })
                
                # Get AI response
                ai_response = await self.openai_service.chat_completion(
                    messages=formatted_messages
                )
                
                # Get form field suggestions
                suggested_form_values = await self.pdf_form_service.suggest_form_values(
                    document_id=form_document_id,
                    case_id=chat_session.case_id
                )
            else:
                # Get AI response
                ai_response = await self.openai_service.chat_completion(
                    messages=formatted_messages
                )
            
            # Add assistant message
            assistant_message = ChatMessage(
                chat_session_id=chat_session_id,
                role="assistant",
                content=ai_response
            )
            self.db.add(assistant_message)
            self.db.commit()
            self.db.refresh(assistant_message)
            
            return assistant_message, suggested_form_values
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error processing message: {str(e)}")
    
    async def _get_document_context(
        self,
        chat_session_id: int,
        query: str,
        additional_document_ids: Optional[List[int]] = None
    ) -> str:
        """
        Get relevant document context for a query
        
        Args:
            chat_session_id: Chat session ID
            query: Query text
            additional_document_ids: Optional additional document IDs
            
        Returns:
            Relevant document context
            
        Raises:
            ValueError: If retrieval fails
        """
        try:
            # Get chat session
            chat_session = self.db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
            if not chat_session:
                raise ValueError(f"Chat session with ID {chat_session_id} not found")
            
            # Get document IDs from chat session
            document_ids = []
            
            # Get documents from chat session
            chat_session_documents = self.db.query(ChatSessionDocument).filter(
                ChatSessionDocument.chat_session_id == chat_session_id
            ).all()
            
            document_ids.extend([doc.document_id for doc in chat_session_documents])
            
            # Add additional document IDs
            if additional_document_ids:
                document_ids.extend(additional_document_ids)
            
            # If no documents, return empty context
            if not document_ids:
                return ""
            
            # Get embedding for query
            query_embedding = await self.openai_service.generate_embeddings([query])
            
            # Search for relevant chunks
            filter_params = {
                "document_id": {"$in": document_ids}
            }
            
            results = await self.pinecone_service.query_vectors(
                query_vector=query_embedding[0],
                top_k=self.max_context_chunks,
                filter=filter_params
            )
            
            # Get chunk content
            chunk_ids = [result["id"] for result in results]
            chunks = self.db.query(DocumentChunk).filter(DocumentChunk.embedding_id.in_(chunk_ids)).all()
            
            # Build context from chunks
            context_parts = []
            for chunk in chunks:
                # Get document info
                document = self.db.query(Document).filter(Document.id == chunk.document_id).first()
                if document:
                    context_parts.append(f"Document: {document.original_filename}\n{chunk.content}\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            raise ValueError(f"Error getting document context: {str(e)}")
