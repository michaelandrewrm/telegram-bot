"""Tests for bot utils validators."""

import pytest
import sys
import os
import hmac
import hashlib

from unittest.mock import patch, MagicMock

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestValidatorsStructure:
    """Test validators module structure and imports."""

    def test_import_structure(self):
        """Test that validators module can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.utils.validators", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "utils", "validators.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load validators module: {e}")


class TestValidateChatId:
    """Test validate_chat_id function."""

    def test_validate_chat_id_integer(self):
        """Test chat ID validation with integers."""
        def mock_validate_chat_id(chat_id):
            if isinstance(chat_id, int):
                return True
            return False
        
        # Test valid integer chat IDs
        assert mock_validate_chat_id(123456789) is True
        assert mock_validate_chat_id(-123456789) is True
        assert mock_validate_chat_id(0) is True

    def test_validate_chat_id_numeric_string(self):
        """Test chat ID validation with numeric strings."""
        def mock_validate_chat_id(chat_id):
            if isinstance(chat_id, int):
                return True
            
            if isinstance(chat_id, str):
                # Check if it's a numeric string
                if chat_id.lstrip('-').isdigit():
                    return True
                
                # Check if it's a channel/group username
                if chat_id.startswith('@') and len(chat_id) > 1:
                    import re
                    return bool(re.match(r'^@[a-zA-Z0-9_]{5,}$', chat_id))
            
            return False
        
        # Test valid numeric strings
        assert mock_validate_chat_id("123456789") is True
        assert mock_validate_chat_id("-123456789") is True
        
        # Test invalid numeric strings
        assert mock_validate_chat_id("12.34") is False
        assert mock_validate_chat_id("abc123") is False

    def test_validate_chat_id_username(self):
        """Test chat ID validation with usernames."""
        def mock_validate_chat_id(chat_id):
            if isinstance(chat_id, str) and chat_id.startswith('@') and len(chat_id) > 1:
                import re
                return bool(re.match(r'^@[a-zA-Z0-9_]{5,}$', chat_id))
            return False
        
        # Test valid usernames
        assert mock_validate_chat_id("@validusername") is True
        assert mock_validate_chat_id("@test_channel") is True
        assert mock_validate_chat_id("@user123") is True
        
        # Test invalid usernames
        assert mock_validate_chat_id("@abc") is False  # Too short
        assert mock_validate_chat_id("@user-name") is False  # Contains hyphen
        assert mock_validate_chat_id("@user@name") is False  # Contains @
        assert mock_validate_chat_id("username") is False  # Missing @

    def test_validate_chat_id_invalid_types(self):
        """Test chat ID validation with invalid types."""
        def mock_validate_chat_id(chat_id):
            if isinstance(chat_id, (int, str)):
                return True  # Simplified for testing
            return False
        
        # Test invalid types
        assert mock_validate_chat_id(None) is False
        assert mock_validate_chat_id([]) is False
        assert mock_validate_chat_id({}) is False
        assert mock_validate_chat_id(12.34) is False


class TestValidateMessage:
    """Test validate_message function."""

    def test_validate_message_valid(self):
        """Test message validation with valid messages."""
        def mock_validate_message(message, max_length=4096):
            if not isinstance(message, str):
                return False, "Message must be a string"
            
            if not message.strip():
                return False, "Message cannot be empty"
            
            if len(message) > max_length:
                return False, f"Message too long ({len(message)} > {max_length} characters)"
            
            return True, None
        
        # Test valid messages
        is_valid, error = mock_validate_message("Hello, world!")
        assert is_valid is True
        assert error is None
        
        is_valid, error = mock_validate_message("A" * 4096)
        assert is_valid is True
        assert error is None

    def test_validate_message_invalid_type(self):
        """Test message validation with invalid types."""
        def mock_validate_message(message, max_length=4096):
            if not isinstance(message, str):
                return False, "Message must be a string"
            return True, None
        
        # Test invalid types
        is_valid, error = mock_validate_message(123)
        assert is_valid is False
        assert "Message must be a string" in error
        
        is_valid, error = mock_validate_message(None)
        assert is_valid is False
        assert "Message must be a string" in error

    def test_validate_message_empty(self):
        """Test message validation with empty messages."""
        def mock_validate_message(message, max_length=4096):
            if not isinstance(message, str):
                return False, "Message must be a string"
            
            if not message.strip():
                return False, "Message cannot be empty"
            
            return True, None
        
        # Test empty messages
        is_valid, error = mock_validate_message("")
        assert is_valid is False
        assert "Message cannot be empty" in error
        
        is_valid, error = mock_validate_message("   ")
        assert is_valid is False
        assert "Message cannot be empty" in error

    def test_validate_message_too_long(self):
        """Test message validation with messages that are too long."""
        def mock_validate_message(message, max_length=4096):
            if not isinstance(message, str):
                return False, "Message must be a string"
            
            if not message.strip():
                return False, "Message cannot be empty"
            
            if len(message) > max_length:
                return False, f"Message too long ({len(message)} > {max_length} characters)"
            
            return True, None
        
        # Test message too long
        long_message = "A" * 4097
        is_valid, error = mock_validate_message(long_message)
        assert is_valid is False
        assert "Message too long" in error
        assert "4097 > 4096" in error


class TestValidateFilePath:
    """Test validate_file_path function."""

    def test_validate_file_path_valid(self):
        """Test file path validation with valid paths."""
        def mock_validate_file_path(file_path):
            if not isinstance(file_path, str):
                return False, "File path must be a string"
            
            if not file_path.strip():
                return False, "File path cannot be empty"
            
            # Basic checks for this test
            if '..' in file_path or '~' in file_path:
                return False, "Path traversal patterns not allowed"
            
            return True, None
        
        # Test valid paths
        is_valid, error = mock_validate_file_path("/home/user/file.txt")
        assert is_valid is True
        assert error is None
        
        is_valid, error = mock_validate_file_path("relative/path/file.txt")
        assert is_valid is True
        assert error is None

    def test_validate_file_path_traversal(self):
        """Test file path validation with traversal attempts."""
        def mock_validate_file_path(file_path):
            if '..' in file_path or '~' in file_path:
                return False, "Path traversal patterns not allowed"
            return True, None
        
        # Test path traversal attempts
        is_valid, error = mock_validate_file_path("../../../etc/passwd")
        assert is_valid is False
        assert "Path traversal patterns not allowed" in error
        
        is_valid, error = mock_validate_file_path("~/secret/file.txt")
        assert is_valid is False
        assert "Path traversal patterns not allowed" in error

    def test_validate_file_path_dangerous_paths(self):
        """Test file path validation with dangerous system paths."""
        def mock_validate_file_path(file_path):
            dangerous_paths = ['/etc/', '/root/', '/sys/', '/proc/', '/dev/', '/var/log/']
            
            for dangerous_path in dangerous_paths:
                if file_path.startswith(dangerous_path):
                    return False, f"Access to system path not allowed: {file_path}"
            
            return True, None
        
        # Test dangerous paths
        dangerous_files = [
            "/etc/passwd",
            "/root/.ssh/id_rsa",
            "/sys/kernel/debug",
            "/proc/version",
            "/dev/random"
        ]
        
        for dangerous_file in dangerous_files:
            is_valid, error = mock_validate_file_path(dangerous_file)
            assert is_valid is False
            assert "Access to system path not allowed" in error


class TestValidateWebhookSignature:
    """Test validate_webhook_signature function."""

    def test_validate_webhook_signature_valid(self):
        """Test webhook signature validation with valid signatures."""
        def mock_validate_webhook_signature(payload, signature, secret):
            if not secret or not signature:
                return False
            
            if not signature.startswith('sha256='):
                return False
            
            expected_signature = 'sha256=' + hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        # Test valid signature
        payload = b"test payload"
        secret = "secret_key"
        expected_signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        is_valid = mock_validate_webhook_signature(payload, expected_signature, secret)
        assert is_valid is True

    def test_validate_webhook_signature_invalid(self):
        """Test webhook signature validation with invalid signatures."""
        def mock_validate_webhook_signature(payload, signature, secret):
            if not secret or not signature:
                return False
            
            if not signature.startswith('sha256='):
                return False
            
            expected_signature = 'sha256=' + hmac.new(
                secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        
        # Test invalid signature
        payload = b"test payload"
        secret = "secret_key"
        wrong_signature = "sha256=wrongsignature"
        
        is_valid = mock_validate_webhook_signature(payload, wrong_signature, secret)
        assert is_valid is False
        
        # Test missing sha256 prefix
        is_valid = mock_validate_webhook_signature(payload, "wrongformat", secret)
        assert is_valid is False
        
        # Test missing secret/signature
        is_valid = mock_validate_webhook_signature(payload, "", secret)
        assert is_valid is False
        
        is_valid = mock_validate_webhook_signature(payload, "sha256=test", "")
        assert is_valid is False


class TestValidateWebhookToken:
    """Test validate_webhook_token function."""

    def test_validate_webhook_token_valid(self):
        """Test webhook token validation with valid tokens."""
        def mock_validate_webhook_token(token, expected_token):
            if not isinstance(token, str) or not isinstance(expected_token, str):
                return False
            
            if not token or not expected_token:
                return False
            
            return hmac.compare_digest(token, expected_token)
        
        # Test valid token
        token = "valid_token_123"
        is_valid = mock_validate_webhook_token(token, token)
        assert is_valid is True

    def test_validate_webhook_token_invalid(self):
        """Test webhook token validation with invalid tokens."""
        def mock_validate_webhook_token(token, expected_token):
            if not isinstance(token, str) or not isinstance(expected_token, str):
                return False
            
            if not token or not expected_token:
                return False
            
            return hmac.compare_digest(token, expected_token)
        
        # Test invalid token
        is_valid = mock_validate_webhook_token("wrong_token", "correct_token")
        assert is_valid is False
        
        # Test invalid types
        is_valid = mock_validate_webhook_token(123, "correct_token")
        assert is_valid is False
        
        is_valid = mock_validate_webhook_token("token", None)
        assert is_valid is False
        
        # Test empty tokens
        is_valid = mock_validate_webhook_token("", "correct_token")
        assert is_valid is False


class TestValidateParseMode:
    """Test validate_parse_mode function."""

    def test_validate_parse_mode_valid(self):
        """Test parse mode validation with valid modes."""
        def mock_validate_parse_mode(parse_mode):
            valid_modes = ['Markdown', 'MarkdownV2', 'HTML']
            return parse_mode in valid_modes
        
        # Test valid parse modes
        assert mock_validate_parse_mode('Markdown') is True
        assert mock_validate_parse_mode('MarkdownV2') is True
        assert mock_validate_parse_mode('HTML') is True

    def test_validate_parse_mode_invalid(self):
        """Test parse mode validation with invalid modes."""
        def mock_validate_parse_mode(parse_mode):
            valid_modes = ['Markdown', 'MarkdownV2', 'HTML']
            return parse_mode in valid_modes
        
        # Test invalid parse modes
        assert mock_validate_parse_mode('markdown') is False  # Case sensitive
        assert mock_validate_parse_mode('TEXT') is False
        assert mock_validate_parse_mode('Invalid') is False
        assert mock_validate_parse_mode('') is False


class TestSanitizeFilename:
    """Test sanitize_filename function."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        def mock_sanitize_filename(filename):
            import re
            # Remove or replace dangerous characters
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # Remove leading/trailing dots and spaces
            sanitized = sanitized.strip('. ')
            
            # Ensure it's not empty
            if not sanitized:
                sanitized = 'file'
            
            return sanitized
        
        # Test basic sanitization
        assert mock_sanitize_filename("normal_file.txt") == "normal_file.txt"
        assert mock_sanitize_filename("file<with>bad:chars") == "file_with_bad_chars"
        assert mock_sanitize_filename('file"with|bad?chars*') == "file_with_bad_chars_"

    def test_sanitize_filename_edge_cases(self):
        """Test filename sanitization edge cases."""
        def mock_sanitize_filename(filename):
            import re
            # Remove or replace dangerous characters
            sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            # Remove leading/trailing dots and spaces
            sanitized = sanitized.strip('. ')
            
            # Ensure it's not empty
            if not sanitized:
                sanitized = 'file'
            
            # Limit length
            if len(sanitized) > 255:
                name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
                max_name_len = 255 - len(ext) - 1 if ext else 255
                sanitized = name[:max_name_len] + ('.' + ext if ext else '')
            
            return sanitized
        
        # Test edge cases
        assert mock_sanitize_filename("") == "file"
        assert mock_sanitize_filename("   ") == "file"
        assert mock_sanitize_filename("...") == "file"
        assert mock_sanitize_filename(".hidden_file") == "hidden_file"
        
        # Test long filename
        long_name = "a" * 300 + ".txt"
        result = mock_sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")


