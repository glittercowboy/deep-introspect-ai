"""
User routes for the API.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token
from app.db.supabase import supabase_client
from app.core.exceptions import NotFoundError, AuthenticationError, AuthorizationError
from app.api.routes.auth import oauth2_scheme

router = APIRouter(prefix="/users", tags=["Users"])

# Models
class UserProfile(BaseModel):
    """User profile model."""
    id: str
    email: EmailStr
    name: str
    metadata: Dict[str, Any] = {}

class UserUpdate(BaseModel):
    """User update model."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    metadata: Optional[Dict[str, Any]] = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Could not validate credentials")
    except JWTError:
        raise AuthenticationError("Could not validate credentials")
    
    user = await supabase_client.get_user(user_id)
    if user is None:
        raise NotFoundError("User not found")
    
    return user

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.patch("/me", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Update current user profile.
    """
    update_data = user_update.dict(exclude_unset=True)
    
    # Don't allow updating the ID
    if "id" in update_data:
        del update_data["id"]
    
    # Merge metadata
    if "metadata" in update_data and update_data["metadata"]:
        current_metadata = current_user.get("metadata", {})
        merged_metadata = {**current_metadata, **update_data["metadata"]}
        update_data["metadata"] = merged_metadata
    
    updated_user = await supabase_client.update_user(
        current_user["id"], update_data
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    return updated_user

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Any:
    """
    Get a specific user profile by ID.
    """
    # Only allow users to view their own profile or admins to view any profile
    is_admin = current_user.get("metadata", {}).get("is_admin", False)
    if current_user["id"] != user_id and not is_admin:
        raise AuthorizationError("Not authorized to access this profile")
    
    user = await supabase_client.get_user(user_id)
    if not user:
        raise NotFoundError("User not found")
    
    return user