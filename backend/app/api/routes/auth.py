"""
Authentication API routes.
"""
from typing import Dict, List, Optional, Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Body, Header
from fastapi.security import OAuth2PasswordRequestForm
from app.api.models.auth import (
    Token,
    TokenPayload,
    LoginRequest,
    SignupRequest,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest
)
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError, NotFoundError

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
async def signup(signup_data: SignupRequest):
    """
    Create a new user account.
    """
    # Check if email already exists
    try:
        # Use Supabase auth to create a new user
        auth_response = supabase_client.client.auth.sign_up({
            "email": signup_data.email,
            "password": signup_data.password
        })
        
        if auth_response.user:
            # Create user in users table
            user_data = {
                "id": auth_response.user.id,
                "email": signup_data.email,
                "name": signup_data.name,
                "created_at": auth_response.user.created_at,
                "preferences": {
                    "default_llm": "anthropic",
                    "theme": "dark"
                }
            }
            
            user = await supabase_client.create_user(user_data)
            return user
        else:
            raise HTTPException(status_code=400, detail="User creation failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Log in with email and password.
    """
    try:
        # Use Supabase auth to sign in
        auth_response = supabase_client.client.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })
        
        if auth_response.user:
            # Create access token with expiration
            access_token = create_access_token(
                subject=auth_response.user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": auth_response.user.id
            }
        else:
            raise AuthenticationError("Invalid credentials")
    except Exception as e:
        raise AuthenticationError(f"Login failed: {str(e)}")

@router.post("/token", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login for API access.
    """
    try:
        # Use Supabase auth to sign in
        auth_response = supabase_client.client.auth.sign_in_with_password({
            "email": form_data.username,  # OAuth2 form uses username field for email
            "password": form_data.password
        })
        
        if auth_response.user:
            # Create access token with expiration
            access_token = create_access_token(
                subject=auth_response.user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": auth_response.user.id
            }
        else:
            raise AuthenticationError("Invalid credentials")
    except Exception as e:
        raise AuthenticationError(f"Login failed: {str(e)}")

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True)
):
    """
    Refresh an access token.
    """
    try:
        # Use Supabase auth to refresh the token
        auth_response = supabase_client.client.auth.refresh_session(refresh_token)
        
        if auth_response.user:
            # Create new access token
            access_token = create_access_token(
                subject=auth_response.user.id,
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": auth_response.user.id
            }
        else:
            raise AuthenticationError("Invalid refresh token")
    except Exception as e:
        raise AuthenticationError(f"Token refresh failed: {str(e)}")

@router.post("/reset-password")
async def reset_password(reset_data: PasswordResetRequest):
    """
    Request a password reset.
    """
    try:
        # Use Supabase auth to request password reset
        supabase_client.client.auth.reset_password_email(reset_data.email)
        
        return {
            "message": "If your email is registered, you will receive a password reset link"
        }
    except Exception as e:
        # Return a generic response to avoid email enumeration
        return {
            "message": "If your email is registered, you will receive a password reset link"
        }

@router.post("/reset-password/confirm")
async def reset_password_confirm(reset_data: PasswordResetConfirmRequest):
    """
    Complete the password reset process.
    """
    try:
        # Use Supabase auth to update the password
        response = supabase_client.client.auth.update_user({
            "password": reset_data.new_password
        }, reset_data.token)
        
        if response.user:
            return {
                "message": "Password reset successful"
            }
        else:
            raise HTTPException(status_code=400, detail="Password reset failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Password reset failed: {str(e)}")

@router.post("/logout")
async def logout(
    authorization: str = Header(None)
):
    """
    Log out the current user.
    """
    if not authorization:
        raise AuthenticationError("Authentication required")
    
    try:
        # Use Supabase auth to sign out
        supabase_client.client.auth.sign_out()
        
        return {
            "message": "Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Logout failed: {str(e)}")