"""
Pinecone service for vector database integration
"""
import os
import logging
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import pinecone
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings
from app.services.ai.openai_service import OpenAIService

logger = logging.getLogger(__name__)

class PineconeService:
    """
    Service for Pinecone vector database integration
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        environment: Optional[str] = None,
        index_name: Optional[str] = None
    ):
        """
        Initialize Pinecone service
        
        Args:
            api_key: Pinecone API key (optional, defaults to settings)
            environment: Pinecone environment (optional, defaults to settings)
            index_name: Pinecone index name (optional, defaults to settings)
        """
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.environment = environment or settings.PINECONE_ENVIRONMENT
        self.index_name = index_name or settings.PINECONE_INDEX_NAME or "watkibot-law-assistant"
        
        if not self.api_key or not self.environment:
            logger.warning("Pinecone API key or environment not provided")
            self.client = None
            self.index = None
        else:
            # Initialize Pinecone client
            try:
                self.client = pinecone.Pinecone(api_key=self.api_key, environment=self.environment)
                
                # Check if index exists, create if not
                existing_indexes = [index.name for index in self.client.list_indexes()]
                
                if self.index_name in existing_indexes:
                    self.index = self.client.Index(self.index_name)
                    logger.info(f"Connected to existing Pinecone index: {self.index_name}")
                else:
                    logger.warning(f"Pinecone index {self.index_name} does not exist")
                    self.index = None
            except Exception as e:
                logger.error(f"Error initializing Pinecone: {str(e)}")
                self.client = None
                self.index = None
        
        # Initialize OpenAI service for embeddings
        self.openai_service = OpenAIService()
    
    async def create_index_if_not_exists(self, dimension: int = 1536):
        """
        Create Pinecone index if it doesn't exist
        
        Args:
            dimension: Dimension of vectors (default: 1536 for OpenAI embeddings)
            
        Returns:
            True if index exists or was created, False otherwise
        """
        if not self.client:
            logger.error("Pinecone client not initialized")
            return False
        
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.client.list_indexes()]
            
            if self.index_name in existing_indexes:
                self.index = self.client.Index(self.index_name)
                logger.info(f"Connected to existing Pinecone index: {self.index_name}")
                return True
            
            # Create index
            self.client.create_index(
                name=self.index_name,
                dimension=dimension,
                metric="cosine"
            )
            
            logger.info(f"Created new Pinecone index: {self.index_name}")
            
            # Connect to new index
            self.index = self.client.Index(self.index_name)
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating Pinecone index: {str(e)}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def upsert_vectors(
        self,
        vectors: List[List[float]],
        ids: List[str],
        metadata: List[Dict[str, Any]]
    ) -> bool:
        """
        Upsert vectors to Pinecone index
        
        Args:
            vectors: List of vectors
            ids: List of vector IDs
            metadata: List of metadata dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        if len(vectors) != len(ids) or len(vectors) != len(metadata):
            logger.error("Vectors, IDs, and metadata must have the same length")
            return False
        
        try:
            # Prepare vectors for upsert
            items = []
            for i in range(len(vectors)):
                items.append({
                    "id": ids[i],
                    "values": vectors[i],
                    "metadata": metadata[i]
                })
            
            # Upsert vectors in batches of 100
            batch_size = 100
            for i in range(0, len(items), batch_size):
                batch = items[i:i+batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone index")
            return True
        
        except Exception as e:
            logger.error(f"Error upserting vectors to Pinecone: {str(e)}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def query_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone index
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filter: Filter for query
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of query results
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return []
        
        try:
            # Query vectors
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=include_metadata,
                filter=filter
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                result = {
                    "id": match.id,
                    "score": match.score
                }
                
                if include_metadata and hasattr(match, 'metadata'):
                    result["metadata"] = match.metadata
                
                formatted_results.append(result)
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error querying vectors from Pinecone: {str(e)}")
            return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def delete_vectors(self, ids: List[str]) -> bool:
        """
        Delete vectors from Pinecone index
        
        Args:
            ids: List of vector IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        try:
            # Delete vectors
            self.index.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} vectors from Pinecone index")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {str(e)}")
            return False
    
    async def index_document(
        self,
        document_id: str,
        document_text: str,
        metadata: Dict[str, Any],
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> bool:
        """
        Index document in Pinecone
        
        Args:
            document_id: Document ID
            document_text: Document text
            metadata: Document metadata
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        try:
            # Split document into chunks
            chunks = self._split_text(document_text, chunk_size, chunk_overlap)
            
            if not chunks:
                logger.warning(f"No chunks generated for document {document_id}")
                return False
            
            # Generate embeddings for chunks
            embeddings = await self.openai_service.generate_embeddings(chunks)
            
            if not embeddings or len(embeddings) != len(chunks):
                logger.error(f"Error generating embeddings for document {document_id}")
                return False
            
            # Prepare vector IDs and metadata
            ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
            
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                # Copy base metadata and add chunk-specific fields
                chunk_meta = metadata.copy()
                chunk_meta["document_id"] = document_id
                chunk_meta["chunk_index"] = i
                chunk_meta["chunk_text"] = chunk
                chunk_meta["total_chunks"] = len(chunks)
                
                chunk_metadata.append(chunk_meta)
            
            # Upsert vectors
            success = await self.upsert_vectors(
                vectors=embeddings,
                ids=ids,
                metadata=chunk_metadata
            )
            
            return success
        
        except Exception as e:
            logger.error(f"Error indexing document {document_id}: {str(e)}")
            return False
    
    async def search_documents(
        self,
        query: str,
        filter: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search documents in Pinecone
        
        Args:
            query: Search query
            filter: Filter for search
            top_k: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return []
        
        try:
            # Generate embedding for query
            embeddings = await self.openai_service.generate_embeddings([query])
            
            if not embeddings:
                logger.error("Error generating embedding for query")
                return []
            
            query_embedding = embeddings[0]
            
            # Query vectors
            results = await self.query_vectors(
                query_vector=query_embedding,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from Pinecone
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.index:
            logger.error("Pinecone index not initialized")
            return False
        
        try:
            # Delete vectors with filter
            self.index.delete(filter={"document_id": document_id})
            
            logger.info(f"Deleted document {document_id} from Pinecone index")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def _split_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks
        
        Args:
            text: Text to split
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Split text into paragraphs
        paragraphs = text.split("\n\n")
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk and start new one
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_start = max(0, len(words) - chunk_overlap)
                current_chunk = " ".join(words[overlap_start:]) + "\n\n" + paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk if not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
