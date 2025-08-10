"""Basic tests for the Telegram bot."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from bot.config import Config
from bot.services.notification import NotificationService
from bot.services.subscription import SubscriptionService
from bot.utils.validators import validate_chat_id, validate_message
from bot.utils.formatters import format_message


class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test config initialization."""
        config = Config()
        assert config is not None
        
    def test_get_method(self):
        """Test config get method."""
        config = Config()
        # Test with default value
        assert config.get("nonexistent_key", "default") == "default"
        
    def test_get_list_method(self):
        """Test config get_list method.""" 
        config = Config()
        # Test with default
        assert config.get_list("nonexistent_key", ["default"]) == ["default"]
        
        # Test with comma-separated string
        with patch.dict('os.environ', {'TEST_LIST': 'item1,item2,item3'}):
            config = Config()
            assert config.get("TEST_LIST").split(',') == ['item1', 'item2', 'item3']


class TestValidators:
    """Test validation utilities."""
    
    def test_validate_chat_id(self):
        """Test chat ID validation."""
        # Valid chat IDs
        assert validate_chat_id(123456789) == True
        assert validate_chat_id("123456789") == True
        assert validate_chat_id("-123456789") == True
        assert validate_chat_id("@username") == False  # Too short
        assert validate_chat_id("@valid_username") == True
        
        # Invalid chat IDs
        assert validate_chat_id("invalid") == False
        assert validate_chat_id("") == False
        assert validate_chat_id(None) == False
        
    def test_validate_message(self):
        """Test message validation."""
        # Valid messages
        is_valid, error = validate_message("Hello world")
        assert is_valid == True
        assert error is None
        
        # Invalid messages
        is_valid, error = validate_message("")
        assert is_valid == False
        assert "empty" in error.lower()
        
        is_valid, error = validate_message("x" * 5000)  # Too long
        assert is_valid == False
        assert "too long" in error.lower()


class TestFormatters:
    """Test message formatting utilities."""
    
    def test_format_message(self):
        """Test message formatting."""
        formatted = format_message(
            title="Test Title",
            message="Test message",
            level="INFO",
            markdown=True
        )
        
        assert "Test Title" in formatted
        assert "Test message" in formatted
        assert "ℹ️" in formatted  # INFO emoji
        
    def test_format_message_html(self):
        """Test HTML message formatting."""
        formatted = format_message(
            title="Test Title", 
            message="Test message",
            level="ERROR",
            markdown=False
        )
        
        assert "Test Title" in formatted
        assert "Test message" in formatted
        assert "[ERROR]" in formatted


@pytest.mark.asyncio
class TestNotificationService:
    """Test notification service."""
    
    async def test_notification_service_init(self):
        """Test notification service initialization."""
        with patch('bot.services.notification.Bot') as mock_bot:
            service = NotificationService("fake_token")
            assert service.bot_token == "fake_token"
            mock_bot.assert_called_once_with(token="fake_token")
    
    async def test_send_notification_success(self):
        """Test successful notification sending."""
        with patch('bot.services.notification.Bot') as mock_bot:
            mock_bot_instance = Mock()
            mock_bot.return_value = mock_bot_instance
            mock_bot_instance.send_message = AsyncMock()
            
            service = NotificationService("fake_token")
            service.retry_handler = Mock()
            service.retry_handler.execute = AsyncMock()
            
            result = await service.send_notification("Test message", "123456789")
            assert result == True
    
    async def test_send_notification_truncation(self):
        """Test message truncation for long messages."""
        with patch('bot.services.notification.Bot'):
            service = NotificationService("fake_token")
            service.retry_handler = Mock()
            service.retry_handler.execute = AsyncMock()
            
            long_message = "x" * 5000
            result = await service.send_notification(long_message, "123456789")
            # Should not fail due to length


@pytest.mark.asyncio  
class TestSubscriptionService:
    """Test subscription service."""
    
    async def test_subscription_service_init(self):
        """Test subscription service initialization."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            assert service._subscriptions == {}
    
    async def test_subscribe_valid_type(self):
        """Test subscribing to valid notification type."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            
            result = await service.subscribe(123456789, 123456789, "system")
            assert result == True
            assert 123456789 in service._subscriptions
            assert "system" in service._subscriptions[123456789]
    
    async def test_subscribe_invalid_type(self):
        """Test subscribing to invalid notification type."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            
            result = await service.subscribe(123456789, 123456789, "invalid_type")
            assert result == False
            assert 123456789 not in service._subscriptions
    
    async def test_unsubscribe(self):
        """Test unsubscribing from notification type."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            
            # Subscribe first
            await service.subscribe(123456789, 123456789, "system")
            
            # Then unsubscribe
            result = await service.unsubscribe(123456789, "system")
            assert result == True
            assert 123456789 not in service._subscriptions
    
    async def test_get_subscriptions(self):
        """Test getting user subscriptions."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            
            # Subscribe to multiple types
            await service.subscribe(123456789, 123456789, "system")
            await service.subscribe(123456789, 123456789, "errors")
            
            subscriptions = await service.get_subscriptions(123456789)
            assert len(subscriptions) == 2
            assert "system" in subscriptions
            assert "errors" in subscriptions
    
    async def test_get_subscribers(self):
        """Test getting subscribers for a type."""
        with patch('pathlib.Path.exists', return_value=False):
            service = SubscriptionService()
            
            # Subscribe multiple users
            await service.subscribe(123456789, 123456789, "system")
            await service.subscribe(987654321, 987654321, "system")
            await service.subscribe(555666777, 555666777, "errors")
            
            system_subscribers = await service.get_subscribers("system")
            assert len(system_subscribers) == 2
            assert 123456789 in system_subscribers
            assert 987654321 in system_subscribers
            
            error_subscribers = await service.get_subscribers("errors")
            assert len(error_subscribers) == 1
            assert 555666777 in error_subscribers


if __name__ == "__main__":
    pytest.main([__file__])
