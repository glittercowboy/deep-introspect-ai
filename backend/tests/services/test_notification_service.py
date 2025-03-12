"""
Tests for the notification service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.notifications.notification_service import NotificationService

@pytest.mark.unit
class TestNotificationService:
    """Tests for the NotificationService class."""
    
    def setup_method(self):
        """Setup for tests."""
        # Create a fresh instance for each test
        self.notification_service = NotificationService()
        
        # Reset the singleton instance to ensure isolation
        NotificationService._instance = None
    
    @pytest.mark.asyncio
    async def test_create_notification(self, mock_supabase):
        """Test creating a notification."""
        # Arrange
        user_id = "test-user-id"
        notification_type = "insight"
        title = "Test Notification"
        content = "This is a test notification."
        metadata = {"key": "value"}
        
        # Mock the create_notification method to return a successful result
        mock_supabase.create_notification.return_value = {
            "id": "test-notification-id",
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "content": content,
            "metadata": metadata,
            "read": False,
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        # Act
        result = await self.notification_service.create_notification(
            user_id, notification_type, title, content, metadata
        )
        
        # Assert
        assert result is not None
        assert result["user_id"] == user_id
        assert result["type"] == notification_type
        assert result["title"] == title
        assert result["content"] == content
        assert result["metadata"] == metadata
        assert result["read"] is False
        
        # Verify the Supabase client was called with expected arguments
        mock_supabase.create_notification.assert_called_once()
        call_args = mock_supabase.create_notification.call_args[0][0]
        assert call_args["user_id"] == user_id
        assert call_args["type"] == notification_type
        assert call_args["title"] == title
        assert call_args["content"] == content
        assert call_args["metadata"] == metadata
    
    @pytest.mark.asyncio
    async def test_create_notification_error(self, mock_supabase):
        """Test error handling when creating a notification."""
        # Arrange
        user_id = "test-user-id"
        notification_type = "insight"
        title = "Test Notification"
        content = "This is a test notification."
        
        # Mock create_notification to raise an exception
        mock_supabase.create_notification.side_effect = Exception("Database error")
        
        # Act
        result = await self.notification_service.create_notification(
            user_id, notification_type, title, content
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_mark_as_read(self, mock_supabase):
        """Test marking a notification as read."""
        # Arrange
        notification_id = "test-notification-id"
        
        # Mock update_notification to return a successful result
        mock_supabase.update_notification.return_value = {
            "id": notification_id,
            "read": True
        }
        
        # Act
        result = await self.notification_service.mark_as_read(notification_id)
        
        # Assert
        assert result is True
        mock_supabase.update_notification.assert_called_once_with(
            notification_id, {"read": True}
        )
    
    @pytest.mark.asyncio
    async def test_mark_all_as_read(self, mock_supabase):
        """Test marking all notifications as read for a user."""
        # Arrange
        user_id = "test-user-id"
        
        # Mock mark_all_notifications_read to return True
        mock_supabase.mark_all_notifications_read.return_value = True
        
        # Act
        result = await self.notification_service.mark_all_as_read(user_id)
        
        # Assert
        assert result is True
        mock_supabase.mark_all_notifications_read.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_notifications(self, mock_supabase):
        """Test retrieving notifications for a user."""
        # Arrange
        user_id = "test-user-id"
        limit = 10
        offset = 0
        unread_only = False
        
        # Mock get_notifications to return test data
        mock_notifications = [
            {
                "id": "notif1",
                "user_id": user_id,
                "type": "insight",
                "title": "New Insight",
                "content": "A new insight was discovered",
                "read": False,
                "created_at": "2023-01-01T00:00:00Z"
            },
            {
                "id": "notif2",
                "user_id": user_id,
                "type": "message",
                "title": "New Message",
                "content": "You have a new message",
                "read": True,
                "created_at": "2023-01-02T00:00:00Z"
            }
        ]
        mock_supabase.get_notifications.return_value = mock_notifications
        
        # Act
        result = await self.notification_service.get_notifications(
            user_id, limit, offset, unread_only
        )
        
        # Assert
        assert result == mock_notifications
        mock_supabase.get_notifications.assert_called_once_with(
            user_id, limit, offset, unread_only
        )
    
    @pytest.mark.asyncio
    async def test_create_insight_notification(self, mock_supabase):
        """Test creating an insight notification."""
        # Arrange
        user_id = "test-user-id"
        insight_type = "belief"
        insight_content = "User values personal growth"
        insight_id = "insight-123"
        
        # Mock create_notification to return a successful result
        notification_result = {
            "id": "notif-123",
            "user_id": user_id,
            "type": "insight",
            "title": f"New {insight_type.capitalize()} Insight",
            "content": insight_content,
            "metadata": {
                "insight_id": insight_id,
                "insight_type": insight_type
            },
            "read": False,
            "created_at": "2023-01-01T00:00:00Z"
        }
        mock_supabase.create_notification.return_value = notification_result
        
        # Act
        result = await self.notification_service.create_insight_notification(
            user_id, insight_type, insight_content, insight_id
        )
        
        # Assert
        assert result == notification_result
        mock_supabase.create_notification.assert_called_once()
        call_args = mock_supabase.create_notification.call_args[0]
        assert call_args[0] == user_id
        assert call_args[1] == "insight"
        assert call_args[2] == "New Belief Insight"
        assert call_args[3] == insight_content
        assert call_args[4]["insight_id"] == insight_id
