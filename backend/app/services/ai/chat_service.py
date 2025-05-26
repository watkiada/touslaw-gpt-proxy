"""
AI chat service for document-based conversations
"""
import os
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime

from app.core.config import settings
from app.services.ai.openai_service import OpenAIService
from app.services.ai.pinecone_service import PineconeService

logger = logging.getLogger(__name__)

class AIChatService:
    """
    Service for AI chat with document context
    """
    
    def __init__(self):
        """
        Initialize AI chat service
        """
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        
        # System prompts
        self.default_system_prompt = """You are Watkibot Law Assistant, an AI assistant for law firms. 
You help with document management, case organization, and answering legal questions based on the firm's documents.
Always be professional, accurate, and helpful. If you're unsure about something, acknowledge your limitations.
When answering questions, cite specific documents or sources when possible."""
    
    async def chat(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_id: int,
        office_id: Optional[int] = None,
        case_id: Optional[int] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, AsyncIterator]:
        """
        Chat with AI using document context
        
        Args:
            message: User message
            chat_history: Previous chat messages
            user_id: User ID
            office_id: Office ID (optional)
            case_id: Case ID (optional)
            system_prompt: Custom system prompt (optional)
            stream: Whether to stream the response
            
        Returns:
            AI response or async iterator for streaming
        """
        # Get relevant document context
        context_docs = await self._retrieve_relevant_context(
            query=message,
            user_id=user_id,
            office_id=office_id,
            case_id=case_id
        )
        
        # Prepare messages for chat
        messages = self._prepare_chat_messages(
            message=message,
            chat_history=chat_history,
            context_docs=context_docs,
            system_prompt=system_prompt
        )
        
        # Generate chat response
        if stream:
            response_stream = await self.openai_service.chat_completion(
                messages=messages,
                stream=True
            )
            return self.openai_service.process_streaming_response(response_stream)
        else:
            response = await self.openai_service.chat_completion(
                messages=messages
            )
            return response["content"]
    
    async def _retrieve_relevant_context(
        self,
        query: str,
        user_id: int,
        office_id: Optional[int] = None,
        case_id: Optional[int] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document context for query
        
        Args:
            query: User query
            user_id: User ID
            office_id: Office ID (optional)
            case_id: Case ID (optional)
            max_results: Maximum number of results
            
        Returns:
            List of relevant document chunks
        """
        # Prepare filter
        filter_dict = {}
        
        if office_id:
            filter_dict["office_id"] = office_id
        
        if case_id:
            filter_dict["case_id"] = case_id
        
        # Search documents
        search_results = await self.pinecone_service.search_documents(
            query=query,
            filter=filter_dict,
            top_k=max_results
        )
        
        return search_results
    
    def _prepare_chat_messages(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        context_docs: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for chat
        
        Args:
            message: User message
            chat_history: Previous chat messages
            context_docs: Relevant document context
            system_prompt: Custom system prompt (optional)
            
        Returns:
            List of messages for chat
        """
        # Use default system prompt if not provided
        if not system_prompt:
            system_prompt = self.default_system_prompt
        
        # Prepare context from documents
        context_text = ""
        if context_docs:
            context_parts = []
            for i, doc in enumerate(context_docs):
                if "metadata" in doc and "chunk_text" in doc["metadata"]:
                    doc_text = doc["metadata"]["chunk_text"]
                    doc_id = doc["metadata"].get("document_id", "unknown")
                    doc_title = doc["metadata"].get("title", f"Document {doc_id}")
                    
                    context_parts.append(f"[Document: {doc_title}]\n{doc_text}")
            
            context_text = "\n\n---\n\n".join(context_parts)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add chat history (limited to last 10 messages)
        if chat_history:
            for msg in chat_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add context and user message
        if context_text:
            user_content = f"I have access to the following document excerpts that might be relevant to your question:\n\n{context_text}\n\nBased on this information, please answer: {message}"
        else:
            user_content = message
        
        messages.append({"role": "user", "content": user_content})
        
        return messages
    
    async def fill_form_with_ai(
        self,
        form_fields: List[Dict[str, str]],
        case_id: Optional[int] = None,
        office_id: Optional[int] = None,
        document_ids: Optional[List[int]] = None
    ) -> Dict[str, str]:
        """
        Fill form fields with AI using document context
        
        Args:
            form_fields: List of form fields
            case_id: Case ID (optional)
            office_id: Office ID (optional)
            document_ids: List of document IDs to use as context (optional)
            
        Returns:
            Dictionary with field values
        """
        # Prepare context query from form fields
        field_names = [field["name"] for field in form_fields]
        query = "Form fields: " + ", ".join(field_names)
        
        # Get relevant document context
        filter_dict = {}
        
        if office_id:
            filter_dict["office_id"] = office_id
        
        if case_id:
            filter_dict["case_id"] = case_id
        
        if document_ids:
            # This assumes Pinecone supports 'in' operator for filters
            # Adjust based on actual Pinecone filter capabilities
            filter_dict["document_id"] = {"$in": document_ids}
        
        # Search documents
        search_results = await self.pinecone_service.search_documents(
            query=query,
            filter=filter_dict,
            top_k=10
        )
        
        # Extract document text from search results
        document_context = ""
        if search_results:
            context_parts = []
            for doc in search_results:
                if "metadata" in doc and "chunk_text" in doc["metadata"]:
                    context_parts.append(doc["metadata"]["chunk_text"])
            
            document_context = "\n\n---\n\n".join(context_parts)
        
        # Fill form fields
        field_values = await self.openai_service.fill_pdf_form(
            form_fields=form_fields,
            document_context=document_context
        )
        
        return field_values
    
    async def generate_letter(
        self,
        letter_type: str,
        recipient: str,
        subject: str,
        content_instructions: str,
        letterhead: Optional[Dict[str, str]] = None,
        case_id: Optional[int] = None,
        office_id: Optional[int] = None
    ) -> str:
        """
        Generate letter with AI using document context
        
        Args:
            letter_type: Type of letter
            recipient: Letter recipient
            subject: Letter subject
            content_instructions: Instructions for letter content
            letterhead: Letterhead information (optional)
            case_id: Case ID (optional)
            office_id: Office ID (optional)
            
        Returns:
            Generated letter
        """
        # Get relevant document context
        context_docs = await self._retrieve_relevant_context(
            query=f"{letter_type} letter {subject} {content_instructions}",
            user_id=0,  # Not used in this context
            office_id=office_id,
            case_id=case_id,
            max_results=5
        )
        
        # Extract document text from search results
        document_context = ""
        if context_docs:
            context_parts = []
            for doc in context_docs:
                if "metadata" in doc and "chunk_text" in doc["metadata"]:
                    context_parts.append(doc["metadata"]["chunk_text"])
            
            document_context = "\n\n---\n\n".join(context_parts)
        
        # Prepare letterhead
        letterhead_text = ""
        if letterhead:
            letterhead_text = f"""
{letterhead.get('firm_name', 'Law Firm')}
{letterhead.get('address', '')}
{letterhead.get('city', '')}, {letterhead.get('state', '')} {letterhead.get('zipCode', '')}
Phone: {letterhead.get('phone', '')} | Email: {letterhead.get('email', '')}
Website: {letterhead.get('website', '')}
"""
        
        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Prepare letter template
        letter_template = f"""
{letterhead_text}

{current_date}

{recipient}

Subject: {subject}

Dear [Recipient Name],

[Letter Content]

Sincerely,

[Attorney Name]
[Title]
"""
        
        # Prepare prompt for letter generation
        messages = [
            {"role": "system", "content": f"You are a legal assistant that generates professional {letter_type} letters for law firms. Use formal language and appropriate legal terminology."},
            {"role": "user", "content": f"""
Please generate a {letter_type} letter with the following details:

Recipient: {recipient}
Subject: {subject}
Instructions: {content_instructions}

Use this document context for relevant information:
{document_context}

Follow this template:
{letter_template}

Replace [Recipient Name], [Letter Content], [Attorney Name], and [Title] with appropriate content based on the instructions and context.
"""}
        ]
        
        # Generate letter
        response = await self.openai_service.chat_completion(messages=messages)
        
        return response["content"]
