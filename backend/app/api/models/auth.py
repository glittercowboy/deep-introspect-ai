"""
Authentication API models.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    user_id: str


class TokenPayload(BaseModel):
    """Token payload model."""
    sub: str
    exp: int


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Password reset confirmation request model."""
    token: str
    password: str


class RegistrationRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    password: str
    name: Optional[str] = None


class RegistrationResponse(BaseModel):
    """Registration response model."""
    user_id: str
    email: EmailStr
    message: str = "Registration successful"