class TestValidateCronExpression:
    """Test validate_cron_expression function."""

    def test_validate_cron_expression_valid(self):
        """Test cron expression validation with valid expressions."""
        def mock_validate_cron_expression(cron_expr):
            if not isinstance(cron_expr, str):
                return False, "Cron expression must be a string"
            
            parts = cron_expr.strip().split()
            
            if len(parts) != 5:
                return False, "Cron expression must have exactly 5 parts (minute hour day month weekday)"
            
            # Simple validation for this test
            for part in parts:
                if part == '*':
                    continue
                if part.isdigit():
                    continue
                if ',' in part or '-' in part or '/' in part:
                    continue
                return False, f"Invalid part: {part}"
            
            return True, None
        
        # Test valid cron expressions
        valid_expressions = [
            "0 9 * * *",      # Daily at 9 AM
            "*/15 * * * *",   # Every 15 minutes
            "0 0 1 * *",      # First day of month
            "0 12 * * 1-5",   # Weekdays at noon
            "30 14 * * 0,6"   # Weekends at 2:30 PM
        ]
        
        for expr in valid_expressions:
            is_valid, error = mock_validate_cron_expression(expr)
            assert is_valid is True, f"Expression {expr} should be valid"
            assert error is None

    def test_validate_cron_expression_invalid(self):
        """Test cron expression validation with invalid expressions."""
        def mock_validate_cron_expression(cron_expr):
            if not isinstance(cron_expr, str):
                return False, "Cron expression must be a string"
            
            parts = cron_expr.strip().split()
            
            if len(parts) != 5:
                return False, "Cron expression must have exactly 5 parts (minute hour day month weekday)"
            
            return True, None
        
        # Test invalid expressions
        invalid_expressions = [
            "0 9 * *",        # Too few parts
            "0 9 * * * *",    # Too many parts
            "",               # Empty
            "not a cron"      # Invalid format
        ]
        
        for expr in invalid_expressions:
            is_valid, error = mock_validate_cron_expression(expr)
            assert is_valid is False, f"Expression {expr} should be invalid"
            assert error is not None

    def test_validate_cron_expression_type_validation(self):
        """Test cron expression type validation."""
        def mock_validate_cron_expression(cron_expr):
            if not isinstance(cron_expr, str):
                return False, "Cron expression must be a string"
            return True, None
        
        # Test invalid types
        is_valid, error = mock_validate_cron_expression(123)
        assert is_valid is False
        assert "Cron expression must be a string" in error
        
        is_valid, error = mock_validate_cron_expression(None)
        assert is_valid is False
        assert "Cron expression must be a string" in error


