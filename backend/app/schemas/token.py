"""
Pydantic schemas for token authentication
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """Token schema for authentication response"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema for JWT decoding"""
    sub: Optional[int] = None
