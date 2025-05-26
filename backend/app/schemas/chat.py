"""
Pydantic schemas for AI chat functionality
"""
from typing import Optional, List
from pydantic import BaseModel


class ChatSessionBase(BaseModel):
    """Base chat session schema with common attributes"""
    title: Optional[str] = None
    case_id: Optional[int] = None
    office_id: int
    ai_model_id: int


class ChatSessionCreate(ChatSessionBase):
    """Chat session creation schema"""
    document_ids: Optional[List[int]] = None


class ChatSessionUpdate(ChatSessionBase):
    """Chat session update schema"""
    title: Optional[str] = None
    case_id: Optional[int] = None
    office_id: Optional[int] = None
    ai_model_id: Optional[int] = None


class ChatSessionInDBBase(ChatSessionBase):
    """Base schema for chat sessions in DB"""
    id: int
    user_id: int

    class Config:
        orm_mode = True


class ChatSession(ChatSessionInDBBase):
    """Chat session schema for API responses"""
    pass


class ChatMessageBase(BaseModel):
    """Base chat message schema with common attributes"""
    role: str  # 'user', 'assistant', 'system'
    content: str


class ChatMessageCreate(ChatMessageBase):
    """Chat message creation schema"""
    chat_session_id: int


class ChatMessageInDBBase(ChatMessageBase):
    """Base schema for chat messages in DB"""
    id: int
    chat_session_id: int

    class Config:
        orm_mode = True


class ChatMessage(ChatMessageInDBBase):
    """Chat message schema for API responses"""
    pass


class ChatCompletionRequest(BaseModel):
    """Chat completion request schema"""
    chat_session_id: int
    message: str
    document_ids: Optional[List[int]] = None
    form_fill_request: Optional[bool] = False
    form_document_id: Optional[int] = None


class ChatCompletionResponse(BaseModel):
    """Chat completion response schema"""
    message: ChatMessage
    suggested_form_values: Optional[dict] = None
