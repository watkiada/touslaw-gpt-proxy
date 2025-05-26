"""
Pinecone service for vector database operations
"""
from typing import List, Dict, Tuple, Optional
import pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class PineconeService:
    """Service for Pinecone vector database operations"""
    
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None, index_name: Optional[str] = None):
        """
        Initialize Pinecone service
        
        Args:
            api_key: Pinecone API key (optional, defaults to settings)
            environment: Pinecone environment (optional, defaults to settings)
            index_name: Pinecone index name (optional, defaults to settings)
        """
        self.api_key = api_key or settings.PINECONE_API_KEY
        self.environment = environment or settings.PINECONE_ENVIRONMENT
        self.index_name = index_name or settings.PINECONE_INDEX_NAME
        self.dimension = settings.CHUNK_SIZE
        
        # Initialize Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
    async def initialize_index(self):
        """
        Create index if it doesn't exist
        
        Raises:
            Exception: If index creation fails
        """
        try:
            # Check if index exists
            if self.index_name not in pinecone.list_indexes():
                # Create index
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
        except Exception as e:
            raise Exception(f"Error initializing Pinecone index: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def upsert_vectors(self, 
                            vectors: List[Tuple[str, List[float], Dict]], 
                            namespace: Optional[str] = None):
        """
        Insert or update vectors in the index
        
        Args:
            vectors: List of tuples (id, vector, metadata)
            namespace: Optional namespace
            
        Raises:
            Exception: If upsert fails
        """
        try:
            # Get index
            index = pinecone.Index(self.index_name)
            
            # Format vectors for upsert
            formatted_vectors = [
                (id, vector, metadata) for id, vector, metadata in vectors
            ]
            
            # Upsert vectors
            index.upsert(
                vectors=formatted_vectors,
                namespace=namespace
            )
        except Exception as e:
            raise Exception(f"Error upserting vectors: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def query_vectors(self, 
                           query_vector: List[float], 
                           top_k: int = 5,
                           namespace: Optional[str] = None,
                           filter: Optional[Dict] = None) -> List[Dict]:
        """
        Query for similar vectors
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            namespace: Optional namespace
            filter: Optional metadata filter
            
        Returns:
            List of query results
            
        Raises:
            Exception: If query fails
        """
        try:
            # Get index
            index = pinecone.Index(self.index_name)
            
            # Query index
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True
            )
            
            return results.matches
        except Exception as e:
            raise Exception(f"Error querying vectors: {str(e)}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def delete_vectors(self, 
                            ids: List[str], 
                            namespace: Optional[str] = None):
        """
        Delete vectors by ID
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
            
        Raises:
            Exception: If deletion fails
        """
        try:
            # Get index
            index = pinecone.Index(self.index_name)
            
            # Delete vectors
            index.delete(
                ids=ids,
                namespace=namespace
            )
        except Exception as e:
            raise Exception(f"Error deleting vectors: {str(e)}")
