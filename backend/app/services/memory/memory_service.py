"""
Memory service for managing conversation history and context.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import httpx
from app.core.config import settings
from app.db.supabase import supabase_client
from app.services.llm.factory import llm_factory

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Service for managing conversation memory and context.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(MemoryService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the memory service."""
        self.mem0_api_key = settings.MEM0_API_KEY
        self.mem0_base_url = "https://api.mem0.ai"
        logger.info("Memory service initialized")
    
    async def create_conversation(self, user_id: str, title: str = None) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            user_id: User ID
            title: Optional conversation title
            
        Returns:
            Conversation data
        """
        conversation_id = str(uuid.uuid4())
        
        # Generate a title if not provided
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create conversation in Supabase
        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "model": "anthropic",  # Default model
            "metadata": {}
        }
        
        result = await supabase_client.create_conversation(conversation_data)
        
        # Initialize conversation in mem0
        await self._create_mem0_conversation(conversation_id, user_id)
        
        return result
    
    async def _create_mem0_conversation(self, conversation_id: str, user_id: str) -> bool:
        """
        Create a conversation in mem0.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mem0_base_url}/conversations",
                    headers={
                        "Authorization": f"Bearer {self.mem0_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "metadata": {
                            "source": "deep-introspect-ai"
                        }
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Created mem0 conversation: {conversation_id}")
                    return True
                else:
                    logger.error(f"Failed to create mem0 conversation: {response.text}")
                    return False
                
        except Exception as e:
            logger.error(f"Error creating mem0 conversation: {str(e)}")
            return False
    
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
            Message data
        """
        message_id = str(uuid.uuid4())
        
        # Create message in Supabase
        message_data = {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        result = await supabase_client.create_message(message_data)
        
        # Add message to mem0
        await self._add_mem0_message(conversation_id, role, content)
        
        # Update conversation timestamp
        await supabase_client.update_conversation(
            conversation_id, 
            {"updated_at": datetime.now().isoformat()}
        )
        
        return result
    
    async def _add_mem0_message(self, conversation_id: str, role: str, content: str) -> bool:
        """
        Add a message to mem0.
        
        Args:
            conversation_id: Conversation ID
            role: Message role
            content: Message content
            
        Returns:
            True if successful
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mem0_base_url}/conversations/{conversation_id}/messages",
                    headers={
                        "Authorization": f"Bearer {self.mem0_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "role": role,
                        "content": content
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"Added message to mem0 conversation: {conversation_id}")
                    return True
                else:
                    logger.error(f"Failed to add message to mem0 conversation: {response.text}")
                    return False
                
        except Exception as e:
            logger.error(f"Error adding message to mem0 conversation: {str(e)}")
            return False
    
    async def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages
        """
        return await supabase_client.get_messages(conversation_id)
    
    async def get_conversation_context(
        self, 
        conversation_id: str, 
        query: str = None,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get context-relevant messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            query: Optional query to find relevant messages
            limit: Maximum number of messages to return
            
        Returns:
            List of messages formatted for LLM context
        """
        if query:
            # Get semantically relevant messages from mem0
            return await self._get_mem0_relevant_messages(conversation_id, query, limit)
        else:
            # Get most recent messages
            messages = await supabase_client.get_messages(conversation_id)
            
            # Format for LLM
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in messages[-limit:]
            ]
            
            return formatted_messages
    
    async def _get_mem0_relevant_messages(
        self, 
        conversation_id: str, 
        query: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get relevant messages from mem0.
        
        Args:
            conversation_id: Conversation ID
            query: Search query
            limit: Maximum number of messages
            
        Returns:
            List of relevant messages
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mem0_base_url}/conversations/{conversation_id}/search",
                    headers={
                        "Authorization": f"Bearer {self.mem0_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": query,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Format for LLM
                    formatted_messages = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in results["messages"]
                    ]
                    
                    return formatted_messages
                else:
                    logger.error(f"Failed to search mem0 conversation: {response.text}")
                    # Fallback to recent messages
                    messages = await supabase_client.get_messages(conversation_id)
                    
                    # Format for LLM
                    formatted_messages = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in messages[-limit:]
                    ]
                    
                    return formatted_messages
                
        except Exception as e:
            logger.error(f"Error searching mem0 conversation: {str(e)}")
            # Fallback to recent messages
            messages = await supabase_client.get_messages(conversation_id)
            
            # Format for LLM
            formatted_messages = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in messages[-limit:]
            ]
            
            return formatted_messages
    
    async def summarize_conversation(self, conversation_id: str) -> str:
        """
        Generate a summary of a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation summary
        """
        messages = await supabase_client.get_messages(conversation_id)
        
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
    
    async def get_conversation_insights(self, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get insights from a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            
        Returns:
            List of insights
        """
        # Get conversation messages
        messages = await supabase_client.get_messages(conversation_id)
        
        if not messages:
            return []
        
        # Prepare prompt for the LLM
        prompt = """Extract key insights about the user from the following conversation. 
        Focus on beliefs, values, patterns, preferences, traits, goals, and habits that emerge from the conversation.
        Format each insight as a JSON object with 'type' (belief, value, pattern, etc.), 'content' (the insight itself), 
        and 'evidence' (specific text from the conversation that supports this insight).
        Return a list of JSON objects:
        
        Conversation:
        """
        
        for msg in messages:
            prompt += f"\n{msg['role'].capitalize()}: {msg['content']}"
        
        prompt += "\n\nInsights (as JSON list):"
        
        # Get LLM service
        llm_service = llm_factory.get_service()
        
        # Generate insights
        insights_text = await llm_service.generate_text(
            prompt,
            system_message="You are an AI assistant tasked with extracting insights about users from conversations. Be thoughtful, nuanced, and evidence-based in your analysis.",
            temperature=0.3
        )
        
        # Parse insights from JSON
        try:
            # Find JSON in the response
            start_idx = insights_text.find("[")
            end_idx = insights_text.rfind("]") + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = insights_text[start_idx:end_idx]
                insights = json.loads(json_str)
            else:
                logger.error("Failed to extract JSON from insights response")
                return []
            
            # Store insights in database
            stored_insights = []
            for insight in insights:
                insight_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "type": insight.get("type", "unknown"),
                    "content": insight.get("content", ""),
                    "evidence": insight.get("evidence", ""),
                    "created_at": datetime.now().isoformat(),
                    "confidence": 0.8,  # Default confidence
                    "metadata": {}
                }
                
                result = await supabase_client.create_insight(insight_data)
                if result:
                    stored_insights.append(result)
            
            return stored_insights
        except Exception as e:
            logger.error(f"Error parsing insights: {str(e)}")
            return []

# Create a singleton instance
memory_service = MemoryService()