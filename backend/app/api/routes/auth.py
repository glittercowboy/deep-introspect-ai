"""
Authentication API routes.
"""
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.api.models.base import (
    UserCreate,
    User,
    TokenResponse,
    ResponseBase,
)
from app.db.supabase import supabase_client
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import AuthenticationError, ValidationError

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    """
    # Check if the user already exists
    existing_user = await supabase_client.get_user_by_email(user_data.email)
    if existing_user:
        raise ValidationError("User with this email already exists")
    
    # Create a new user with hashed password
    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])
    user_dict["id"] = supabase_client.generate_uuid()
    user_dict["created_at"] = datetime.now().isoformat()
    user_dict["metadata"] = {}
    
    # Store user in database
    new_user = await supabase_client.create_user(user_dict)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return User(**new_user)

@router.post("/login", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Login to get an access token.
    """
    # Get user from database
    user = await supabase_client.get_user_by_email(form_data.username)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    # Verify password
    if not verify_password(form_data.password, user["password"]):
        raise AuthenticationError("Incorrect email or password")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user["id"],
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Refresh access token.
    """
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=current_user.id,
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout", response_model=ResponseBase)
async def logout(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Logout the current user.
    
    Note: JWT tokens cannot be invalidated, so this is primarily
    for client-side cleanup. The client should discard the token.
    """
    return ResponseBase(message="Successfully logged out")

@router.post("/password-reset-request")
async def request_password_reset(email: EmailStr):
    """
    Request a password reset.
    """
    # Check if user exists
    user = await supabase_client.get_user_by_email(email)
    if not user:
        # Return success anyway to prevent email enumeration
        return ResponseBase(message="If the email exists, a password reset link has been sent")
    
    # In a real implementation, we would send an email with a reset link
    # For now, we'll just return a success message
    
    return ResponseBase(message="If the email exists, a password reset link has been sent")

@router.post("/password-reset")
async def reset_password(token: str, new_password: str):
    """
    Reset password using a reset token.
    """
    # In a real implementation, we would validate the token
    # and update the user's password
    
    # For now, we'll just return a success message
    return ResponseBase(message="Password has been reset successfully")

@router.get("/me", response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get the current authenticated user.
    """
    return current_user