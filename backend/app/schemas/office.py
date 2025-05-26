"""
Pydantic schemas for office management
"""
from typing import Optional, List
from pydantic import BaseModel


class OfficeBase(BaseModel):
    """Base office schema with common attributes"""
    name: str
    description: Optional[str] = None


class OfficeCreate(OfficeBase):
    """Office creation schema"""
    pass


class OfficeUpdate(OfficeBase):
    """Office update schema"""
    name: Optional[str] = None


class OfficeInDBBase(OfficeBase):
    """Base schema for offices in DB"""
    id: int
    created_by_id: Optional[int] = None

    class Config:
        orm_mode = True


class Office(OfficeInDBBase):
    """Office schema for API responses"""
    pass


class OfficeUserBase(BaseModel):
    """Base office user relationship schema"""
    role: str = "member"


class OfficeUserCreate(OfficeUserBase):
    """Office user relationship creation schema"""
    user_id: int
    office_id: int


class OfficeUserUpdate(OfficeUserBase):
    """Office user relationship update schema"""
    role: Optional[str] = None


class OfficeUserInDBBase(OfficeUserBase):
    """Base schema for office user relationships in DB"""
    office_id: int
    user_id: int

    class Config:
        orm_mode = True


class OfficeUser(OfficeUserInDBBase):
    """Office user relationship schema for API responses"""
    pass
