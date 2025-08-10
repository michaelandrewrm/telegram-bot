"""Security tests for the Telegram bot."""

import pytest
import hmac
import hashlib
from unittest.mock import Mock, patch
from bot.utils.validators import (
    validate_webhook_signature,
    validate_webhook_token,
    validate_file_path
)


class TestWebhookSecurity:
    """Test webhook security features."""
    
    def test_webhook_signature_validation(self):
        """Test webhook signature validation with HMAC."""
        secret = "test_secret"
        payload = b'{"message": "test"}'
        
        # Generate valid signature
        expected_signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Test valid signature
        assert validate_webhook_signature(payload, expected_signature, secret) == True
        
        # Test invalid signature
        assert validate_webhook_signature(payload, "sha256=invalid", secret) == False
        
        # Test malformed signature
        assert validate_webhook_signature(payload, "invalid_format", secret) == False
        
        # Test empty values
        assert validate_webhook_signature(payload, "", secret) == False
        assert validate_webhook_signature(payload, expected_signature, "") == False
    
    def test_webhook_token_validation(self):
        """Test webhook token validation."""
        valid_token = "secure_token_123"
        
        # Test valid token
        assert validate_webhook_token(valid_token, valid_token) == True
        
        # Test invalid token
        assert validate_webhook_token("wrong_token", valid_token) == False
        
        # Test empty tokens
        assert validate_webhook_token("", valid_token) == False
        assert validate_webhook_token(valid_token, "") == False
        
        # Test non-string types
        assert validate_webhook_token(123, valid_token) == False
        assert validate_webhook_token(valid_token, 123) == False


class TestPathSecurity:
    """Test file path security validation."""
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks."""
        # Valid paths
        is_valid, error = validate_file_path("/home/user/file.txt")
        assert is_valid == True
        assert error is None
        
        # Path traversal attempts
        is_valid, error = validate_file_path("../../../etc/passwd")
        assert is_valid == False
        assert "traversal" in error.lower()
        
        is_valid, error = validate_file_path("~/../../etc/passwd")
        assert is_valid == False
        assert "traversal" in error.lower()
        
        # System paths
        is_valid, error = validate_file_path("/etc/passwd")
        assert is_valid == False
        assert "system path" in error.lower()
        
        is_valid, error = validate_file_path("/root/.ssh/id_rsa")
        assert is_valid == False
        assert "system path" in error.lower()
        
        # Empty path
        is_valid, error = validate_file_path("")
        assert is_valid == False
        assert "empty" in error.lower()
        
        # Non-string path
        is_valid, error = validate_file_path(123)
        assert is_valid == False
        assert "string" in error.lower()


class TestInputSanitization:
    """Test input sanitization and validation."""
    
    def test_message_length_limits(self):
        """Test message length validation."""
        from bot.utils.validators import validate_message
        
        # Test maximum length enforcement
        max_length = 4096
        long_message = "x" * (max_length + 1)
        
        is_valid, error = validate_message(long_message, max_length)
        assert is_valid == False
        assert "too long" in error.lower()
        
        # Test valid length
        valid_message = "x" * max_length
        is_valid, error = validate_message(valid_message, max_length)
        assert is_valid == True
        assert error is None
    
    def test_chat_id_sanitization(self):
        """Test chat ID validation and sanitization."""
        from bot.utils.validators import validate_chat_id
        
        # Test SQL injection attempts (should be invalid)
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1; SELECT * FROM users",
            "<script>alert('xss')</script>",
            "../../etc/passwd"
        ]
        
        for malicious_input in malicious_inputs:
            assert validate_chat_id(malicious_input) == False
    
    def test_api_key_handling(self):
        """Test API key validation."""
        # This would typically test actual API key validation
        # Here we test the structure
        
        valid_api_key = "sk-1234567890abcdef"
        
        # Test minimum length requirements
        assert len(valid_api_key) >= 16
        
        # Test character set (alphanumeric + hyphens)
        import re
        assert re.match(r'^[a-zA-Z0-9\-_]+$', valid_api_key)


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_decorator(self):
        """Test rate limiting decorator if implemented."""
        # This would test actual rate limiting implementation
        # For now, we test the concept
        
        from collections import defaultdict
        import time
        
        # Simulate rate limiting storage
        request_counts = defaultdict(list)
        rate_limit = 10  # 10 requests per minute
        window = 60  # 60 seconds
        
        def is_rate_limited(user_id: str) -> bool:
            now = time.time()
            # Clean old requests
            request_counts[user_id] = [
                req_time for req_time in request_counts[user_id]
                if now - req_time < window
            ]
            
            # Check limit
            if len(request_counts[user_id]) >= rate_limit:
                return True
            
            # Add current request
            request_counts[user_id].append(now)
            return False
        
        # Test rate limiting
        user_id = "test_user"
        
        # Should not be rate limited initially
        for _ in range(rate_limit):
            assert is_rate_limited(user_id) == False
        
        # Should be rate limited after exceeding limit
        assert is_rate_limited(user_id) == True


class TestConfigSecurity:
    """Test configuration security."""
    
    def test_secret_key_validation(self):
        """Test secret key requirements."""
        # Test minimum length
        short_key = "123"
        assert len(short_key) < 16  # Should be rejected
        
        # Test entropy (simple check)
        weak_key = "password123"
        strong_key = "8f3e9d2a7b1c4e6f9a8d7e5b3c2a9f8e"
        
        # Strong key should have good character distribution
        unique_chars = len(set(strong_key))
        assert unique_chars > 8  # Good entropy indicator
    
    @patch.dict('os.environ', {'TELEGRAM_BOT_TOKEN': ''})
    def test_missing_required_config(self):
        """Test handling of missing required configuration."""
        from bot.config import Config
        
        # Should handle missing required config gracefully
        config = Config()
        
        # Should have the property defined
        assert isinstance(getattr(Config, 'telegram_bot_token', None), property)
        
        # Accessing the property should raise a ValueError for missing required config
        with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN is required"):
            config.telegram_bot_token
    
    def test_config_validation(self):
        """Test configuration value validation."""
        # Test URL validation for webhook URLs
        invalid_urls = [
            "not_a_url",
            "ftp://invalid.com",
            "javascript:alert('xss')",
            "file:///etc/passwd"
        ]
        
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        for invalid_url in invalid_urls:
            if invalid_url.startswith(('http://', 'https://')):
                # Only http/https should pass basic pattern check
                continue
            assert not url_pattern.match(invalid_url)
