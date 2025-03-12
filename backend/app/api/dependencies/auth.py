"""
Authentication dependencies for API routes.
"""
import logging
from typing import Dict, Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from the request
        
    Returns:
        User data
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Extract user ID from the token
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user data from the database
    user = await supabase_client.get_user(user_id)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[Dict[str, Any]]:
    """
    Get the current user if authenticated, or None if not.
    This is useful for endpoints that work both for authenticated and anonymous users.
    
    Args:
        token: Optional JWT token
        
    Returns:
        User data or None
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None