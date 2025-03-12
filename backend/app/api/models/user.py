"""
User API models.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str


class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """User response model."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


class UserPreferences(BaseModel):
    """User preferences model."""
    theme: Optional[str] = "dark"
    default_model: Optional[str] = "anthropic"
    notification_enabled: Optional[bool] = True
    insights_enabled: Optional[bool] = True


class UserProfileResponse(UserResponse):
    """User profile response model with additional user data."""
    preferences: Optional[UserPreferences] = None
    conversation_count: Optional[int] = 0
    insight_count: Optional[int] = 0
    last_activity: Optional[datetime] = None
