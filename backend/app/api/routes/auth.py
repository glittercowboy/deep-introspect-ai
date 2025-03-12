"""
API routes for authentication.
"""
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# Request and response models
class Token(BaseModel):
    """Response model for token."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class UserCreate(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    """Response model for user."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: str

# API Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register a new user.
    """
    try:
        # Check if the user already exists
        existing_user = await supabase_client.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user in Supabase
        user = await supabase_client.create_user({
            "email": user_data.email,
            "password_hash": hashed_password,
            "full_name": user_data.full_name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None,
            "metadata": {}
        })
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return user
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token using OAuth2 password flow.
    """
    try:
        # Get user by email
        user = await supabase_client.get_user_by_email(form_data.username)
        
        if not user:
            raise AuthenticationError("Incorrect email or password")
        
        # Verify password
        is_password_valid = verify_password(form_data.password, user["password_hash"])
        
        if not is_password_valid:
            raise AuthenticationError("Incorrect email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user["id"], 
            expires_delta=access_token_expires
        )
        
        # Update last login
        await supabase_client.update_user(user["id"], {
            "last_login": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            "user_id": user["id"]
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Login with email and password.
    """
    form_data = OAuth2PasswordRequestForm(
        username=user_data.email,
        password=user_data.password,
        scope=""
    )
    return await login_for_access_token(form_data)