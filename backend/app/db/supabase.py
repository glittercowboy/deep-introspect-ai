"""
Supabase client for database operations.
"""
import logging
from typing import Dict, List, Optional, Any, Union
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Client for interacting with Supabase.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the client exists."""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the Supabase client."""
        self.client: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        logger.info("Supabase client initialized")
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            User data or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.
        
        Args:
            email: The user email
            
        Returns:
            User data or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user.
        
        Args:
            user_data: User data to insert
            
        Returns:
            Created user data or None if failed
        """
        try:
            response = self.client.table("users").insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None
    
    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user data.
        
        Args:
            user_id: The user ID
            user_data: User data to update
            
        Returns:
            Updated user data or None if failed
        """
        try:
            response = self.client.table("users").update(user_data).eq("id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("users").delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return False
    
    async def get_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of conversation data
        """
        try:
            response = self.client.table("conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {str(e)}")
            return []
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            Conversation data or None if not found
        """
        try:
            response = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {str(e)}")
            return None
    
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new conversation.
        
        Args:
            conversation_data: Conversation data to insert
            
        Returns:
            Created conversation data or None if failed
        """
        try:
            response = self.client.table("conversations").insert(conversation_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return None
    
    async def update_conversation(self, conversation_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a conversation.
        
        Args:
            conversation_id: The conversation ID
            data: Data to update
            
        Returns:
            Updated conversation data or None if failed
        """
        try:
            response = self.client.table("conversations").update(data).eq("id", conversation_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error updating conversation {conversation_id}: {str(e)}")
            return None
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            True if successful
        """
        try:
            # Delete all messages first
            await self.delete_messages(conversation_id)
            
            # Delete conversation
            response = self.client.table("conversations").delete().eq("id", conversation_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            return False
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            List of message data
        """
        try:
            response = self.client.table("messages").select("*").eq("conversation_id", conversation_id).order("created_at", asc=True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting messages for conversation {conversation_id}: {str(e)}")
            return []
    
    async def create_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new message.
        
        Args:
            message_data: Message data to insert
            
        Returns:
            Created message data or None if failed
        """
        try:
            response = self.client.table("messages").insert(message_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return None
    
    async def delete_messages(self, conversation_id: str) -> bool:
        """
        Delete all messages for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            True if successful
        """
        try:
            response = self.client.table("messages").delete().eq("conversation_id", conversation_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting messages for conversation {conversation_id}: {str(e)}")
            return False
    
    async def get_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all insights for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of insight data
        """
        try:
            response = self.client.table("insights").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting insights for user {user_id}: {str(e)}")
            return []
    
    async def get_insights_by_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all insights for a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            List of insight data
        """
        try:
            response = self.client.table("insights").select("*").eq("conversation_id", conversation_id).order("created_at", desc=True).execute()
            
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting insights for conversation {conversation_id}: {str(e)}")
            return []
    
    async def create_insight(self, insight_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new insight.
        
        Args:
            insight_data: Insight data to insert
            
        Returns:
            Created insight data or None if failed
        """
        try:
            response = self.client.table("insights").insert(insight_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating insight: {str(e)}")
            return None

# Create a singleton instance
supabase_client = SupabaseClient()