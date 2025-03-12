"""
Authentication API routes.
"""
import logging
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.config import settings
from app.db.supabase import supabase_client
from app.core.security import create_access_token, verify_password, get_password_hash
from app.api.models.auth import (
    Token, 
    LoginRequest, 
    RefreshTokenRequest, 
    PasswordResetRequest,
    PasswordResetConfirmRequest, 
    RegistrationRequest,
    RegistrationResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Login with email and password.
    
    Args:
        form_data: OAuth2 form data with username (email) and password
        
    Returns:
        Token object with access token
    """
    # Get user from database
    user = await supabase_client.get_user_by_email(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user["id"]), expires_delta=access_token_expires
    )
    
    # Create refresh token (optional)
    refresh_token = create_access_token(
        subject=str(user["id"]),
        expires_delta=timedelta(days=30),
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=access_token_expires.total_seconds(),
        refresh_token=refresh_token,
        user_id=user["id"]
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_data: RefreshTokenRequest) -> Any:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token data
        
    Returns:
        New token object with access token
    """
    try:
        from jose import jwt
        
        # Decode refresh token
        payload = jwt.decode(
            refresh_data.refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await supabase_client.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user["id"]), expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token = create_access_token(
            subject=str(user["id"]),
            expires_delta=timedelta(days=30),
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=access_token_expires.total_seconds(),
            refresh_token=refresh_token,
            user_id=user["id"]
        )
        
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=RegistrationResponse)
async def register(registration: RegistrationRequest) -> Any:
    """
    Register a new user.
    
    Args:
        registration: Registration data with email and password
        
    Returns:
        Registration response with user ID
    """
    # Check if email already exists
    existing_user = await supabase_client.get_user_by_email(registration.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user in database
    user_data = {
        "email": registration.email,
        "password_hash": get_password_hash(registration.password),
        "name": registration.name,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    user = await supabase_client.create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )
    
    return RegistrationResponse(
        user_id=user["id"],
        email=user["email"],
        message="Registration successful",
    )


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(reset_request: PasswordResetRequest) -> Any:
    """
    Request a password reset.
    
    Args:
        reset_request: Password reset request with email
        
    Returns:
        Success message
    """
    # Check if email exists
    user = await supabase_client.get_user_by_email(reset_request.email)
    if not user:
        # Don't reveal that the email doesn't exist
        return {"message": "If the email exists, a password reset link will be sent"}
    
    # Generate reset token
    reset_token = create_access_token(
        subject=str(user["id"]),
        expires_delta=timedelta(hours=24),
    )
    
    # Store token in database or send via email
    # In a real implementation, you would send an email with a reset link
    # For this example, we'll just return the token
    
    return {"message": "If the email exists, a password reset link will be sent"}


@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(reset_confirm: PasswordResetConfirmRequest) -> Any:
    """
    Confirm password reset with token and new password.
    
    Args:
        reset_confirm: Password reset confirmation with token and new password
        
    Returns:
        Success message
    """
    try:
        from jose import jwt
        
        # Decode reset token
        payload = jwt.decode(
            reset_confirm.token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )
        
        # Get user from database
        user = await supabase_client.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )
        
        # Update password
        user_data = {
            "password_hash": get_password_hash(reset_confirm.password),
            "updated_at": datetime.now().isoformat(),
        }
        
        updated_user = await supabase_client.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password",
            )
        
        return {"message": "Password reset successful"}
        
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token",
        )