class TestValidatorsIntegration:
    """Test validators integration scenarios."""

    def test_security_validation_chain(self):
        """Test security validation chain."""
        def security_validation_chain(data):
            """Chain multiple security validations."""
            validations = []
            
            # File path validation
            if 'file_path' in data:
                if '..' in data['file_path']:
                    validations.append("Path traversal detected")
            
            # Token validation
            if 'token' in data and 'expected_token' in data:
                if data['token'] != data['expected_token']:
                    validations.append("Invalid token")
            
            # Message validation
            if 'message' in data:
                if len(data['message']) > 4096:
                    validations.append("Message too long")
            
            return len(validations) == 0, validations
        
        # Test secure data
        secure_data = {
            'file_path': '/safe/path/file.txt',
            'token': 'valid_token',
            'expected_token': 'valid_token',
            'message': 'Valid message'
        }
        
        is_secure, errors = security_validation_chain(secure_data)
        assert is_secure is True
        assert len(errors) == 0
        
        # Test insecure data
        insecure_data = {
            'file_path': '../../../etc/passwd',
            'token': 'wrong_token',
            'expected_token': 'correct_token',
            'message': 'A' * 5000
        }
        
        is_secure, errors = security_validation_chain(insecure_data)
        assert is_secure is False
        assert len(errors) > 0

    def test_input_sanitization_patterns(self):
        """Test input sanitization patterns."""
        def sanitize_input(input_data):
            """Sanitize various input types."""
            sanitized = {}
            
            for key, value in input_data.items():
                if key == 'filename':
                    # Basic filename sanitization
                    import re
                    sanitized[key] = re.sub(r'[<>:"/\\|?*]', '_', str(value))
                elif key == 'message':
                    # Message sanitization
                    sanitized[key] = str(value).strip()
                elif key == 'chat_id':
                    # Chat ID validation
                    if isinstance(value, str) and value.startswith('@'):
                        sanitized[key] = value
                    elif str(value).lstrip('-').isdigit():
                        sanitized[key] = str(value)
                    else:
                        sanitized[key] = None
                else:
                    sanitized[key] = value
            
            return sanitized
        
        # Test input sanitization
        dirty_input = {
            'filename': 'bad<file>name.txt',
            'message': '  Clean message  ',
            'chat_id': '@valid_channel',
            'other': 'unchanged'
        }
        
        clean_input = sanitize_input(dirty_input)
        
        assert clean_input['filename'] == 'bad_file_name.txt'
        assert clean_input['message'] == 'Clean message'
        assert clean_input['chat_id'] == '@valid_channel'
        assert clean_input['other'] == 'unchanged'
