"""
API routes for authentication.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.core.exceptions import AuthenticationError
from app.db.supabase import supabase_client
from app.api.models.auth import (
    UserCredentials,
    SignUpRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)

# Create router
router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Logger
logger = logging.getLogger(__name__)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current user from the token.
    
    Args:
        token: JWT token
        
    Returns:
        User data
    
    Raises:
        AuthenticationError: If the token is invalid or expired
    """
    try:
        # Verify the token with Supabase
        response = supabase_client.client.auth.get_user(token)
        user = response.user
        
        if not user:
            raise AuthenticationError("Invalid or expired token")
        
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise AuthenticationError("Invalid or expired token")


@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: SignUpRequest):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        User and token data
    """
    try:
        # Create user in Supabase
        response = supabase_client.client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name
                }
            }
        })
        
        user = response.user
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Format user data for response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.user_metadata.get("name", ""),
            created_at=user.created_at
        )
        
        # Format token for response
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(
            user=user_response,
            token=token_response
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return access token.
    
    Args:
        form_data: Form data with username and password
        
    Returns:
        User and token data
    """
    try:
        # Sign in user with Supabase
        response = supabase_client.client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        user = response.user
        session = response.session
        
        if not user or not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(
            subject=user.id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Format user data for response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            name=user.user_metadata.get("name", ""),
            created_at=user.created_at
        )
        
        # Format token for response
        token_response = TokenResponse(
            access_token=session.access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(
            user=user_response,
            token=token_response
        )
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )


@router.post("/reset-password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(reset_data: PasswordResetRequest):
    """
    Request a password reset.
    
    Args:
        reset_data: Password reset request data
    """
    try:
        # Send password reset email with Supabase
        response = supabase_client.client.auth.reset_password_email(reset_data.email)
        
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Error sending password reset: {str(e)}")
        return {"message": "Password reset email sent"}  # Don't reveal if email exists


@router.post("/reset-password-confirm", status_code=status.HTTP_200_OK)
async def reset_password_confirm(reset_data: PasswordResetConfirm):
    """
    Confirm password reset.
    
    Args:
        reset_data: Password reset confirmation data
    """
    try:
        # Update user with new password
        response = supabase_client.client.auth.update_user({
            "password": reset_data.new_password
        }, reset_data.token)
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )
        
        return {"message": "Password reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user data.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.user_metadata.get("name", ""),
        created_at=current_user.created_at
    )
