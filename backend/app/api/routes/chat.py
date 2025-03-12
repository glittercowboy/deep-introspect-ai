"""
Chat API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.services.chat.chat_service import chat_service
from app.api.routes.auth import get_current_user
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/chat", tags=["chat"])

# Models for request and response
class Message(BaseModel):
    """Message model."""
    id: str
    role: str
    content: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class Conversation(BaseModel):
    """Conversation model."""
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    model: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationCreate(BaseModel):
    """Conversation creation model."""
    title: Optional[str] = None
    model: Optional[str] = "anthropic"
    metadata: Optional[Dict[str, Any]] = None

class MessageCreate(BaseModel):
    """Message creation model."""
    content: str = Field(..., min_length=1)
    model: Optional[str] = "anthropic"
    metadata: Optional[Dict[str, Any]] = None

class ConversationSummary(BaseModel):
    """Conversation summary model."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    message_count: int = 0

@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new conversation.
    
    Args:
        conversation_data: Conversation data
        current_user: Current user data
        
    Returns:
        Created conversation
    """
    user_id = current_user["id"]
    
    conversation = await chat_service.start_conversation(
        user_id,
        title=conversation_data.title
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    
    # Process the conversation metadata before returning
    return {
        "id": conversation["id"],
        "user_id": conversation["user_id"],
        "title": conversation["title"],
        "created_at": datetime.fromisoformat(conversation["created_at"]),
        "updated_at": datetime.fromisoformat(conversation["updated_at"]),
        "model": conversation.get("model", "anthropic"),
        "metadata": conversation.get("metadata", {})
    }

@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all conversations for the current user.
    
    Args:
        current_user: Current user data
        
    Returns:
        List of conversations
    """
    user_id = current_user["id"]
    
    # Get all conversations for the user
    conversations = await chat_service.get_user_conversations(user_id)
    
    # Format the response
    result = []
    for conv in conversations:
        # Get the most recent message for this conversation
        messages = await chat_service.get_conversation_history(conv["id"])
        
        last_message = None
        if messages:
            last_message_obj = messages[-1]
            if last_message_obj["role"] == "assistant":
                last_message = last_message_obj["content"][:100] + "..." if len(last_message_obj["content"]) > 100 else last_message_obj["content"]
        
        result.append({
            "id": conv["id"],
            "title": conv["title"],
            "created_at": datetime.fromisoformat(conv["created_at"]),
            "updated_at": datetime.fromisoformat(conv["updated_at"]),
            "last_message": last_message,
            "message_count": len(messages)
        })
    
    # Sort by updated_at
    result.sort(key=lambda c: c["updated_at"], reverse=True)
    
    return result

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a conversation by ID.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user data
        
    Returns:
        Conversation data
    """
    user_id = current_user["id"]
    
    # Get the conversation
    conversation = await chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    
    # Check that the conversation belongs to the user
    if conversation["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Process the conversation metadata before returning
    return {
        "id": conversation["id"],
        "user_id": conversation["user_id"],
        "title": conversation["title"],
        "created_at": datetime.fromisoformat(conversation["created_at"]),
        "updated_at": datetime.fromisoformat(conversation["updated_at"]),
        "model": conversation.get("model", "anthropic"),
        "metadata": conversation.get("metadata", {})
    }

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_conversation_messages(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all messages for a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user data
        
    Returns:
        List of messages
    """
    user_id = current_user["id"]
    
    # Get the conversation
    conversation = await chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    
    # Check that the conversation belongs to the user
    if conversation["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Get the messages
    messages = await chat_service.get_conversation_history(conversation_id)
    
    # Format the response
    result = []
    for msg in messages:
        result.append({
            "id": msg["id"],
            "role": msg["role"],
            "content": msg["content"],
            "created_at": datetime.fromisoformat(msg["created_at"]),
            "metadata": msg.get("metadata", {})
        })
    
    return result

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to a conversation.
    
    Args:
        conversation_id: Conversation ID
        message_data: Message data
        current_user: Current user data
        
    Returns:
        Assistant response message
    """
    user_id = current_user["id"]
    
    # Get the conversation
    conversation = await chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    
    # Check that the conversation belongs to the user
    if conversation["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Send the message and get the response
    response = await chat_service.send_message(
        conversation_id,
        user_id,
        message_data.content
    )
    
    # Format the response
    return {
        "id": response["id"],
        "role": response["role"],
        "content": response["content"],
        "created_at": datetime.fromisoformat(response["created_at"]),
        "metadata": response.get("metadata", {})
    }

@router.post("/conversations/{conversation_id}/messages/stream")
async def create_message_stream(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to a conversation and stream the response.
    
    Args:
        conversation_id: Conversation ID
        message_data: Message data
        current_user: Current user data
        
    Returns:
        Streaming response of assistant message chunks
    """
    user_id = current_user["id"]
    
    # Get the conversation
    conversation = await chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    
    # Check that the conversation belongs to the user
    if conversation["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Create a generator for the streaming response
    async def generate():
        async for chunk in chat_service.stream_message(
            conversation_id,
            user_id,
            message_data.content
        ):
            # Yield the chunk as a server-sent event
            yield f"data: {chunk}\n\n"
    
    # Return a streaming response
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a summary of a conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current user data
        
    Returns:
        Conversation summary
    """
    user_id = current_user["id"]
    
    # Get the conversation
    conversation = await chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError(f"Conversation {conversation_id} not found")
    
    # Check that the conversation belongs to the user
    if conversation["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Get the summary
    summary = await chat_service.summarize_conversation(conversation_id)
    
    return {"summary": summary}