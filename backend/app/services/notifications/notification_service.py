"""
Notification service for managing user notifications.
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from app.db.supabase import supabase_client

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for managing user notifications.
    """
    _instance = None

    def __new__(cls):
        """Singleton pattern to ensure only one instance of the service exists."""
        if cls._instance is None:
            cls._instance = super(NotificationService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the notification service."""
        logger.info("Notification service initialized")
    
    async def create_notification(
        self,
        user_id: str,
        type: str,
        title: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new notification.
        
        Args:
            user_id: User ID
            type: Notification type (insight, message, system)
            title: Notification title
            content: Notification content
            metadata: Optional metadata (URLs, IDs, etc.)
            
        Returns:
            Created notification data
        """
        try:
            notification_id = str(uuid.uuid4())
            
            notification_data = {
                "id": notification_id,
                "user_id": user_id,
                "type": type,
                "title": title,
                "content": content,
                "read": False,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            result = await supabase_client.create_notification(notification_data)
            
            logger.info(f"Created notification for user {user_id}: {title}")
            
            return result
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return None
    
    async def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful
        """
        try:
            result = await supabase_client.update_notification(
                notification_id,
                {"read": True}
            )
            
            return result is not None
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> bool:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            result = await supabase_client.mark_all_notifications_read(user_id)
            
            return result
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            return False
    
    async def get_notifications(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            unread_only: Whether to get only unread notifications
            
        Returns:
            List of notifications
        """
        try:
            result = await supabase_client.get_notifications(
                user_id,
                limit,
                offset,
                unread_only
            )
            
            return result
        except Exception as e:
            logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    async def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Count of unread notifications
        """
        try:
            result = await supabase_client.get_unread_notification_count(user_id)
            
            return result
        except Exception as e:
            logger.error(f"Error getting unread notification count: {str(e)}")
            return 0
    
    async def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if successful
        """
        try:
            result = await supabase_client.delete_notification(notification_id)
            
            return result
        except Exception as e:
            logger.error(f"Error deleting notification: {str(e)}")
            return False
    
    async def create_insight_notification(
        self,
        user_id: str,
        insight_type: str,
        insight_content: str,
        insight_id: str
    ) -> Dict[str, Any]:
        """
        Create a notification for a new insight.
        
        Args:
            user_id: User ID
            insight_type: Type of insight (belief, value, pattern, etc.)
            insight_content: Content of the insight
            insight_id: ID of the insight
            
        Returns:
            Created notification data
        """
        title = f"New {insight_type.capitalize()} Insight"
        content = insight_content[:100] + ("..." if len(insight_content) > 100 else "")
        metadata = {
            "insight_id": insight_id,
            "insight_type": insight_type
        }
        
        return await self.create_notification(
            user_id,
            "insight",
            title,
            content,
            metadata
        )
    
    async def create_message_notification(
        self,
        user_id: str,
        conversation_title: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Create a notification for a new message.
        
        Args:
            user_id: User ID
            conversation_title: Title of the conversation
            conversation_id: ID of the conversation
            
        Returns:
            Created notification data
        """
        title = "New Message"
        content = f"You have a new message in '{conversation_title}'"
        metadata = {
            "conversation_id": conversation_id
        }
        
        return await self.create_notification(
            user_id,
            "message",
            title,
            content,
            metadata
        )
    
    async def create_summary_notification(
        self,
        user_id: str,
        summary_type: str = "weekly"
    ) -> Dict[str, Any]:
        """
        Create a notification for a new summary.
        
        Args:
            user_id: User ID
            summary_type: Type of summary (weekly, monthly)
            
        Returns:
            Created notification data
        """
        title = f"{summary_type.capitalize()} Summary Ready"
        content = f"Your {summary_type} introspection summary is now available to view."
        metadata = {
            "url": "/insights?view=summary",
            "summary_type": summary_type
        }
        
        return await self.create_notification(
            user_id,
            "system",
            title,
            content,
            metadata
        )

# Create a singleton instance
notification_service = NotificationService()