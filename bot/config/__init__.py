"""Configuration management for the Telegram bot."""

import os
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv
import structlog

logger = structlog.get_logger(__name__)


class Config:
    """Configuration class that loads settings from .env and config.yaml files."""
    
    def __init__(self, config_path: Optional[Path] = None, env_path: Optional[Path] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
            env_path: Path to .env file
        """
        self.config_path = config_path or Path("config.yaml")
        self.env_path = env_path or Path(".env")
        
        # Load environment variables
        if self.env_path.exists():
            load_dotenv(self.env_path)
            logger.info("Loaded environment variables", path=str(self.env_path))
        
        # Load YAML configuration
        self.yaml_config = {}
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.yaml_config = yaml.safe_load(f) or {}
            logger.info("Loaded YAML configuration", path=str(self.config_path))
    
    def get(self, key: str, default: Any = None, section: Optional[str] = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not found
            section: YAML section to look in
            
        Returns:
            Configuration value
        """
        # First try environment variable (uppercase)
        env_key = key.upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Then try YAML config
        if section and section in self.yaml_config:
            return self.yaml_config[section].get(key, default)
        
        # Search all sections for the key
        for section_data in self.yaml_config.values():
            if isinstance(section_data, dict) and key in section_data:
                return section_data[key]
        
        return default
    
    def get_list(self, key: str, default: Optional[List] = None, separator: str = ",") -> List:
        """Get configuration value as a list.
        
        Args:
            key: Configuration key
            default: Default value if not found
            separator: Separator for string values
            
        Returns:
            List of values
        """
        value = self.get(key, default)
        if value is None:
            return default or []
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        
        return [value]
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get configuration value as integer."""
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get configuration value as float."""
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        return bool(value)
    
    # Bot configuration properties
    @property
    def telegram_bot_token(self) -> str:
        """Get Telegram bot token."""
        token = self.get("telegram_bot_token")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        return token
    
    @property
    def webhook_secret(self) -> Optional[str]:
        """Get webhook secret."""
        return self.get("telegram_webhook_secret")
    
    @property
    def default_chat_ids(self) -> List[str]:
        """Get default chat IDs."""
        return self.get_list("default_chat_ids")
    
    @property
    def api_host(self) -> str:
        """Get API host."""
        return self.get("api_host", "0.0.0.0")
    
    @property
    def api_port(self) -> int:
        """Get API port."""
        return self.get_int("api_port", 8080)
    
    @property
    def api_secret_key(self) -> str:
        """Get API secret key."""
        return self.get("api_secret_key", "your-secret-key-change-this")
    
    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get("log_level", "INFO")
    
    @property
    def log_file(self) -> Optional[str]:
        """Get log file path."""
        return self.get("log_file")
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.get("database_url", "sqlite:///bot.db")
    
    # Bot settings from YAML
    @property
    def bot_name(self) -> str:
        """Get bot name."""
        return self.get("name", "Notification Bot", "bot")
    
    @property
    def bot_description(self) -> str:
        """Get bot description."""
        return self.get("description", "Automated notification system", "bot")
    
    @property
    def webhook_url(self) -> Optional[str]:
        """Get webhook URL."""
        return self.get("webhook_url", section="bot")
    
    @property
    def polling_interval(self) -> int:
        """Get polling interval."""
        return self.get_int("polling_interval", 1)
    
    @property
    def default_parse_mode(self) -> Optional[str]:
        """Get default parse mode."""
        return self.get("default_parse_mode", "Markdown", "notifications")
    
    @property
    def retry_attempts(self) -> int:
        """Get retry attempts."""
        return self.get_int("retry_attempts", 3)
    
    @property
    def retry_delay(self) -> int:
        """Get retry delay."""
        return self.get_int("retry_delay", 1)
    
    @property
    def max_message_length(self) -> int:
        """Get max message length."""
        return self.get_int("max_message_length", 4096)
    
    @property
    def scheduler_timezone(self) -> str:
        """Get scheduler timezone."""
        return self.get("timezone", "UTC", "scheduler")
    
    @property
    def scheduler_max_workers(self) -> int:
        """Get scheduler max workers."""
        return self.get_int("max_workers", 5)
    
    @property
    def api_enabled(self) -> bool:
        """Check if API is enabled."""
        return self.get_bool("enabled", True, "api")
    
    @property
    def api_title(self) -> str:
        """Get API title."""
        return self.get("title", "Telegram Bot API", "api")
    
    @property
    def api_version(self) -> str:
        """Get API version."""
        return self.get("version", "1.0.0", "api")
    
    @property
    def api_docs_url(self) -> str:
        """Get API docs URL."""
        return self.get("docs_url", "/docs", "api")
    
    @property
    def require_webhook_auth(self) -> bool:
        """Check if webhook auth is required."""
        return self.get_bool("require_webhook_auth", True, "security")
    
    @property
    def allowed_users(self) -> List[int]:
        """Get allowed user IDs."""
        users = self.get("allowed_users", [], "security")
        return [int(uid) for uid in users if str(uid).isdigit()]
    
    @property
    def rate_limit(self) -> int:
        """Get rate limit."""
        return self.get_int("rate_limit", 10)
    
    # Monitoring thresholds
    @property
    def cpu_threshold(self) -> float:
        """Get CPU threshold."""
        return self.get_float("cpu_threshold", 80.0)
    
    @property
    def memory_threshold(self) -> float:
        """Get memory threshold."""
        return self.get_float("memory_threshold", 80.0)
    
    @property
    def disk_threshold(self) -> float:
        """Get disk threshold."""
        return self.get_float("disk_threshold", 90.0)
    
    # Feature flags
    @property
    def enable_subscriptions(self) -> bool:
        """Check if subscriptions are enabled."""
        return self.get_bool("enable_subscriptions", True, "features")
    
    @property
    def enable_file_uploads(self) -> bool:
        """Check if file uploads are enabled."""
        return self.get_bool("enable_file_uploads", True, "features")
    
    @property
    def enable_scheduling(self) -> bool:
        """Check if scheduling is enabled."""
        return self.get_bool("enable_scheduling", True, "features")
    
    @property
    def enable_monitoring(self) -> bool:
        """Check if monitoring is enabled."""
        return self.get_bool("enable_monitoring", True, "features")


# Global configuration instance
config = Config()
