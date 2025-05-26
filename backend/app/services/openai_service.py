"""
OpenAI service for AI integrations
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class OpenAIService:
    """Service for OpenAI API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI service
        
        Args:
            api_key: OpenAI API key (optional, defaults to settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = settings.DEFAULT_AI_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            texts: List of text chunks
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def chat_completion(self, 
                             messages: List[Dict[str, str]], 
                             model: Optional[str] = None,
                             temperature: Optional[float] = None) -> str:
        """
        Generate chat completion response
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Optional model override
            temperature: Optional temperature override
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature or 0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating chat completion: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def extract_data(self, text: str, schema: Dict) -> Dict:
        """
        Extract structured data from text based on schema
        
        Args:
            text: Text to extract data from
            schema: JSON schema for extraction
            
        Returns:
            Extracted data as dictionary
            
        Raises:
            Exception: If API call fails
        """
        try:
            prompt = f"""
            Extract the following information from the text according to this schema:
            {schema}
            
            Text:
            {text}
            
            Return only a valid JSON object matching the schema.
            """
            
            response = await self.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1  # Lower temperature for more deterministic extraction
            )
            
            # Parse JSON response
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from text response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        return {}
                else:
                    return {}
        except Exception as e:
            raise Exception(f"Error extracting data: {str(e)}")
