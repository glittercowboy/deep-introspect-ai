"""
Base models for API data validation.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class ResponseBase(BaseModel):
    """Base response model."""
    message: str = Field(default="success")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: Dict[str, Any] = Field(..., 
        example={
            "code": "VALIDATION_ERROR",
            "message": "Validation error",
            "details": [{"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}]
        }
    )

class MetadataBase(BaseModel):
    """Base class for metadata model."""
    model_config = ConfigDict(extra='allow')

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    """User creation model."""
    password: str

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    
class UserInDB(UserBase):
    """User model as stored in database."""
    id: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class User(UserInDB):
    """User model returned to client."""
    pass

class TokenData(BaseModel):
    """Token data model for JWT."""
    sub: str
    exp: int
    
class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class IDResponse(ResponseBase):
    """Response with an ID."""
    id: str

class ConversationBase(BaseModel):
    """Base conversation model."""
    title: str

class ConversationCreate(ConversationBase):
    """Conversation creation model."""
    pass
    
class ConversationUpdate(BaseModel):
    """Conversation update model."""
    title: Optional[str] = None
    
class Conversation(ConversationBase):
    """Conversation model."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    model: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageBase(BaseModel):
    """Base message model."""
    content: str
    role: str = Field(..., description="Role of the message sender: user or assistant")
    
class MessageCreate(MessageBase):
    """Message creation model."""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class Message(MessageBase):
    """Message model."""
    id: str
    conversation_id: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class InsightBase(BaseModel):
    """Base insight model."""
    type: str
    content: str
    evidence: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    
class Insight(InsightBase):
    """Insight model."""
    id: str
    user_id: str
    conversation_id: Optional[str] = None
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationSummary(BaseModel):
    """Conversation summary model."""
    id: str
    title: str
    summary: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class UserSummary(BaseModel):
    """User summary model."""
    summary: str
    categories: Dict[str, Any]
    
class InsightGraph(BaseModel):
    """Insight graph model."""
    nodes: List[Dict[str, Any]]
    links: List[Dict[str, Any]]
    
class UserInsights(BaseModel):
    """User insights model."""
    insights: List[Insight]
    summary: UserSummary
    graph: InsightGraph