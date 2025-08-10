"""Validation utilities for the Telegram bot."""

import re
from typing import Union, Optional


def validate_chat_id(chat_id: Union[str, int]) -> bool:
    """Validate Telegram chat ID.
    
    Args:
        chat_id: Chat ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if isinstance(chat_id, int):
        return True
    
    if isinstance(chat_id, str):
        # Check if it's a numeric string
        if chat_id.lstrip('-').isdigit():
            return True
        
        # Check if it's a channel/group username
        if chat_id.startswith('@') and len(chat_id) > 1:
            return bool(re.match(r'^@[a-zA-Z0-9_]{5,}$', chat_id))
    
    return False


def validate_message(message: str, max_length: int = 4096) -> tuple[bool, Optional[str]]:
    """Validate message content.
    
    Args:
        message: Message to validate
        max_length: Maximum message length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(message, str):
        return False, "Message must be a string"
    
    if not message.strip():
        return False, "Message cannot be empty"
    
    if len(message) > max_length:
        return False, f"Message too long ({len(message)} > {max_length} characters)"
    
    return True, None


def validate_file_path(file_path: str) -> tuple[bool, Optional[str]]:
    """Validate file path.
    
    Args:
        file_path: File path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(file_path, str):
        return False, "File path must be a string"
    
    if not file_path.strip():
        return False, "File path cannot be empty"
    
    # Check for potentially dangerous paths
    dangerous_patterns = ['../', '~/', '/etc/', '/root/', '/sys/', '/proc/']
    for pattern in dangerous_patterns:
        if pattern in file_path:
            return False, f"Potentially dangerous file path: {file_path}"
    
    return True, None


def validate_webhook_token(token: str, expected_token: str) -> bool:
    """Validate webhook token.
    
    Args:
        token: Token to validate
        expected_token: Expected token value
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(token, str) or not isinstance(expected_token, str):
        return False
    
    if not token or not expected_token:
        return False
    
    # Use constant time comparison to prevent timing attacks
    return len(token) == len(expected_token) and sum(
        ord(a) ^ ord(b) for a, b in zip(token, expected_token)
    ) == 0


def validate_parse_mode(parse_mode: str) -> bool:
    """Validate Telegram parse mode.
    
    Args:
        parse_mode: Parse mode to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_modes = ['Markdown', 'MarkdownV2', 'HTML']
    return parse_mode in valid_modes


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
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


def validate_cron_expression(cron_expr: str) -> tuple[bool, Optional[str]]:
    """Validate cron expression format.
    
    Args:
        cron_expr: Cron expression to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(cron_expr, str):
        return False, "Cron expression must be a string"
    
    parts = cron_expr.strip().split()
    
    if len(parts) != 5:
        return False, "Cron expression must have exactly 5 parts (minute hour day month weekday)"
    
    # Basic validation of each part
    ranges = [
        (0, 59),   # minute
        (0, 23),   # hour
        (1, 31),   # day
        (1, 12),   # month
        (0, 6)     # weekday
    ]
    
    for i, (part, (min_val, max_val)) in enumerate(zip(parts, ranges)):
        if part == '*':
            continue
        
        # Handle ranges and lists
        if ',' in part:
            sub_parts = part.split(',')
        else:
            sub_parts = [part]
        
        for sub_part in sub_parts:
            if '/' in sub_part:
                sub_part = sub_part.split('/')[0]
            
            if '-' in sub_part:
                try:
                    start, end = map(int, sub_part.split('-'))
                    if not (min_val <= start <= max_val and min_val <= end <= max_val):
                        return False, f"Invalid range in part {i + 1}: {sub_part}"
                except ValueError:
                    return False, f"Invalid range format in part {i + 1}: {sub_part}"
            else:
                try:
                    val = int(sub_part)
                    if not (min_val <= val <= max_val):
                        return False, f"Value out of range in part {i + 1}: {val}"
                except ValueError:
                    return False, f"Invalid value in part {i + 1}: {sub_part}"
    
    return True, None
