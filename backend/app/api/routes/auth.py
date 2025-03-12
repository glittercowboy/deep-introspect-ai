"""
Authentication API routes.
"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import create_access_token
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Models
class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class SignUpRequest(BaseModel):
    """Sign up request model"""
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    created_at: str

@router.post("/signup", response_model=TokenResponse)
async def sign_up(request: SignUpRequest) -> Dict[str, Any]:
    """
    Sign up a new user.
    
    Args:
        request: Sign up request containing email, password, and name
        
    Returns:
        Token response
    """
    try:
        # Sign up with Supabase Auth
        response = supabase_client.client.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        # Check if user was created successfully
        if not response.user:
            raise AuthenticationError("Failed to create user")
        
        user_id = response.user.id
        
        # Create user profile in the database
        await supabase_client.create_user({
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "created_at": response.user.created_at,
            "last_sign_in_at": response.user.last_sign_in_at,
            "metadata": {}
        })
        
        # Create access token
        access_token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user_id
        }
    except Exception as e:
        raise AuthenticationError(f"Error during sign up: {str(e)}")

@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """
    Login to get access token.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        
    Returns:
        Token response
    """
    try:
        # Sign in with Supabase Auth
        response = supabase_client.client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        # Check if login was successful
        if not response.user:
            raise AuthenticationError("Invalid credentials")
        
        user_id = response.user.id
        
        # Create access token
        access_token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user_id
        }
    except Exception as e:
        raise AuthenticationError(f"Error during login: {str(e)}")

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Logout and invalidate token.
    
    Args:
        token: Access token
        
    Returns:
        Success message
    """
    try:
        # Sign out with Supabase Auth
        supabase_client.client.auth.sign_out()
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise AuthenticationError(f"Error during logout: {str(e)}")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get current user from token.
    
    Args:
        token: Access token
        
    Returns:
        User data
    """
    try:
        # Verify token and get user ID
        user = supabase_client.client.auth.get_user(token)
        
        if not user:
            raise AuthenticationError("Invalid token")
        
        # Get user profile from database
        user_data = await supabase_client.get_user(user.id)
        
        if not user_data:
            raise AuthenticationError("User not found")
        
        return user_data
    except Exception as e:
        raise AuthenticationError(f"Error getting current user: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_me(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user profile.
    
    Args:
        user: Current user (from token)
        
    Returns:
        User profile
    """
    return user