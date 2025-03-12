"""
Authentication models.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from app.api.models.user import UserResponse

class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str
    user_id: str

class TokenPayload(BaseModel):
    """Token payload model."""
    sub: Optional[str] = None
    exp: Optional[int] = None

class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class SignupRequest(BaseModel):
    """Signup request model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)

class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator("new_password")
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        # Check for at least one digit
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        
        return v

class TokenVerifyRequest(BaseModel):
    """Token verification request model."""
    token: str

class LoginResponse(BaseModel):
    """Login response model."""
    token: Token
    user: UserResponse