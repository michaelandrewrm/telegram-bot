"""Simplified notification interface for external applications."""

import asyncio
import os
from typing import Optional, Union, List
from pathlib import Path
import logging

# Try to import telegram, provide helpful error if not available
try:
    from telegram import Bot
    from telegram.constants import ParseMode
except ImportError:
    raise ImportError(
        "python-telegram-bot is required. Install with: pip install python-telegram-bot"
    )

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Simple Telegram notifier for external applications."""
    
    def __init__(
        self, 
        bot_token: Optional[str] = None,
        default_chat_ids: Optional[List[Union[str, int]]] = None,
        parse_mode: str = "Markdown"
    ):
        """Initialize notifier.
        
        Args:
            bot_token: Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)
            default_chat_ids: Default chat IDs (or set TELEGRAM_CHAT_IDS env var)
            parse_mode: Default parse mode (Markdown, HTML, or None)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError(
                "Bot token required: pass bot_token parameter or set TELEGRAM_BOT_TOKEN environment variable"
            )
        
        # Handle default chat IDs from parameter or environment
        if default_chat_ids:
            self.default_chat_ids = [str(chat) for chat in default_chat_ids]
        else:
            env_chat_ids = os.getenv("TELEGRAM_CHAT_IDS", "")
            self.default_chat_ids = [chat.strip() for chat in env_chat_ids.split(",") if chat.strip()]
        
        self.parse_mode = parse_mode
        self.bot = Bot(token=self.bot_token)
    
    async def send(
        self,
        message: str,
        chat_id: Optional[Union[str, int]] = None,
        parse_mode: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Send a notification message.
        
        Args:
            message: Message text
            chat_id: Specific chat ID (uses default if None)
            parse_mode: Message formatting (Markdown, HTML, or None)
            **kwargs: Additional telegram send_message parameters
            
        Returns:
            True if sent to at least one chat successfully
        """
        try:
            parse_mode = parse_mode or self.parse_mode
            
            if chat_id:
                # Send to specific chat
                await self.bot.send_message(
                    chat_id=str(chat_id),
                    text=message,
                    parse_mode=parse_mode,
                    **kwargs
                )
                logger.info(f"Message sent to chat {chat_id}")
                return True
            else:
                # Send to all default chats
                if not self.default_chat_ids:
                    logger.warning("No default chat IDs configured")
                    return False
                
                success_count = 0
                for chat in self.default_chat_ids:
                    try:
                        await self.bot.send_message(
                            chat_id=chat,
                            text=message,
                            parse_mode=parse_mode,
                            **kwargs
                        )
                        success_count += 1
                        logger.info(f"Message sent to chat {chat}")
                    except Exception as e:
                        logger.error(f"Failed to send to chat {chat}: {str(e)}")
                
                return success_count > 0
                
        except Exception as e:
            logger.error(f"Send failed: {str(e)}")
            return False
    
    async def send_file(
        self,
        file_path: Union[str, Path],
        caption: str = "",
        chat_id: Optional[Union[str, int]] = None,
        **kwargs
    ) -> bool:
        """Send a file with optional caption.
        
        Args:
            file_path: Path to file to send
            caption: Optional caption for the file
            chat_id: Specific chat ID (uses default if None)
            **kwargs: Additional telegram parameters
            
        Returns:
            True if sent successfully
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            chat_ids = [str(chat_id)] if chat_id else self.default_chat_ids
            if not chat_ids:
                logger.warning("No chat IDs available for file send")
                return False
            
            success_count = 0
            for chat in chat_ids:
                try:
                    with open(file_path, 'rb') as file:
                        if file_path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}:
                            await self.bot.send_photo(
                                chat_id=chat,
                                photo=file,
                                caption=caption,
                                **kwargs
                            )
                        else:
                            await self.bot.send_document(
                                chat_id=chat,
                                document=file,
                                caption=caption,
                                **kwargs
                            )
                    success_count += 1
                    logger.info(f"File sent to chat {chat}")
                except Exception as e:
                    logger.error(f"Failed to send file to chat {chat}: {str(e)}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"File send failed: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test if the bot token is valid and bot can connect.
        
        Returns:
            True if connection successful
        """
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connection successful: {bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"Bot connection failed: {str(e)}")
            return False


# Convenience functions for quick use
async def send_notification(
    message: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[Union[str, int]] = None,
    **kwargs
) -> bool:
    """Quick async send function.
    
    Args:
        message: Message text
        bot_token: Bot token (or use TELEGRAM_BOT_TOKEN env var)
        chat_id: Chat ID (or use TELEGRAM_CHAT_IDS env var)
        **kwargs: Additional parameters
        
    Returns:
        True if successful
    """
    notifier = TelegramNotifier(bot_token=bot_token)
    return await notifier.send(message, chat_id=chat_id, **kwargs)


def send_notification_sync(
    message: str,
    bot_token: Optional[str] = None,
    chat_id: Optional[Union[str, int]] = None,
    **kwargs
) -> bool:
    """Synchronous version of send_notification.
    
    Perfect for non-async applications or quick notifications.
    
    Args:
        message: Message text
        bot_token: Bot token (or use TELEGRAM_BOT_TOKEN env var)
        chat_id: Chat ID (or use TELEGRAM_CHAT_IDS env var)
        **kwargs: Additional parameters
        
    Returns:
        True if successful
        
    Example:
        >>> send_notification_sync("Hello World!", chat_id="123456789")
        True
    """
    try:
        return asyncio.run(send_notification(message, bot_token, chat_id, **kwargs))
    except Exception as e:
        logger.error(f"Sync notification failed: {str(e)}")
        return False


# Context manager for batch notifications
class NotificationBatch:
    """Context manager for sending multiple notifications efficiently."""
    
    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self.messages = []
    
    def add(self, message: str, chat_id: Optional[Union[str, int]] = None, **kwargs):
        """Add a message to the batch."""
        self.messages.append((message, chat_id, kwargs))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Send all batched messages."""
        results = []
        for message, chat_id, kwargs in self.messages:
            result = await self.notifier.send(message, chat_id, **kwargs)
            results.append(result)
        return results
