"""
Document processing service for handling document operations
"""
import os
import uuid
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Document, DocumentChunk, DocumentMetadata
from app.services.ocr_service import OCRService
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService


class DocumentProcessor:
    """Service for document processing operations"""
    
    def __init__(
        self,
        db: Session,
        openai_service: OpenAIService,
        pinecone_service: PineconeService,
        ocr_service: OCRService,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize document processor
        
        Args:
            db: Database session
            openai_service: OpenAI service for embeddings
            pinecone_service: Pinecone service for vector storage
            ocr_service: OCR service for text extraction
            chunk_size: Size of document chunks (optional, defaults to settings)
            chunk_overlap: Overlap between chunks (optional, defaults to settings)
        """
        self.db = db
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
        self.ocr_service = ocr_service
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    async def process_document(self, document_id: int) -> None:
        """
        Process a document for AI interaction
        
        Args:
            document_id: Document ID
            
        Raises:
            ValueError: If document is not found
        """
        # Get document from database
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Extract text based on document type
        text = await self._extract_text(document)
        
        # Split text into chunks
        chunks = await self.chunk_text(text)
        
        # Generate embeddings
        embeddings = await self.openai_service.generate_embeddings(chunks)
        
        # Store chunks and embeddings
        await self._store_chunks(document, chunks, embeddings)
        
        # Extract metadata
        metadata = await self.extract_metadata(document, text)
        
        # Store metadata
        await self._store_metadata(document, metadata)
        
        # Update document status
        document.is_indexed = True
        self.db.commit()
    
    async def _extract_text(self, document: Document) -> str:
        """
        Extract text from document
        
        Args:
            document: Document object
            
        Returns:
            Extracted text
            
        Raises:
            ValueError: If text extraction fails
        """
        mime_type = document.mime_type.lower()
        file_path = document.file_path
        
        try:
            if mime_type == 'application/pdf':
                # Check if PDF is scanned
                is_scanned = await self.ocr_service.is_scanned_pdf(file_path)
                
                if is_scanned:
                    # Process with OCR
                    pages = await self.ocr_service.process_pdf(file_path)
                    text = '\n\n'.join(pages)
                    
                    # Update OCR status
                    document.is_ocr_processed = True
                    self.db.commit()
                else:
                    # Extract text with pdftotext
                    import subprocess
                    result = subprocess.run(
                        ["pdftotext", file_path, "-"],
                        capture_output=True,
                        text=True
                    )
                    text = result.stdout
            elif mime_type.startswith('image/'):
                # Process with OCR
                text = await self.ocr_service.process_image(file_path)
                
                # Update OCR status
                document.is_ocr_processed = True
                self.db.commit()
            elif mime_type in ['text/plain', 'text/markdown', 'text/csv']:
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                              'application/msword']:
                # Extract text from Word document
                import docx
                doc = docx.Document(file_path)
                text = '\n\n'.join([para.text for para in doc.paragraphs])
            else:
                # Unsupported format
                text = f"Unsupported document format: {mime_type}"
            
            return text
        except Exception as e:
            raise ValueError(f"Error extracting text from document: {str(e)}")
    
    async def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Get chunk
            end = start + self.chunk_size
            if end > len(text):
                end = len(text)
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            if start >= len(text):
                break
        
        return chunks
    
    async def _store_chunks(self, document: Document, chunks: List[str], embeddings: List[List[float]]) -> None:
        """
        Store document chunks and embeddings
        
        Args:
            document: Document object
            chunks: List of text chunks
            embeddings: List of embedding vectors
            
        Raises:
            ValueError: If storage fails
        """
        try:
            # Delete existing chunks
            self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
            
            # Prepare vectors for Pinecone
            vectors = []
            chunk_records = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create embedding ID
                embedding_id = f"{document.id}_{i}"
                
                # Create chunk record
                chunk_record = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk,
                    embedding_id=embedding_id
                )
                chunk_records.append(chunk_record)
                
                # Create vector for Pinecone
                metadata = {
                    "document_id": document.id,
                    "chunk_index": i,
                    "office_id": document.office_id,
                    "case_id": document.case_id,
                    "mime_type": document.mime_type
                }
                vectors.append((embedding_id, embedding, metadata))
            
            # Store chunks in database
            self.db.add_all(chunk_records)
            self.db.commit()
            
            # Store vectors in Pinecone
            await self.pinecone_service.upsert_vectors(vectors)
        except Exception as e:
            raise ValueError(f"Error storing document chunks: {str(e)}")
    
    async def extract_metadata(self, document: Document, text: str = None) -> Dict:
        """
        Extract metadata from document using AI
        
        Args:
            document: Document object
            text: Optional document text (if already extracted)
            
        Returns:
            Dictionary of metadata
            
        Raises:
            ValueError: If extraction fails
        """
        try:
            # Get text if not provided
            if not text:
                text = await self._extract_text(document)
            
            # Truncate text if too long
            if len(text) > 10000:
                text = text[:10000] + "..."
            
            # Define extraction schema
            schema = {
                "title": "Document title",
                "author": "Document author or creator",
                "date": "Document creation or modification date",
                "summary": "Brief summary of document content",
                "document_type": "Type of document (e.g., contract, letter, report)",
                "keywords": "List of keywords or key phrases",
                "entities": "List of named entities (people, organizations, locations)"
            }
            
            # Extract metadata with OpenAI
            metadata = await self.openai_service.extract_data(text, schema)
            return metadata
        except Exception as e:
            # Return basic metadata on error
            return {
                "title": os.path.basename(document.original_filename),
                "error": str(e)
            }
    
    async def _store_metadata(self, document: Document, metadata: Dict) -> None:
        """
        Store document metadata
        
        Args:
            document: Document object
            metadata: Dictionary of metadata
            
        Raises:
            ValueError: If storage fails
        """
        try:
            # Delete existing metadata
            self.db.query(DocumentMetadata).filter(DocumentMetadata.document_id == document.id).delete()
            
            # Create metadata records
            metadata_records = []
            
            for key, value in metadata.items():
                if value:
                    # Convert lists to strings
                    if isinstance(value, list):
                        value = ", ".join(value)
                    
                    metadata_record = DocumentMetadata(
                        document_id=document.id,
                        key=key,
                        value=str(value)
                    )
                    metadata_records.append(metadata_record)
            
            # Store metadata in database
            self.db.add_all(metadata_records)
            self.db.commit()
        except Exception as e:
            raise ValueError(f"Error storing document metadata: {str(e)}")
