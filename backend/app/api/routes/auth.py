"""
Authentication routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.supabase import supabase_client
from app.core.exceptions import AuthenticationError, NotFoundError

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Models for request and response
class TokenRequest(BaseModel):
    """Token request model."""
    username: str
    password: str

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    expires_in: int
    user_id: str

class UserCreate(BaseModel):
    """User creation model."""
    email: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    """User model."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current user from a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        User data
        
    Raises:
        AuthenticationError: If the token is invalid
    """
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise AuthenticationError("Could not validate credentials")
        
        # Get the user from the database
        user = await supabase_client.get_user(user_id)
        
        if user is None:
            raise AuthenticationError("User not found")
        
        return user
    except JWTError:
        raise AuthenticationError("Could not validate credentials")

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user
    """
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create the user
    user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "password_hash": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    # Store the user in the database
    created_user = await supabase_client.create_user(user)
    
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user"
        )
    
    # Return the created user (without the password hash)
    return {
        "id": created_user["id"],
        "email": created_user["email"],
        "full_name": created_user["full_name"],
        "created_at": datetime.fromisoformat(created_user["created_at"])
    }

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get an access token.
    
    Args:
        form_data: Username and password
        
    Returns:
        Access token
    """
    # Get the user by email
    user = await supabase_client.get_user_by_email(form_data.username)
    
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    # Verify the password
    if not verify_password(form_data.password, user["password_hash"]):
        raise AuthenticationError("Incorrect email or password")
    
    # Create the access token
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(user["id"], expires_delta=expires_delta)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user["id"]
    }

@router.get("/me", response_model=User)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get the current user's information.
    
    Args:
        user: Current user data
        
    Returns:
        User information
    """
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "created_at": datetime.fromisoformat(user["created_at"])
    }