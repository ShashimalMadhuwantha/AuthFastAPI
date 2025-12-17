from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
