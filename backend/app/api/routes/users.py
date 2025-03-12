"""
User API routes.
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.models.base import (
    User,
    UserUpdate,
    ResponseBase,
)
from app.api.dependencies.auth import get_current_user
from app.db.supabase import supabase_client
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Get current user information.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user_data: UserUpdate
):
    """
    Update current user information.
    """
    # Check if email is changed and if it's already in use
    if user_data.email and user_data.email != current_user.email:
        existing_user = await supabase_client.get_user_by_email(user_data.email)
        if existing_user:
            raise ValidationError("Email already in use")
    
    # Update user data
    user_dict = user_data.model_dump(exclude_unset=True)
    if not user_dict:
        return current_user
    
    # Update user in database
    updated_user = await supabase_client.update_user(current_user.id, user_dict)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    return User(**updated_user)

@router.delete("/me", response_model=ResponseBase)
async def delete_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Delete current user account.
    """
    # Delete user from database
    success = await supabase_client.delete_user(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return ResponseBase(message="User deleted successfully")

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get user by ID.
    
    Note: Currently only allows users to fetch their own profile.
    """
    # Only allow users to fetch their own profile
    if user_id != current_user.id:
        raise ValidationError("Not authorized to access this user's data")
    
    return current_user