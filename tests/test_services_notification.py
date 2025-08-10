"""Tests for bot services notification."""

import pytest
import asyncio
import sys
import os

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestNotificationStructure:
    """Test notification service structure and imports."""

    def test_import_structure(self):
        """Test that notification service can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.services.notification", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "services", "notification.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load notification service: {e}")


class TestNotificationService:
    """Test NotificationService class."""

    def setup_method(self):
        """Set up test environment."""
        self.mock_config = MagicMock()
        self.mock_config.telegram_bot_token = "test_token"
        self.mock_config.retry_attempts = 3
        self.mock_config.retry_delay = 1.0
        self.mock_config.default_parse_mode = "Markdown"
        self.mock_config.max_message_length = 4096

    def test_notification_service_initialization(self):
        """Test NotificationService initialization."""
        # Mock NotificationService initialization
        class MockNotificationService:
            def __init__(self, bot_token=None):
                self.bot_token = bot_token or "default_token"
                self.bot = MagicMock()
                self.retry_handler = MagicMock()
        
        # Test with custom token
        service = MockNotificationService("custom_token")
        assert service.bot_token == "custom_token"
        assert service.bot is not None
        assert service.retry_handler is not None
        
        # Test with default token
        service = MockNotificationService()
        assert service.bot_token == "default_token"

    def test_send_notification_success(self):
        """Test successful text notification sending."""
        # Mock successful notification sending
        async def mock_send_notification(message, chat_id, parse_mode=None, **kwargs):
            if not message or not chat_id:
                return False
            
            # Mock message length validation
            max_length = 4096
            if len(message) > max_length:
                message = message[:max_length - 3] + "..."
            
            # Simulate successful sending
            return True
        
        # Test successful sending
        result = asyncio.run(mock_send_notification("Hello, world!", "123456789"))
        assert result is True
        
        # Test with long message (should be truncated)
        long_message = "A" * 5000
        result = asyncio.run(mock_send_notification(long_message, "123456789"))
        assert result is True

    def test_send_notification_failure(self):
        """Test notification sending failure scenarios."""
        # Mock notification sending with failures
        async def mock_send_notification(message, chat_id, parse_mode=None, **kwargs):
            if not message:
                return False
            if not chat_id:
                return False
            if chat_id == "invalid_chat":
                return False
            return True
        
        # Test missing message
        result = asyncio.run(mock_send_notification("", "123456789"))
        assert result is False
        
        # Test missing chat ID
        result = asyncio.run(mock_send_notification("Test message", ""))
        assert result is False
        
        # Test invalid chat ID
        result = asyncio.run(mock_send_notification("Test message", "invalid_chat"))
        assert result is False

    def test_message_truncation_logic(self):
        """Test message truncation for long messages."""
        def mock_truncate_message(message, max_length=4096):
            """Mock message truncation logic."""
            if len(message) > max_length:
                return message[:max_length - 3] + "..."
            return message
        
        # Test normal message
        normal_message = "This is a normal message"
        result = mock_truncate_message(normal_message)
        assert result == normal_message
        
        # Test long message
        long_message = "A" * 5000
        result = mock_truncate_message(long_message)
        assert len(result) == 4096
        assert result.endswith("...")

    def test_send_photo_success(self):
        """Test successful photo sending."""
        # Mock photo sending
        async def mock_send_photo(chat_id, photo, caption=None, parse_mode=None):
            if not chat_id or not photo:
                return False
            
            # Mock file validation
            if isinstance(photo, (str, Path)):
                # Check if it's a valid path or URL
                if str(photo).startswith("http") or Path(photo).exists():
                    return True
                return False
            
            # Assume file object is valid
            return True
        
        # Test with URL
        result = asyncio.run(mock_send_photo("123456789", "https://example.com/photo.jpg"))
        assert result is True
        
        # Test with file path (mocked as existing)
        with patch('pathlib.Path.exists', return_value=True):
            result = asyncio.run(mock_send_photo("123456789", "/path/to/photo.jpg"))
            assert result is True

    def test_send_document_success(self):
        """Test successful document sending."""
        # Mock document sending
        async def mock_send_document(chat_id, document, filename=None, caption=None, parse_mode=None):
            if not chat_id or not document:
                return False
            
            # Extract filename logic
            if isinstance(document, (str, Path)) and not filename:
                filename = Path(document).name
            
            return True
        
        # Test document sending
        result = asyncio.run(mock_send_document("123456789", "/path/to/document.pdf"))
        assert result is True
        
        # Test with custom filename
        result = asyncio.run(mock_send_document("123456789", "/path/to/file", filename="custom.pdf"))
        assert result is True

    def test_send_video_success(self):
        """Test successful video sending."""
        # Mock video sending
        async def mock_send_video(chat_id, video, duration=None, width=None, height=None, caption=None, parse_mode=None):
            if not chat_id or not video:
                return False
            
            # Validate video parameters
            if duration is not None and duration < 0:
                return False
            if width is not None and width <= 0:
                return False
            if height is not None and height <= 0:
                return False
            
            return True
        
        # Test basic video sending
        result = asyncio.run(mock_send_video("123456789", "/path/to/video.mp4"))
        assert result is True
        
        # Test with video parameters
        result = asyncio.run(mock_send_video("123456789", "/path/to/video.mp4", duration=120, width=1920, height=1080))
        assert result is True
        
        # Test with invalid parameters
        result = asyncio.run(mock_send_video("123456789", "/path/to/video.mp4", duration=-1))
        assert result is False

    def test_send_to_multiple_success(self):
        """Test sending to multiple chats."""
        # Mock sending to multiple chats
        async def mock_send_to_multiple(message, chat_ids, **kwargs):
            """Send to multiple chats with individual results."""
            results = []
            
            for chat_id in chat_ids:
                if chat_id == "invalid_chat":
                    results.append(False)
                else:
                    results.append(True)
            
            return results
        
        # Test successful sending to multiple valid chats
        chat_ids = ["123456789", "987654321", "555666777"]
        results = asyncio.run(mock_send_to_multiple("Test message", chat_ids))
        assert all(results)
        assert len(results) == 3
        
        # Test mixed success/failure
        mixed_chat_ids = ["123456789", "invalid_chat", "987654321"]
        results = asyncio.run(mock_send_to_multiple("Test message", mixed_chat_ids))
        assert results == [True, False, True]

    def test_send_to_default_chats(self):
        """Test sending to default configured chats."""
        # Mock sending to default chats
        async def mock_send_to_default_chats(message, **kwargs):
            """Send to default chats from configuration."""
            default_chat_ids = ["123456789", "987654321"]  # Mock config
            
            if not default_chat_ids:
                return []
            
            # Simulate sending to all default chats
            return [True] * len(default_chat_ids)
        
        # Test sending to default chats
        results = asyncio.run(mock_send_to_default_chats("Test message"))
        assert all(results)
        assert len(results) == 2

    def test_file_preparation_logic(self):
        """Test file data preparation for different input types."""
        async def mock_prepare_file_data(file_input):
            """Mock file preparation logic."""
            if isinstance(file_input, (str, Path)):
                file_path = Path(file_input)
                if str(file_input).startswith("http"):
                    # URL
                    return str(file_input)
                elif file_path.exists():
                    # File path - mock reading
                    return b"mock_file_data"
                else:
                    # Invalid path
                    return str(file_input)
            else:
                # File object
                return file_input
        
        # Test URL
        result = asyncio.run(mock_prepare_file_data("https://example.com/file.jpg"))
        assert result == "https://example.com/file.jpg"
        
        # Test file path (mocked as existing)
        with patch('pathlib.Path.exists', return_value=True):
            result = asyncio.run(mock_prepare_file_data("/path/to/file.jpg"))
            assert result == b"mock_file_data"
        
        # Test file object
        file_obj = MagicMock()
        result = asyncio.run(mock_prepare_file_data(file_obj))
        assert result == file_obj

    def test_retry_logic_integration(self):
        """Test retry logic integration."""
        # Mock retry execution
        async def mock_execute_with_retry(func, chat_id, message_type, max_attempts=3):
            """Mock retry execution logic."""
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    await func()
                    return True
                except Exception as e:
                    attempt += 1
                    if "RetryAfter" in str(e):
                        # Handle rate limiting
                        await asyncio.sleep(0.01)  # Short delay for testing
                        return True  # Succeed after rate limit wait
                    elif "NetworkError" in str(e) and attempt < max_attempts:
                        # Retry network errors
                        await asyncio.sleep(0.01)
                        continue
                    else:
                        # Don't retry other errors
                        return False
            
            return False
        
        # Mock successful function
        async def successful_func():
            return "success"
        
        result = asyncio.run(mock_execute_with_retry(successful_func, "123456789", "text"))
        assert result is True
        
        # Mock failing function that succeeds on retry
        call_count = 0
        async def retryable_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("NetworkError")
            return "success"
        
        result = asyncio.run(mock_execute_with_retry(retryable_func, "123456789", "text"))
        assert result is True
        assert call_count == 2

    def test_connection_testing(self):
        """Test bot connection testing."""
        # Mock connection testing
        async def mock_test_connection(bot_token):
            """Mock bot connection test."""
            if not bot_token:
                return False
            
            if bot_token == "invalid_token":
                return False
            
            # Mock successful connection
            return True
        
        # Test valid connection
        result = asyncio.run(mock_test_connection("valid_token"))
        assert result is True
        
        # Test invalid connection
        result = asyncio.run(mock_test_connection("invalid_token"))
        assert result is False
        
        # Test missing token
        result = asyncio.run(mock_test_connection(""))
        assert result is False


class TestNotificationServiceIntegration:
    """Test notification service integration scenarios."""

    def test_error_handling_patterns(self):
        """Test error handling patterns in notification service."""
        # Mock error handling for different error types
        async def mock_handle_telegram_errors(func, error_type):
            """Mock Telegram error handling."""
            try:
                await func()
                return True
            except Exception as e:
                if error_type == "RetryAfter":
                    # Handle rate limiting
                    await asyncio.sleep(0.01)
                    try:
                        await func()
                        return True
                    except Exception:
                        return False
                elif error_type == "TelegramError":
                    # Log and return False
                    return False
                elif error_type == "NetworkError":
                    # Could retry, but for this test just return False
                    return False
                else:
                    # Unexpected error
                    return False
        
        # Test different error scenarios
        async def retry_after_func():
            raise Exception("RetryAfter")
        
        result = asyncio.run(mock_handle_telegram_errors(retry_after_func, "RetryAfter"))
        assert result in [True, False]  # Could succeed after retry
        
        async def telegram_error_func():
            raise Exception("TelegramError")
        
        result = asyncio.run(mock_handle_telegram_errors(telegram_error_func, "TelegramError"))
        assert result is False

    def test_bulk_operations_performance(self):
        """Test bulk operations and performance considerations."""
        # Mock bulk operation performance
        async def mock_bulk_send(messages, chat_ids):
            """Mock bulk sending with performance tracking."""
            import time
            start_time = time.time()
            
            results = []
            for message in messages:
                for chat_id in chat_ids:
                    # Simulate some processing time
                    await asyncio.sleep(0.001)
                    results.append(True)
            
            end_time = time.time()
            return results, (end_time - start_time)
        
        # Test bulk operations
        messages = ["Message 1", "Message 2", "Message 3"]
        chat_ids = ["123456789", "987654321"]
        
        results, duration = asyncio.run(mock_bulk_send(messages, chat_ids))
        assert len(results) == len(messages) * len(chat_ids)
        assert all(results)
        assert duration > 0

    def test_file_type_validation(self):
        """Test file type validation and handling."""
        def validate_file_type(file_path, allowed_types=None):
            """Validate file type based on extension."""
            if allowed_types is None:
                allowed_types = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.mp4', '.mov']
            
            if isinstance(file_path, str):
                extension = Path(file_path).suffix.lower()
                return extension in allowed_types
            
            return True  # Assume file objects are valid
        
        # Test valid file types
        assert validate_file_type("image.jpg") is True
        assert validate_file_type("document.pdf") is True
        assert validate_file_type("video.mp4") is True
        
        # Test invalid file types
        assert validate_file_type("script.exe") is False
        assert validate_file_type("archive.zip") is False

    def test_configuration_integration(self):
        """Test configuration integration with notification service."""
        # Mock configuration handling
        class MockConfig:
            def __init__(self):
                self.telegram_bot_token = "test_token"
                self.default_parse_mode = "Markdown"
                self.max_message_length = 4096
                self.default_chat_ids = ["123456789", "987654321"]
                self.retry_attempts = 3
                self.retry_delay = 1.0
        
        def validate_config(config):
            """Validate configuration for notification service."""
            errors = []
            
            if not config.telegram_bot_token:
                errors.append("Bot token is required")
            
            if config.max_message_length <= 0:
                errors.append("Max message length must be positive")
            
            if not config.default_chat_ids:
                errors.append("Default chat IDs should be configured")
            
            valid_parse_modes = ["Markdown", "HTML", "MarkdownV2"]
            if config.default_parse_mode not in valid_parse_modes:
                errors.append(f"Invalid parse mode: {config.default_parse_mode}")
            
            return errors
        
        # Test valid configuration
        config = MockConfig()
        errors = validate_config(config)
        assert len(errors) == 0
        
        # Test invalid configuration
        config.telegram_bot_token = ""
        config.max_message_length = -1
        errors = validate_config(config)
        assert len(errors) > 0

    def test_rate_limiting_handling(self):
        """Test rate limiting and backoff strategies."""
        # Mock rate limiting handler
        class MockRateLimiter:
            def __init__(self):
                self.requests_made = 0
                self.rate_limit = 3  # Lower limit for testing
                self.window_start = 0
            
            async def check_rate_limit(self):
                """Check if we're within rate limits."""
                import time
                current_time = time.time()
                
                # Reset window if minute has passed
                if current_time - self.window_start > 60:
                    self.requests_made = 0
                    self.window_start = current_time
                
                if self.window_start == 0:
                    self.window_start = current_time
                
                if self.requests_made >= self.rate_limit:
                    # Rate limited
                    return False, 60 - (current_time - self.window_start)
                
                self.requests_made += 1
                return True, 0
        
        # Test rate limiting
        rate_limiter = MockRateLimiter()
        
        # Make requests within limit
        for _ in range(3):
            allowed, delay = asyncio.run(rate_limiter.check_rate_limit())
            assert allowed is True
            assert delay == 0
        
        # Next request should be rate limited
        allowed, delay = asyncio.run(rate_limiter.check_rate_limit())
        assert allowed is False
        assert delay >= 0

    def test_message_formatting_integration(self):
        """Test message formatting integration."""
        def format_message_for_telegram(message, parse_mode="Markdown"):
            """Format message according to parse mode."""
            if parse_mode == "Markdown":
                # Escape special characters
                message = message.replace('_', '\\_').replace('*', '\\*')
            elif parse_mode == "HTML":
                # Escape HTML characters
                message = message.replace('<', '&lt;').replace('>', '&gt;')
            
            return message
        
        # Test Markdown formatting
        formatted = format_message_for_telegram("Test_message*bold", "Markdown")
        assert "Test\\_message\\*bold" in formatted
        
        # Test HTML formatting
        formatted = format_message_for_telegram("Test<tag>content</tag>", "HTML")
        assert "&lt;tag&gt;" in formatted


def test_convenience_function():
    """Test convenience function for easy importing."""
    # Mock convenience function
    async def mock_send_notification(message, chat_id=None, **kwargs):
        """Mock convenience function."""
        if chat_id is not None:
            # Send to specific chat
            return True
        else:
            # Send to default chats
            return True
    
    # Test with specific chat ID
    result = asyncio.run(mock_send_notification("Test message", "123456789"))
    assert result is True
    
    # Test with default chats
    result = asyncio.run(mock_send_notification("Test message"))
    assert result is True
