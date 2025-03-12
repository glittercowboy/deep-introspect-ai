"""
Chat API routes.
"""
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.models.base import (
    User,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    MessageCreate,
    Message,
    ResponseBase,
    IDResponse,
)
from app.api.dependencies.auth import get_current_user
from app.services.chat.chat_service import chat_service
from app.services.memory.memory_service import memory_service
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new conversation.
    """
    new_conversation = await chat_service.start_conversation(
        user_id=current_user.id,
        title=conversation_data.title
    )
    
    if not new_conversation:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    
    return Conversation(**new_conversation)

@router.get("/conversations", response_model=List[ConversationSummary])
async def get_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all conversations for the current user.
    """
    conversations = await memory_service.get_user_conversations(current_user.id)
    
    # Convert to ConversationSummary objects
    result = []
    for conv in conversations:
        # Get message count
        messages = await memory_service.get_conversation_history(conv["id"])
        
        # Generate summary if not already available
        summary = ""
        if "summary" in conv["metadata"] and conv["metadata"]["summary"]:
            summary = conv["metadata"]["summary"]
        else:
            # Only generate for conversations with enough messages
            if len(messages) >= 3:
                summary = await chat_service.summarize_conversation(conv["id"])
        
        result.append(
            ConversationSummary(
                id=conv["id"],
                title=conv["title"],
                summary=summary,
                message_count=len(messages),
                created_at=conv["created_at"],
                updated_at=conv["updated_at"]
            )
        )
    
    # Apply pagination
    paginated_result = result[skip:skip+limit]
    
    return paginated_result

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a conversation by ID.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to access this conversation")
    
    return Conversation(**conversation)

@router.delete("/conversations/{conversation_id}", response_model=ResponseBase)
async def delete_conversation(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Delete a conversation.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to delete this conversation")
    
    # Delete conversation
    success = await memory_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )
    
    return ResponseBase(message="Conversation deleted successfully")

@router.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get all messages for a conversation.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to access this conversation")
    
    # Get messages
    messages = await memory_service.get_conversation_history(conversation_id)
    
    return [Message(**msg) for msg in messages]

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def send_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Send a message to a conversation.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to access this conversation")
    
    # Only user messages can be sent through this endpoint
    if message_data.role != "user":
        raise ValidationError("Only user messages can be sent through this endpoint")
    
    # Send message and get response
    response = await chat_service.send_message(
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=message_data.content
    )
    
    return Message(**response)

@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Send a message and stream the response.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to access this conversation")
    
    # Only user messages can be sent through this endpoint
    if message_data.role != "user":
        raise ValidationError("Only user messages can be sent through this endpoint")
    
    # Stream response
    async def stream_generator():
        async for chunk in chat_service.stream_message(
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=message_data.content
        ):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream"
    )

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a summary of a conversation.
    """
    # Get conversation from database
    conversation = await memory_service.get_conversation(conversation_id)
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Check if the conversation belongs to the current user
    if conversation["user_id"] != current_user.id:
        raise ValidationError("Not authorized to access this conversation")
    
    # Generate summary
    summary = await chat_service.summarize_conversation(conversation_id)
    
    return {"summary": summary}