"""
PDF form handling service for filling out PDF forms with AI assistance
"""
import os
import uuid
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import Document, Case, Folder, DocumentChunk
from app.schemas.document import PDFFormField, PDFForm, PDFFormFillRequest


class PDFFormService:
    """Service for handling PDF form operations"""
    
    def __init__(self, db: Session, openai_service=None, pinecone_service=None):
        """
        Initialize PDF form service
        
        Args:
            db: Database session
            openai_service: OpenAI service for AI assistance
            pinecone_service: Pinecone service for document retrieval
        """
        self.db = db
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
    
    async def extract_form_fields(self, document_id: int) -> PDFForm:
        """
        Extract form fields from a PDF document
        
        Args:
            document_id: Document ID
            
        Returns:
            PDFForm object with extracted fields
            
        Raises:
            ValueError: If document is not found or not a PDF
        """
        # Get document from database
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        if not document.mime_type.lower().endswith('pdf'):
            raise ValueError(f"Document with ID {document_id} is not a PDF")
        
        # Open PDF and extract form fields
        pdf_path = document.file_path
        fields = []
        
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                widgets = page.widgets()
                for widget in widgets:
                    field = PDFFormField(
                        name=widget.field_name,
                        type=self._map_field_type(widget.field_type),
                        value=widget.field_value,
                        options=widget.choice_values if hasattr(widget, 'choice_values') else None,
                        required=False,  # PDF doesn't store this info, default to False
                        page=page_num,
                        rect=[widget.rect.x0, widget.rect.y0, widget.rect.x1, widget.rect.y1]
                    )
                    fields.append(field)
            doc.close()
        except Exception as e:
            raise ValueError(f"Error extracting form fields: {str(e)}")
        
        return PDFForm(document_id=document_id, fields=fields)
    
    async def fill_form(self, request: PDFFormFillRequest) -> Document:
        """
        Fill a PDF form with provided values
        
        Args:
            request: Form fill request with field values
            
        Returns:
            Document object for the filled PDF
            
        Raises:
            ValueError: If document is not found or not a PDF
        """
        # Get document from database
        document = self.db.query(Document).filter(Document.id == request.document_id).first()
        if not document:
            raise ValueError(f"Document with ID {request.document_id} not found")
        
        if not document.mime_type.lower().endswith('pdf'):
            raise ValueError(f"Document with ID {request.document_id} is not a PDF")
        
        # Create output filename if not provided
        output_filename = request.output_filename
        if not output_filename:
            base_name = os.path.splitext(document.original_filename)[0]
            output_filename = f"{base_name}_filled.pdf"
        
        # Create output path
        office_path = os.path.join(settings.STORAGE_PATH, "offices", str(document.office_id))
        
        if request.case_id:
            case = self.db.query(Case).filter(Case.id == request.case_id).first()
            if not case:
                raise ValueError(f"Case with ID {request.case_id} not found")
            case_path = os.path.join(office_path, "cases", str(case.id), "documents")
            os.makedirs(case_path, exist_ok=True)
            output_path = os.path.join(case_path, output_filename)
        elif request.folder_id:
            folder = self.db.query(Folder).filter(Folder.id == request.folder_id).first()
            if not folder:
                raise ValueError(f"Folder with ID {request.folder_id} not found")
            folder_path = os.path.join(office_path, "folders", str(folder.id))
            os.makedirs(folder_path, exist_ok=True)
            output_path = os.path.join(folder_path, output_filename)
        else:
            # Default to same location as original
            output_dir = os.path.dirname(document.file_path)
            output_path = os.path.join(output_dir, output_filename)
        
        # Fill the form
        try:
            doc = fitz.open(document.file_path)
            for page in doc:
                for field_name, field_value in request.field_values.items():
                    field = page.get_field(field_name)
                    if field:
                        field.field_value = field_value
                        page.update_field(field)
            
            # Save filled form
            doc.save(output_path)
            doc.close()
        except Exception as e:
            raise ValueError(f"Error filling form: {str(e)}")
        
        # Create new document record
        new_doc = Document(
            filename=str(uuid.uuid4()),
            original_filename=output_filename,
            file_path=output_path,
            file_size=os.path.getsize(output_path),
            mime_type="application/pdf",
            folder_id=request.folder_id,
            case_id=request.case_id,
            office_id=document.office_id,
            is_ocr_processed=False,
            is_indexed=False,
            created_by_id=document.created_by_id
        )
        
        self.db.add(new_doc)
        self.db.commit()
        self.db.refresh(new_doc)
        
        return new_doc
    
    async def suggest_form_values(self, document_id: int, case_id: Optional[int] = None) -> Dict[str, str]:
        """
        Suggest values for form fields based on case documents
        
        Args:
            document_id: Document ID of the form
            case_id: Optional case ID to limit document search
            
        Returns:
            Dictionary of field names to suggested values
            
        Raises:
            ValueError: If document is not found or not a PDF
        """
        if not self.openai_service or not self.pinecone_service:
            raise ValueError("AI services not initialized")
        
        # Extract form fields
        form = await self.extract_form_fields(document_id)
        
        # Get document from database
        document = self.db.query(Document).filter(Document.id == document_id).first()
        
        # Get relevant document chunks
        query = "Information for filling out legal forms"
        filter_params = {"office_id": document.office_id}
        
        if case_id:
            filter_params["case_id"] = case_id
        
        # Get embedding for query
        query_embedding = await self.openai_service.generate_embeddings([query])
        
        # Search for relevant chunks
        results = await self.pinecone_service.query_vectors(
            query_vector=query_embedding[0],
            top_k=10,
            filter=filter_params
        )
        
        # Get chunk content
        chunk_ids = [result["id"] for result in results]
        chunks = self.db.query(DocumentChunk).filter(DocumentChunk.embedding_id.in_(chunk_ids)).all()
        
        # Build context from chunks
        context = "\n\n".join([chunk.content for chunk in chunks])
        
        # Build field descriptions
        field_descriptions = []
        for field in form.fields:
            field_type = field.type
            options = ""
            if field.options:
                options = f" Options: {', '.join(field.options)}"
            field_descriptions.append(f"Field name: {field.name}, Type: {field_type}{options}")
        
        field_text = "\n".join(field_descriptions)
        
        # Build prompt for OpenAI
        prompt = f"""
        You are an AI assistant helping to fill out a PDF form based on information from legal documents.
        
        Form fields:
        {field_text}
        
        Relevant document content:
        {context}
        
        Based on the document content, suggest appropriate values for each form field.
        Return your response as a JSON object with field names as keys and suggested values as values.
        If you cannot determine a value for a field, use null.
        """
        
        # Get suggestions from OpenAI
        response = await self.openai_service.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for filling out legal forms."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse response as JSON
        import json
        try:
            suggestions = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from text response
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                try:
                    suggestions = json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    suggestions = {}
            else:
                suggestions = {}
        
        return suggestions
    
    def _map_field_type(self, field_type: int) -> str:
        """
        Map PyMuPDF field type to schema field type
        
        Args:
            field_type: PyMuPDF field type
            
        Returns:
            Schema field type
        """
        # PyMuPDF field types
        # 1: text, 2: checkbox, 3: radio, 4: listbox, 5: combobox, 6: signature
        type_map = {
            1: "text",
            2: "checkbox",
            3: "radio",
            4: "select",
            5: "select",
            6: "signature"
        }
        return type_map.get(field_type, "text")
