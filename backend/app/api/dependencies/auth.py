"""
Authentication dependencies for FastAPI.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.db.supabase import supabase_client
from app.api.models.auth import TokenPayload
from app.core.exceptions import AuthenticationError

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Get the current authenticated user from the token.
    
    Args:
        token: JWT token from OAuth2 scheme
        
    Returns:
        User data dictionary
        
    Raises:
        AuthenticationError: If the token is invalid or the user doesn't exist
    """
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # Validate token payload
        token_data = TokenPayload(**payload)
        
        # Check if token is expired
        if token_data.exp < int(import_module("time").time()):
            raise AuthenticationError("Token expired")
        
        # Get user ID from token
        user_id = token_data.sub
        if not user_id:
            raise AuthenticationError("Invalid token")
        
        # Get user from database
        user = await supabase_client.get_user(user_id)
        if not user:
            raise AuthenticationError("User not found")
        
        return user
        
    except (JWTError, ValidationError):
        raise AuthenticationError("Invalid authentication credentials")


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get the current active user.
    
    Args:
        current_user: User data from get_current_user
        
    Returns:
        User data dictionary
        
    Raises:
        AuthenticationError: If the user is disabled
    """
    if current_user.get("is_disabled"):
        raise AuthenticationError("Inactive user")
    
    return current_user


def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Get the current user if authenticated, otherwise return None.
    
    Args:
        token: Optional JWT token from OAuth2 scheme
        
    Returns:
        User data dictionary or None if not authenticated
    """
    if not token:
        return None
    
    try:
        # Decode the token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # Validate token payload
        token_data = TokenPayload(**payload)
        
        # Get user ID from token
        user_id = token_data.sub
        if not user_id:
            return None
        
        # Get user from database
        user = await supabase_client.get_user(user_id)
        return user
    except (JWTError, ValidationError):
        return None