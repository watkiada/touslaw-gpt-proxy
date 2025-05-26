"""
OpenAI service for AI integration
"""
import os
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Service for OpenAI API integration
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI service
        
        Args:
            api_key: OpenAI API key (optional, defaults to settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not provided")
        
        # Configure OpenAI client
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Default parameters
        self.default_model = settings.OPENAI_MODEL or "gpt-4"
        self.default_temperature = settings.OPENAI_TEMPERATURE or 0.7
        self.default_max_tokens = settings.OPENAI_MAX_TOKENS or 4000
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError))
    )
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        if not texts:
            return []
        
        try:
            # Call OpenAI embeddings API
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            
            return embeddings
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.APIError, openai.APIConnectionError, openai.RateLimitError))
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], AsyncIterator]:
        """
        Generate chat completion
        
        Args:
            messages: List of messages
            model: Model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Chat completion response or async iterator for streaming
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        # Use default parameters if not provided
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        try:
            # Call OpenAI chat completion API
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return response
            else:
                return {
                    "content": response.choices[0].message.content,
                    "role": response.choices[0].message.role,
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
        
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            raise
    
    async def process_streaming_response(self, stream):
        """
        Process streaming response from OpenAI
        
        Args:
            stream: Streaming response from OpenAI
            
        Returns:
            Full response content
        """
        content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content
        
        return content
    
    async def summarize_document(self, text: str, max_length: int = 1000) -> str:
        """
        Summarize document text
        
        Args:
            text: Document text
            max_length: Maximum length of summary
            
        Returns:
            Document summary
        """
        # Truncate text if too long
        if len(text) > 15000:
            text = text[:15000] + "..."
        
        # Create prompt for summarization
        messages = [
            {"role": "system", "content": "You are a legal assistant that summarizes documents accurately and concisely. Focus on key information, parties involved, dates, and legal implications."},
            {"role": "user", "content": f"Please summarize the following document in a concise manner, highlighting the most important information. Keep the summary under {max_length} characters.\n\nDocument:\n{text}"}
        ]
        
        # Generate summary
        response = await self.chat_completion(messages=messages)
        
        return response["content"]
    
    async def extract_key_information(self, text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract key information from document text
        
        Args:
            text: Document text
            document_type: Type of document (optional)
            
        Returns:
            Dictionary with extracted information
        """
        # Truncate text if too long
        if len(text) > 15000:
            text = text[:15000] + "..."
        
        # Create prompt based on document type
        system_prompt = "You are a legal assistant that extracts key information from documents accurately."
        
        if document_type:
            system_prompt += f" This is a {document_type} document."
        
        user_prompt = "Please extract the following information from this document and format it as a JSON object with these fields: parties_involved, dates, locations, monetary_values, legal_references, key_terms, action_items.\n\nDocument:\n" + text
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Generate extraction
        response = await self.chat_completion(messages=messages)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            content = response["content"]
            
            # Find JSON block
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                extracted_info = json.loads(json_str)
            else:
                # Fallback if JSON not properly formatted
                extracted_info = {"error": "Could not parse JSON response", "raw_response": content}
            
            return extracted_info
        
        except Exception as e:
            logger.error(f"Error parsing extraction response: {str(e)}")
            return {"error": str(e), "raw_response": response["content"]}
    
    async def generate_document_from_template(
        self,
        template: str,
        context: Dict[str, Any],
        document_type: str
    ) -> str:
        """
        Generate document from template
        
        Args:
            template: Document template
            context: Context variables
            document_type: Type of document
            
        Returns:
            Generated document
        """
        # Convert context to string representation
        context_str = json.dumps(context, indent=2)
        
        # Create prompt for document generation
        messages = [
            {"role": "system", "content": f"You are a legal assistant that generates {document_type} documents based on templates and context information. Follow the template structure exactly, filling in the appropriate information from the context."},
            {"role": "user", "content": f"Please generate a {document_type} document based on this template and context information.\n\nTemplate:\n{template}\n\nContext:\n{context_str}"}
        ]
        
        # Generate document
        response = await self.chat_completion(messages=messages)
        
        return response["content"]
    
    async def answer_question_with_context(
        self,
        question: str,
        context: List[str],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Answer question with document context
        
        Args:
            question: User question
            context: List of document excerpts for context
            chat_history: Previous chat messages (optional)
            
        Returns:
            Answer to question
        """
        # Combine context
        combined_context = "\n\n---\n\n".join(context)
        
        # Create system prompt
        system_prompt = "You are a legal assistant that answers questions based on the provided document context. If the answer is not in the context, say that you don't know. Always cite the specific parts of the context that support your answer."
        
        # Create messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history[-5:])  # Add last 5 messages
        
        # Add context and question
        messages.append({"role": "user", "content": f"Context:\n{combined_context}\n\nQuestion: {question}"})
        
        # Generate answer
        response = await self.chat_completion(messages=messages)
        
        return response["content"]
    
    async def fill_pdf_form(self, form_fields: List[Dict[str, str]], document_context: str) -> Dict[str, str]:
        """
        Fill PDF form fields based on document context
        
        Args:
            form_fields: List of form fields
            document_context: Document context
            
        Returns:
            Dictionary with field values
        """
        # Format form fields
        fields_str = "\n".join([f"- {field['name']}: {field.get('description', '')}" for field in form_fields])
        
        # Create prompt for form filling
        messages = [
            {"role": "system", "content": "You are a legal assistant that fills out form fields based on document context. Extract the appropriate information from the context to fill each field. If the information is not available, leave the field blank."},
            {"role": "user", "content": f"Please fill out the following form fields based on this document context. Return your response as a JSON object with field names as keys and field values as values.\n\nForm Fields:\n{fields_str}\n\nDocument Context:\n{document_context}"}
        ]
        
        # Generate form field values
        response = await self.chat_completion(messages=messages)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            content = response["content"]
            
            # Find JSON block
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                field_values = json.loads(json_str)
            else:
                # Fallback if JSON not properly formatted
                field_values = {"error": "Could not parse JSON response", "raw_response": content}
            
            return field_values
        
        except Exception as e:
            logger.error(f"Error parsing form filling response: {str(e)}")
            return {"error": str(e), "raw_response": response["content"]}
