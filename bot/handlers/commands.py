"""Command handlers for the Telegram bot."""

import datetime
from telegram import Update
from telegram.ext import ContextTypes
from ..constants import MESSAGES, EMOJIS
from ..services.subscription import SubscriptionService
from ..services.notification import notification_service
from ..utils.formatters import format_system_info
import structlog

logger = structlog.get_logger(__name__)


class CommandHandlers:
    """Handles bot commands."""
    
    def __init__(self):
        self.subscription_service = SubscriptionService()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info("Start command received", user_id=user.id, chat_id=chat_id)
        
        await update.message.reply_text(
            MESSAGES['WELCOME'],
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user = update.effective_user
        logger.info("Help command received", user_id=user.id)
        
        await update.message.reply_text(
            MESSAGES['HELP'],
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user = update.effective_user
        logger.info("Status command received", user_id=user.id)
        
        try:
            # Test bot connection
            is_healthy = await notification_service.test_connection()
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            if is_healthy:
                message = MESSAGES['STATUS_OK'].format(timestamp=timestamp)
            else:
                message = MESSAGES['STATUS_ERROR'].format(timestamp=timestamp)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in status command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def system_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /system command."""
        user = update.effective_user
        logger.info("System command received", user_id=user.id)
        
        try:
            system_info = format_system_info(markdown=True)
            await update.message.reply_text(
                system_info,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in system command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
                parse_mode='Markdown'
            )
            return
        
        subscription_type = context.args[0].lower()
        
        try:
            success = await self.subscription_service.subscribe(
                user_id=user.id,
                chat_id=chat_id,
                subscription_type=subscription_type
            )
            
            if success:
                message = MESSAGES['SUBSCRIPTION_SUCCESS'].format(
                    subscription_type=subscription_type
                )
                logger.info("User subscribed", 
                           user_id=user.id, 
                           subscription_type=subscription_type)
            else:
                message = MESSAGES['INVALID_SUBSCRIPTION_TYPE']
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in subscribe command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
                parse_mode='Markdown'
            )
            return
        
        subscription_type = context.args[0].lower()
        
        try:
            success = await self.subscription_service.unsubscribe(
                user_id=user.id,
                subscription_type=subscription_type
            )
            
            if success:
                message = MESSAGES['UNSUBSCRIPTION_SUCCESS'].format(
                    subscription_type=subscription_type
                )
                logger.info("User unsubscribed", 
                           user_id=user.id, 
                           subscription_type=subscription_type)
            else:
                message = MESSAGES['INVALID_SUBSCRIPTION_TYPE']
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in unsubscribe command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def subscriptions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscriptions command."""
        user = update.effective_user
        
        try:
            subscriptions = await self.subscription_service.get_subscriptions(user.id)
            
            if subscriptions:
                subscription_list = "\n".join([f"• `{sub}`" for sub in subscriptions])
                message = MESSAGES['SUBSCRIPTIONS_LIST'].format(
                    subscriptions=subscription_list
                )
            else:
                message = MESSAGES['NO_SUBSCRIPTIONS']
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in subscriptions command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info("Test command received", user_id=user.id)
        
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            message = MESSAGES['TEST_NOTIFICATION'].format(timestamp=timestamp)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error("Error in test command", error=str(e))
            await update.message.reply_text(
                MESSAGES['ERROR_GENERIC'].format(error_id=str(e)[:8]),
                parse_mode='Markdown'
            )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands."""
        user = update.effective_user
        logger.info("Unknown command received", 
                   user_id=user.id, 
                   command=update.message.text)
        
        await update.message.reply_text(
            MESSAGES['COMMAND_NOT_FOUND'],
            parse_mode='Markdown'
        )


# Global handler instance
command_handlers = CommandHandlers()
