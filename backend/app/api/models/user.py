"""
User models.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

class UserPreferences(BaseModel):
    """User preferences model."""
    default_llm: Optional[str] = "anthropic"
    theme: Optional[str] = "dark"
    email_notifications: Optional[bool] = True
    reminder_frequency: Optional[str] = "daily"
    reflection_questions: Optional[List[str]] = None

class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class User(UserBase):
    """User model."""
    id: str
    created_at: datetime
    preferences: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic config."""
        orm_mode = True

class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    avatar_url: Optional[str] = None
    
    class Config:
        """Pydantic config."""
        orm_mode = True