"""
Authentication and authorization dependencies.
"""
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.db.supabase import supabase_client
from app.api.models.base import User, TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from OAuth2PasswordBearer
        
    Returns:
        Current authenticated user
        
    Raises:
        AuthenticationError: If authentication fails
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError("Could not validate credentials")
        
        token_data = TokenData(sub=user_id, exp=payload.get("exp"))
    except JWTError:
        raise AuthenticationError("Could not validate credentials")
    
    # Get user from database
    user = await supabase_client.get_user(user_id)
    
    if user is None:
        raise AuthenticationError("User not found")
    
    return User(**user)

async def get_optional_user(token: Annotated[str, Depends(oauth2_scheme)]) -> Optional[User]:
    """
    Get the current authenticated user if a token is provided, otherwise return None.
    
    Args:
        token: JWT token from OAuth2PasswordBearer
        
    Returns:
        Current authenticated user or None
    """
    try:
        return await get_current_user(token)
    except HTTPException:
        return None