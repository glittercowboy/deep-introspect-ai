"""
User API routes.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.db.supabase import supabase_client
from app.api.routes.auth import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/users", tags=["Users"])

# Models
class UserUpdateRequest(BaseModel):
    """User update request model"""
    name: str = None
    metadata: Dict[str, Any] = None

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    name: str
    created_at: str
    last_sign_in_at: str = None
    metadata: Dict[str, Any] = None

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current user profile.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        User profile
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    request: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update current user profile.
    
    Args:
        request: User update request
        current_user: Current user (from token)
        
    Returns:
        Updated user profile
    """
    update_data = {}
    
    if request.name is not None:
        update_data["name"] = request.name
    
    if request.metadata is not None:
        update_data["metadata"] = request.metadata
    
    if not update_data:
        return current_user
    
    # Update user in database
    updated_user = await supabase_client.update_user(current_user["id"], update_data)
    
    if not updated_user:
        raise NotFoundError("User not found")
    
    return updated_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current user (from token)
        
    Returns:
        User profile
    """
    # Only allow getting own user for now (can be expanded with admin permissions)
    if user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access other users"
        )
    
    user = await supabase_client.get_user(user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    return user