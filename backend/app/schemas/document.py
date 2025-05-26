"""
Pydantic schemas for document management
"""
from typing import Optional, List
from pydantic import BaseModel


class DocumentBase(BaseModel):
    """Base document schema with common attributes"""
    original_filename: str
    folder_id: Optional[int] = None
    case_id: Optional[int] = None
    office_id: int


class DocumentCreate(DocumentBase):
    """Document creation schema"""
    file_path: str
    file_size: int
    mime_type: str


class DocumentUpdate(DocumentBase):
    """Document update schema"""
    original_filename: Optional[str] = None
    folder_id: Optional[int] = None
    case_id: Optional[int] = None
    office_id: Optional[int] = None
    is_ocr_processed: Optional[bool] = None
    is_indexed: Optional[bool] = None


class DocumentInDBBase(DocumentBase):
    """Base schema for documents in DB"""
    id: int
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    is_ocr_processed: bool
    is_indexed: bool
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True


class Document(DocumentInDBBase):
    """Document schema for API responses"""
    pass


class DocumentMetadataBase(BaseModel):
    """Base document metadata schema"""
    key: str
    value: Optional[str] = None


class DocumentMetadataCreate(DocumentMetadataBase):
    """Document metadata creation schema"""
    document_id: int


class DocumentMetadataUpdate(DocumentMetadataBase):
    """Document metadata update schema"""
    key: Optional[str] = None
    value: Optional[str] = None


class DocumentMetadataInDBBase(DocumentMetadataBase):
    """Base schema for document metadata in DB"""
    id: int
    document_id: int

    class Config:
        orm_mode = True


class DocumentMetadata(DocumentMetadataInDBBase):
    """Document metadata schema for API responses"""
    pass


class DocumentWithMetadata(Document):
    """Document schema with metadata for API responses"""
    metadata: List[DocumentMetadata] = []


class PDFFormField(BaseModel):
    """PDF form field schema"""
    name: str
    type: str  # 'text', 'checkbox', 'radio', 'select'
    value: Optional[str] = None
    options: Optional[List[str]] = None  # For select/radio fields
    required: bool = False
    page: int = 0
    rect: Optional[List[float]] = None  # [x1, y1, x2, y2]


class PDFForm(BaseModel):
    """PDF form schema"""
    document_id: int
    fields: List[PDFFormField] = []


class PDFFormFillRequest(BaseModel):
    """PDF form fill request schema"""
    document_id: int
    field_values: dict  # Field name to value mapping
    output_filename: Optional[str] = None
    case_id: Optional[int] = None
    folder_id: Optional[int] = None


class PDFFormFillResponse(BaseModel):
    """PDF form fill response schema"""
    filled_document_id: int
    success: bool
    message: str
