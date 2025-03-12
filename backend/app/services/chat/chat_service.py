"""
Chat service for handling conversations and interactions.
"""
import logging
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from app.services.llm.factory import llm_factory
from app.services.memory.memory_service import memory_service
from app.services.knowledge.knowledge_service import knowledge_service
from app.services.insights.insights_service import insights_service
from app.db.supabase import supabase_client

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for managing chat conversations.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(ChatService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the chat service."""
        self.system_message = """You are DeepIntrospect AI, a groundbreaking self-reflection AI chatbot designed to help users understand themselves better through conversation. 
        Your purpose is to facilitate personal growth through AI-assisted introspection.
        
        As you chat with users:
        - Be empathetic, thoughtful, and insightful
        - Ask probing but respectful questions that help users reflect on their thoughts, beliefs, patterns, and behaviors
        - Maintain continuity across the conversation
        - Avoid generic platitudes or shallow responses
        - When appropriate, offer observations or potential patterns you notice, but be humble and open to correction
        - Tailor your responses to the individual user based on what you learn about them
        - Help users gain valuable insights about themselves through conversation
        
        You are here to help users understand themselves better - not to give generic advice or act as a medical professional."""
        
        logger.info("Chat service initialized")
    
    async def get_user_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversations
        """
        return await supabase_client.get_conversations(user_id)
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data
        """
        return await supabase_client.get_conversation(conversation_id)
    
    async def update_conversation(self, conversation_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a conversation.
        
        Args:
            conversation_id: Conversation ID
            data: Data to update
            
        Returns:
            Updated conversation data
        """
        return await supabase_client.update_conversation(conversation_id, data)
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if successful
        """
        return await supabase_client.delete_conversation(conversation_id)
    
    async def start_conversation(self, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new conversation.
        
        Args:
            user_id: User ID
            title: Optional conversation title
            
        Returns:
            Conversation data
        """
        # Create conversation
        conversation_id = str(uuid.uuid4())
        
        # Generate a title if not provided
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create conversation in database
        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "model": "anthropic",  # Default model
            "metadata": {}
        }
        
        conversation = await supabase_client.create_conversation(conversation_data)
        
        # Add welcome message from assistant
        welcome_message = """Hello! I'm DeepIntrospect AI, designed to help you better understand yourself through thoughtful conversation. As we talk, I'll learn about your thoughts, patterns, and perspectives.

How are you feeling today, and what would you like to explore or reflect on?"""
        
        await self.add_message(
            conversation_id,
            "assistant",
            welcome_message
        )
        
        # Initialize conversation in memory service
        await memory_service.create_conversation(user_id, title)
        
        return conversation
    
    async def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user or assistant)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Created message data
        """
        message_id = str(uuid.uuid4())
        
        # Create message in database
        message_data = {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        message = await supabase_client.create_message(message_data)
        
        # Update conversation timestamp
        await supabase_client.update_conversation(
            conversation_id, 
            {"updated_at": datetime.now().isoformat()}
        )
        
        # Add to memory service
        await memory_service.add_message(conversation_id, role, content, metadata)
        
        return message
    
    async def send_message(
        self, 
        conversation_id: str,
        user_id: str, 
        content: str
    ) -> Dict[str, Any]:
        """
        Send a user message and get a response.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            
        Returns:
            Response data
        """
        # Add user message
        user_message = await self.add_message(
            conversation_id,
            "user",
            content
        )
        
        # Get conversation
        conversation = await supabase_client.get_conversation(conversation_id)
        model = conversation.get("model", "anthropic") if conversation else "anthropic"
        
        # Set the model in the LLM factory
        llm_factory.set_default_provider(model)
        
        # Get conversation context
        context_messages = await memory_service.get_conversation_context(
            conversation_id,
            query=content,
            limit=20
        )
        
        # Add system message
        messages = [{"role": "system", "content": self.system_message}] + context_messages
        
        # Generate response
        llm_service = llm_factory.get_service()
        response_content = await llm_service.generate_chat(
            messages,
            temperature=0.7
        )
        
        # Add assistant message
        assistant_message = await self.add_message(
            conversation_id,
            "assistant",
            response_content
        )
        
        # Process conversation for knowledge and insights (run in background)
        asyncio.create_task(self._process_conversation_insights(user_id, conversation_id))
        
        return assistant_message
    
    async def stream_message(
        self,
        conversation_id: str,
        user_id: str,
        content: str
    ) -> AsyncGenerator[str, None]:
        """
        Send a user message and stream the response.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            content: Message content
            
        Yields:
            Response chunks
        """
        # Add user message
        user_message = await self.add_message(
            conversation_id,
            "user",
            content
        )
        
        # Get conversation
        conversation = await supabase_client.get_conversation(conversation_id)
        model = conversation.get("model", "anthropic") if conversation else "anthropic"
        
        # Set the model in the LLM factory
        llm_factory.set_default_provider(model)
        
        # Get conversation context
        context_messages = await memory_service.get_conversation_context(
            conversation_id,
            query=content,
            limit=20
        )
        
        # Add system message
        messages = [{"role": "system", "content": self.system_message}] + context_messages
        
        # Generate streaming response
        llm_service = llm_factory.get_service()
        full_response = ""
        async for chunk in llm_service.generate_stream(
            messages,
            temperature=0.7
        ):
            full_response += chunk
            yield chunk
        
        # Add assistant message
        assistant_message = await self.add_message(
            conversation_id,
            "assistant",
            full_response
        )
        
        # Process conversation for knowledge and insights (run in background)
        asyncio.create_task(self._process_conversation_insights(user_id, conversation_id))
    
    async def _process_conversation_insights(self, user_id: str, conversation_id: str) -> None:
        """
        Process conversation for insights in the background.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
        """
        try:
            # Get conversation messages
            messages = await self.get_conversation_history(conversation_id)
            
            if len(messages) < 6:  # Wait until there's enough conversation
                return
            
            # Process with knowledge service
            await knowledge_service.process_conversation(user_id, conversation_id, messages)
            
            # Generate insights if conversation is substantial
            if len(messages) >= 10:
                await insights_service.generate_conversation_insights(user_id, conversation_id)
        except Exception as e:
            logger.error(f"Error processing conversation insights: {str(e)}")
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        return await supabase_client.get_messages(conversation_id)
    
    async def summarize_conversation(self, conversation_id: str) -> str:
        """
        Generate a summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        # Get conversation messages
        messages = await self.get_conversation_history(conversation_id)
        
        if not messages:
            return "No messages in this conversation."
        
        # Prepare prompt for the LLM
        prompt = "Summarize the following conversation in a concise paragraph:\n\n"
        
        for msg in messages:
            prompt += f"{msg['role'].capitalize()}: {msg['content']}\n\n"
        
        prompt += "Summary:"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate summary
        summary = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with summarizing conversations. Create a concise summary that captures the main topics and insights from the conversation.",
            temperature=0.3
        )
        
        return summary
    
    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get insights for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            User insights data
        """
        # Get raw insights
        raw_insights = await insights_service.get_user_insights(user_id)
        
        # Get user summary
        summary = await insights_service.generate_user_summary(user_id)
        
        # Get insight graph
        graph = await insights_service.generate_insight_graph(user_id)
        
        return {
            "insights": raw_insights,
            "summary": summary,
            "graph": graph
        }

# Create a singleton instance
chat_service = ChatService()