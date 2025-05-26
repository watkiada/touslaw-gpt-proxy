"""
Pydantic schemas for folder management
"""
from typing import Optional, List
from pydantic import BaseModel


class FolderBase(BaseModel):
    """Base folder schema with common attributes"""
    name: str
    parent_id: Optional[int] = None
    case_id: Optional[int] = None
    office_id: int


class FolderCreate(FolderBase):
    """Folder creation schema"""
    pass


class FolderUpdate(FolderBase):
    """Folder update schema"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    case_id: Optional[int] = None
    office_id: Optional[int] = None


class FolderInDBBase(FolderBase):
    """Base schema for folders in DB"""
    id: int
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True


class Folder(FolderInDBBase):
    """Folder schema for API responses"""
    pass


class FolderTree(Folder):
    """Folder schema with children for tree view"""
    children: List['FolderTree'] = []
