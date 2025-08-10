"""Configuration helper for Telegram Notifier."""

import os
from typing import Optional, List, Union
from pathlib import Path


class NotifierConfig:
    """Configuration helper for TelegramNotifier."""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        """Initialize config.
        
        Args:
            config_file: Optional path to .env file to load
        """
        self.config_file = Path(config_file) if config_file else None
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if specified."""
        if self.config_file and self.config_file.exists():
            try:
                # Simple .env file parser
                with open(self.config_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ.setdefault(key.strip(), value.strip())
            except Exception:
                pass  # Ignore errors in .env parsing
    
    @property
    def bot_token(self) -> Optional[str]:
        """Get bot token from environment."""
        return os.getenv("TELEGRAM_BOT_TOKEN")
    
    @property
    def chat_ids(self) -> List[str]:
        """Get chat IDs from environment."""
        chat_ids_str = os.getenv("TELEGRAM_CHAT_IDS", "")
        return [chat.strip() for chat in chat_ids_str.split(",") if chat.strip()]
    
    @property
    def default_chat_id(self) -> Optional[str]:
        """Get first chat ID as default."""
        chat_ids = self.chat_ids
        return chat_ids[0] if chat_ids else None
    
    def is_configured(self) -> bool:
        """Check if minimum configuration is available."""
        return bool(self.bot_token and self.chat_ids)
    
    def validate(self) -> tuple[bool, str]:
        """Validate configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.bot_token:
            return False, "TELEGRAM_BOT_TOKEN not set"
        
        if not self.chat_ids:
            return False, "TELEGRAM_CHAT_IDS not set"
        
        # Basic token format check
        if not self.bot_token.count(":") == 1:
            return False, "Invalid bot token format"
        
        return True, "Configuration valid"


def setup_from_env(env_file: Optional[Union[str, Path]] = None) -> NotifierConfig:
    """Setup configuration from environment file.
    
    Args:
        env_file: Path to .env file (optional)
        
    Returns:
        NotifierConfig instance
        
    Example:
        >>> config = setup_from_env(".env")
        >>> if config.is_configured():
        ...     notifier = TelegramNotifier(config.bot_token, config.chat_ids)
    """
    return NotifierConfig(env_file)
