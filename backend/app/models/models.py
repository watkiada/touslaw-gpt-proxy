"""
Database models for the application
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


# Association table for chat sessions and documents
ChatSessionDocument = Table(
    "chat_session_document",
    Base.metadata,
    Column("chat_session_id", Integer, ForeignKey("chat_session.id"), primary_key=True),
    Column("document_id", Integer, ForeignKey("document.id"), primary_key=True)
)


class User(Base):
    """User model"""
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    offices = relationship("OfficeUser", back_populates="user")
    documents = relationship("Document", back_populates="created_by")
    chat_sessions = relationship("ChatSession", back_populates="user")


class OfficeUser(Base):
    """Office-User relationship model"""
    __tablename__ = "office_user"
    
    office_id = Column(Integer, ForeignKey("office.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    role = Column(String(50), default="member")  # 'admin' or 'member'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    office = relationship("Office", back_populates="users")
    user = relationship("User", back_populates="offices")


class Office(Base):
    """Office model"""
    __tablename__ = "office"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("OfficeUser", back_populates="office")
    cases = relationship("Case", back_populates="office")
    documents = relationship("Document", back_populates="office")
    folders = relationship("Folder", back_populates="office")
    chat_sessions = relationship("ChatSession", back_populates="office")
    created_by = relationship("User")


class Case(Base):
    """Case model"""
    __tablename__ = "case"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="active")  # 'active', 'archived', 'closed'
    office_id = Column(Integer, ForeignKey("office.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    office = relationship("Office", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    folders = relationship("Folder", back_populates="case")
    chat_sessions = relationship("ChatSession", back_populates="case")
    created_by = relationship("User")


class Folder(Base):
    """Folder model"""
    __tablename__ = "folder"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("folder.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("case.id"), nullable=True)
    office_id = Column(Integer, ForeignKey("office.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("Folder", remote_side=[id], backref="children")
    case = relationship("Case", back_populates="folders")
    office = relationship("Office", back_populates="folders")
    documents = relationship("Document", back_populates="folder")
    created_by = relationship("User")


class Document(Base):
    """Document model"""
    __tablename__ = "document"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)  # System filename (UUID)
    original_filename = Column(String(255), nullable=False)  # Original filename
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(255), nullable=False)
    folder_id = Column(Integer, ForeignKey("folder.id"), nullable=True)
    case_id = Column(Integer, ForeignKey("case.id"), nullable=True)
    office_id = Column(Integer, ForeignKey("office.id"), nullable=False)
    is_ocr_processed = Column(Boolean, default=False)
    is_indexed = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    folder = relationship("Folder", back_populates="documents")
    case = relationship("Case", back_populates="documents")
    office = relationship("Office", back_populates="documents")
    created_by = relationship("User", back_populates="documents")
    metadata = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", secondary=ChatSessionDocument, back_populates="documents")


class DocumentMetadata(Base):
    """Document metadata model"""
    __tablename__ = "document_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    
    # Relationships
    document = relationship("Document", back_populates="metadata")


class DocumentChunk(Base):
    """Document chunk model for vector search"""
    __tablename__ = "document_chunk"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=False, unique=True)  # ID in vector database
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class AIModel(Base):
    """AI model configuration"""
    __tablename__ = "ai_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)  # 'openai', 'anthropic', etc.
    model_id = Column(String(255), nullable=False)  # 'gpt-4', 'claude-3-opus', etc.
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="ai_model")


class ChatSession(Base):
    """Chat session model"""
    __tablename__ = "chat_session"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("case.id"), nullable=True)
    office_id = Column(Integer, ForeignKey("office.id"), nullable=False)
    ai_model_id = Column(Integer, ForeignKey("ai_model.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    case = relationship("Case", back_populates="chat_sessions")
    office = relationship("Office", back_populates="chat_sessions")
    ai_model = relationship("AIModel", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")
    documents = relationship("Document", secondary=ChatSessionDocument, back_populates="chat_sessions")


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_message"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_session.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
