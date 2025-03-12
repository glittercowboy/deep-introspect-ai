"""
Chat API routes.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Path, Query, Body
from fastapi.responses import StreamingResponse
from app.api.models.chat import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationListResponse
)
from app.api.models.user import User
from app.services.chat.chat_service import chat_service
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/v1/chat", tags=["Chat"])

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation.
    """
    conversation = await chat_service.start_conversation(
        user_id=current_user.id,
        title=conversation_data.title
    )
    
    return conversation

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all conversations for the current user.
    """
    from app.db.supabase import supabase_client
    
    conversations = await supabase_client.get_conversations(current_user.id)
    
    # Apply pagination
    paginated_conversations = conversations[offset:offset+limit]
    
    return {
        "conversations": paginated_conversations,
        "total": len(conversations),
        "limit": limit,
        "offset": offset
    }

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str = Path(..., title="The ID of the conversation to get"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific conversation.
    """
    from app.db.supabase import supabase_client
    
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if the conversation belongs to the user
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str = Path(..., title="The ID of the conversation to get messages for"),
    current_user: User = Depends(get_current_user)
):
    """
    Get all messages for a specific conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get messages
    messages = await chat_service.get_conversation_history(conversation_id)
    
    return messages

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    conversation_id: str = Path(..., title="The ID of the conversation to send the message to"),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message in a conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Send message and get response
    response = await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=message_data.content
    )
    
    return response

@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    message_data: MessageCreate,
    conversation_id: str = Path(..., title="The ID of the conversation to send the message to"),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message in a conversation and stream the response.
    """
    from app.db.supabase import supabase_client
    
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Stream response
    async def response_generator():
        async for chunk in chat_service.stream_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=message_data.content
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str = Path(..., title="The ID of the conversation to summarize"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of a conversation.
    """
    from app.db.supabase import supabase_client
    
    # Verify that the conversation exists and belongs to the user
    conversation = await supabase_client.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Get summary
    summary = await chat_service.summarize_conversation(conversation_id)
    
    return {"summary": summary}