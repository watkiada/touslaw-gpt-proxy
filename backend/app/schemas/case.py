"""
Pydantic schemas for case management
"""
from typing import Optional, List
from pydantic import BaseModel


class CaseBase(BaseModel):
    """Base case schema with common attributes"""
    name: str
    description: Optional[str] = None
    status: str = "active"  # 'active', 'archived', 'closed'
    office_id: int


class CaseCreate(CaseBase):
    """Case creation schema"""
    pass


class CaseUpdate(CaseBase):
    """Case update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    office_id: Optional[int] = None


class CaseInDBBase(CaseBase):
    """Base schema for cases in DB"""
    id: int
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True


class Case(CaseInDBBase):
    """Case schema for API responses"""
    pass
