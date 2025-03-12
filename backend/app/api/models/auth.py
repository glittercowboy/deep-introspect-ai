"""
API models for authentication.
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCredentials(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User's email")
    password: str = Field(..., description="User's password", min_length=8)


class SignUpRequest(UserCredentials):
    """Schema for user registration."""
    name: str = Field(..., description="User's full name")


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User's email")
    name: str = Field(..., description="User's full name")
    created_at: str = Field(..., description="Account creation timestamp")


class AuthResponse(BaseModel):
    """Schema for authentication response."""
    user: UserResponse = Field(..., description="User data")
    token: TokenResponse = Field(..., description="Authentication token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User's email")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password", min_length=8)
