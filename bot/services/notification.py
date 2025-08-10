"""Core notification service for sending messages via Telegram."""

import asyncio
import aiofiles
from typing import Optional, List, Union, BinaryIO
from pathlib import Path
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError, RetryAfter, NetworkError
import structlog
from ..config import config
from ..utils.retry import RetryHandler

logger = structlog.get_logger(__name__)


class NotificationService:
    """Service for sending notifications via Telegram."""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize the notification service.
        
        Args:
            bot_token: Telegram bot token. If None, uses config.
        """
        self.bot_token = bot_token or config.telegram_bot_token
        self.bot = Bot(token=self.bot_token)
        self.retry_handler = RetryHandler(
            max_attempts=config.retry_attempts,
            delay=config.retry_delay
        )
        
    async def send_notification(
        self,
        message: str,
        chat_id: Union[str, int],
        parse_mode: Optional[str] = None,
        disable_web_page_preview: bool = True,
        reply_to_message_id: Optional[int] = None,
        reply_markup=None
    ) -> bool:
        """Send a text notification.
        
        Args:
            message: Message text to send
            chat_id: Telegram chat ID
            parse_mode: Message parse mode (Markdown, HTML, or None)
            disable_web_page_preview: Whether to disable web page preview
            reply_to_message_id: ID of message to reply to
            reply_markup: Reply markup (keyboard)
            
        Returns:
            True if successful, False otherwise
        """
        parse_mode = parse_mode or config.default_parse_mode
        
        # Truncate message if too long
        if len(message) > config.max_message_length:
            message = message[:config.max_message_length - 3] + "..."
            logger.warning("Message truncated", 
                         original_length=len(message) + 3,
                         max_length=config.max_message_length)
        
        async def _send():
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_to_message_id=reply_to_message_id,
                reply_markup=reply_markup
            )
        
        return await self._execute_with_retry(_send, chat_id, "text")
    
    async def _prepare_file_data(
        self, 
        file_input: Union[str, Path, BinaryIO]
    ) -> Union[BinaryIO, str, bytes]:
        """Prepare file data for sending.
        
        Args:
            file_input: File path, URL, or file object
            
        Returns:
            Prepared file data
        """
        if isinstance(file_input, (str, Path)):
            file_path = Path(file_input)
            if file_path.exists():
                async with aiofiles.open(file_path, 'rb') as f:
                    return await f.read()
            else:
                # Assume it's a URL
                return str(file_input)
        else:
            return file_input
    
    async def send_photo(
        self,
        chat_id: Union[str, int],
        photo: Union[str, Path, BinaryIO],
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> bool:
        """Send a photo notification.
        
        Args:
            chat_id: Telegram chat ID
            photo: Photo file path, URL, or file object
            caption: Photo caption
            parse_mode: Caption parse mode
            
        Returns:
            True if successful, False otherwise
        """
        parse_mode = parse_mode or config.default_parse_mode
        
        async def _send():
            photo_data = await self._prepare_file_data(photo)
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_data,
                caption=caption,
                parse_mode=parse_mode
            )
        
        return await self._execute_with_retry(_send, chat_id, "photo")
    
    async def send_document(
        self,
        chat_id: Union[str, int],
        document: Union[str, Path, BinaryIO],
        filename: Optional[str] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> bool:
        """Send a document notification.
        
        Args:
            chat_id: Telegram chat ID
            document: Document file path, URL, or file object
            filename: Custom filename
            caption: Document caption
            parse_mode: Caption parse mode
            
        Returns:
            True if successful, False otherwise
        """
        parse_mode = parse_mode or config.default_parse_mode
        
        async def _send():
            document_data = await self._prepare_file_data(document)
            await self.bot.send_document(
                chat_id=chat_id,
                document=document_data,
                filename=filename or (Path(document).name if isinstance(document, (str, Path)) else None),
                caption=caption,
                parse_mode=parse_mode
            )
        
        return await self._execute_with_retry(_send, chat_id, "document")
    
    async def send_video(
        self,
        chat_id: Union[str, int],
        video: Union[str, Path, BinaryIO],
        duration: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        caption: Optional[str] = None,
        parse_mode: Optional[str] = None
    ) -> bool:
        """Send a video notification.
        
        Args:
            chat_id: Telegram chat ID
            video: Video file path, URL, or file object
            duration: Video duration in seconds
            width: Video width
            height: Video height
            caption: Video caption
            parse_mode: Caption parse mode
            
        Returns:
            True if successful, False otherwise
        """
        parse_mode = parse_mode or config.default_parse_mode
        
        async def _send():
            if isinstance(video, (str, Path)):
                if Path(video).exists():
                    async with aiofiles.open(video, 'rb') as f:
                        video_data = await f.read()
                    await self.bot.send_video(
                        chat_id=chat_id,
                        video=video_data,
                        duration=duration,
                        width=width,
                        height=height,
                        caption=caption,
                        parse_mode=parse_mode
                    )
                else:
                    # Assume it's a URL
                    await self.bot.send_video(
                        chat_id=chat_id,
                        video=str(video),
                        duration=duration,
                        width=width,
                        height=height,
                        caption=caption,
                        parse_mode=parse_mode
                    )
            else:
                await self.bot.send_video(
                    chat_id=chat_id,
                    video=video,
                    duration=duration,
                    width=width,
                    height=height,
                    caption=caption,
                    parse_mode=parse_mode
                )
        
        return await self._execute_with_retry(_send, chat_id, "video")
    
    async def send_to_multiple(
        self,
        message: str,
        chat_ids: List[Union[str, int]],
        **kwargs
    ) -> List[bool]:
        """Send notification to multiple chats.
        
        Args:
            message: Message to send
            chat_ids: List of chat IDs
            **kwargs: Additional arguments for send_notification
            
        Returns:
            List of success statuses for each chat
        """
        tasks = [
            self.send_notification(message, chat_id, **kwargs)
            for chat_id in chat_ids
        ]
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def send_to_default_chats(
        self,
        message: str,
        **kwargs
    ) -> List[bool]:
        """Send notification to default chat IDs.
        
        Args:
            message: Message to send
            **kwargs: Additional arguments for send_notification
            
        Returns:
            List of success statuses for each chat
        """
        chat_ids = config.default_chat_ids
        if not chat_ids:
            logger.warning("No default chat IDs configured")
            return []
        
        return await self.send_to_multiple(message, chat_ids, **kwargs)
    
    async def _execute_with_retry(
        self, 
        func, 
        chat_id: Union[str, int], 
        message_type: str
    ) -> bool:
        """Execute function with retry logic.
        
        Args:
            func: Async function to execute
            chat_id: Chat ID for logging
            message_type: Type of message for logging
            
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.retry_handler.execute(func)
            logger.info("Message sent successfully",
                       chat_id=chat_id,
                       message_type=message_type)
            return True
            
        except RetryAfter as e:
            logger.error("Rate limited by Telegram",
                        chat_id=chat_id,
                        retry_after=e.retry_after,
                        message_type=message_type)
            # Wait for the specified time and try once more
            await asyncio.sleep(e.retry_after)
            try:
                await func()
                logger.info("Message sent after rate limit",
                           chat_id=chat_id,
                           message_type=message_type)
                return True
            except Exception as retry_error:
                logger.error("Failed after rate limit retry",
                           chat_id=chat_id,
                           error=str(retry_error),
                           message_type=message_type)
                return False
                
        except TelegramError as e:
            logger.error("Telegram API error",
                        chat_id=chat_id,
                        error=str(e),
                        message_type=message_type)
            return False
            
        except Exception as e:
            logger.error("Unexpected error sending message",
                        chat_id=chat_id,
                        error=str(e),
                        message_type=message_type)
            return False
    
    async def test_connection(self) -> bool:
        """Test the bot connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            bot_info = await self.bot.get_me()
            logger.info("Bot connection test successful",
                       bot_username=bot_info.username,
                       bot_id=bot_info.id)
            return True
        except Exception as e:
            logger.error("Bot connection test failed", error=str(e))
            return False


# Global notification service instance
notification_service = NotificationService()


# Convenience function for easy importing
async def send_notification(
    message: str,
    chat_id: Optional[Union[str, int]] = None,
    **kwargs
) -> bool:
    """Send a notification message.
    
    Args:
        message: Message to send
        chat_id: Chat ID. If None, sends to default chats
        **kwargs: Additional arguments
        
    Returns:
        True if successful, False otherwise
    """
    if chat_id is not None:
        return await notification_service.send_notification(message, chat_id, **kwargs)
    else:
        results = await notification_service.send_to_default_chats(message, **kwargs)
        return all(results) if results else False
