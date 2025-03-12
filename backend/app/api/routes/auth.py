"""
Authentication routes for the API.
"""
from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.security import create_access_token
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Authentication scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Models
class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    password: str
    name: str

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    """Token data model."""
    user_id: str

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate) -> Any:
    """
    Create a new user.
    """
    try:
        # Create user in Supabase Auth
        response = supabase_client.client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not response.user:
            raise AuthenticationError("Error creating user")
        
        user_id = response.user.id
        
        # Create user profile in database
        user_profile = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "created_at": response.user.created_at,
            "metadata": {}
        }
        
        await supabase_client.create_user(user_profile)
        
        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }
    except Exception as e:
        raise AuthenticationError(f"Error creating user: {str(e)}")

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login.
    """
    try:
        # Login with Supabase Auth
        response = supabase_client.client.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if not response.user:
            raise AuthenticationError("Incorrect email or password")
        
        user_id = response.user.id
        
        # Generate access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        }
    except Exception as e:
        raise AuthenticationError("Incorrect email or password")

@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Logout user.
    """
    try:
        supabase_client.client.auth.sign_out()
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise AuthenticationError(f"Error logging out: {str(e)}")

@router.post("/reset-password")
async def reset_password(email: EmailStr) -> Dict[str, str]:
    """
    Reset password for user.
    """
    try:
        supabase_client.client.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a password reset link has been sent"}