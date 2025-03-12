"""
Chat API routes.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.chat.chat_service import chat_service
from app.api.routes.auth import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/chat", tags=["Chat"])

# Models
class ConversationCreateRequest(BaseModel):
    """Conversation create request model"""
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    model: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageCreateRequest(BaseModel):
    """Message create request model"""
    content: str

class MessageResponse(BaseModel):
    """Message response model"""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationListResponse(BaseModel):
    """Conversation list response model"""
    conversations: List[ConversationResponse]
    total: int

class MessageListResponse(BaseModel):
    """Message list response model"""
    messages: List[MessageResponse]
    total: int

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new conversation.
    
    Args:
        request: Conversation create request
        current_user: Current user (from token)
        
    Returns:
        New conversation
    """
    conversation = await chat_service.start_conversation(
        user_id=current_user["id"],
        title=request.title
    )
    
    return conversation

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List user conversations.
    
    Args:
        current_user: Current user (from token)
        
    Returns:
        List of conversations
    """
    from app.db.supabase import supabase_client
    
    conversations = await supabase_client.get_conversations(current_user["id"])
    
    return {
        "conversations": conversations,
        "total": len(conversations)
    }

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get conversation by ID.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user (from token)
        
    Returns:
        Conversation details
    """
    from app.db.supabase import supabase_client
    
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Verify ownership
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def list_messages(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    List messages in a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user (from token)
        
    Returns:
        List of messages
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    messages = await chat_service.get_conversation_history(conversation_id)
    
    return {
        "messages": messages,
        "total": len(messages)
    }

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    request: MessageCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create a new message and get a response.
    
    Args:
        conversation_id: Conversation ID
        request: Message create request
        current_user: Current user (from token)
        
    Returns:
        Assistant response message
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    # Send message and get response
    response = await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user["id"],
        content=request.content
    )
    
    return response

@router.post("/conversations/{conversation_id}/messages/stream")
async def create_message_stream(
    conversation_id: str,
    request: MessageCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new message and stream the response.
    
    Args:
        conversation_id: Conversation ID
        request: Message create request
        current_user: Current user (from token)
        
    Returns:
        Streaming response
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    # Stream response
    async def generate():
        async for chunk in chat_service.stream_message(
            conversation_id=conversation_id,
            user_id=current_user["id"],
            content=request.content
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get a summary of a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user (from token)
        
    Returns:
        Conversation summary
    """
    from app.db.supabase import supabase_client
    
    # Verify conversation exists and belongs to user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    if conversation["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this conversation"
        )
    
    summary = await chat_service.summarize_conversation(conversation_id)
    
    return {"summary": summary}