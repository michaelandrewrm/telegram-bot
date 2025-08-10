"""Tests for bot command handlers."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes

from bot.handlers.commands import CommandHandlers, command_handlers
from bot.constants import MESSAGES


class TestCommandHandlers:
    """Test cases for CommandHandlers class."""

    @pytest.fixture
    def handler(self):
        """Create a CommandHandlers instance for testing."""
        return CommandHandlers()

    @pytest.fixture
    def mock_update(self):
        """Create a mock Update object."""
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=User)
        update.effective_user.id = 123456789
        update.effective_user.first_name = "Test"
        update.effective_user.username = "testuser"
        
        update.effective_chat = MagicMock(spec=Chat)
        update.effective_chat.id = 123456789
        
        update.message = MagicMock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock Context object."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = []
        return context

    @pytest.mark.asyncio
    async def test_start_command(self, handler, mock_update, mock_context):
        """Test /start command handler."""
        with patch('bot.handlers.commands.logger') as mock_logger:
            await handler.start_command(mock_update, mock_context)
            
            # Verify message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['WELCOME'],
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "Start command received",
                user_id=123456789,
                chat_id=123456789
            )

    @pytest.mark.asyncio
    async def test_help_command(self, handler, mock_update, mock_context):
        """Test /help command handler."""
        with patch('bot.handlers.commands.logger') as mock_logger:
            await handler.help_command(mock_update, mock_context)
            
            # Verify message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['HELP'],
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "Help command received",
                user_id=123456789
            )

    @pytest.mark.asyncio
    async def test_status_command_healthy(self, handler, mock_update, mock_context):
        """Test /status command when bot is healthy."""
        with patch('bot.handlers.commands.notification_service.test_connection') as mock_test_connection, \
             patch('bot.handlers.commands.logger') as mock_logger, \
             patch('bot.handlers.commands.datetime.datetime') as mock_datetime:
            
            # Mock healthy response
            mock_test_connection.return_value = True
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2025-08-10 12:00:00 UTC"
            mock_datetime.now.return_value = mock_now
            
            await handler.status_command(mock_update, mock_context)
            
            # Verify connection test was called
            mock_test_connection.assert_called_once()
            
            # Verify appropriate message was sent
            expected_message = MESSAGES['STATUS_OK'].format(timestamp="2025-08-10 12:00:00 UTC")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "Status command received",
                user_id=123456789
            )

    @pytest.mark.asyncio
    async def test_status_command_unhealthy(self, handler, mock_update, mock_context):
        """Test /status command when bot is unhealthy."""
        with patch('bot.handlers.commands.notification_service.test_connection') as mock_test_connection, \
             patch('bot.handlers.commands.logger') as mock_logger, \
             patch('bot.handlers.commands.datetime.datetime') as mock_datetime:
            
            # Mock unhealthy response
            mock_test_connection.return_value = False
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2025-08-10 12:00:00 UTC"
            mock_datetime.now.return_value = mock_now
            
            await handler.status_command(mock_update, mock_context)
            
            # Verify appropriate message was sent
            expected_message = MESSAGES['STATUS_ERROR'].format(timestamp="2025-08-10 12:00:00 UTC")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )

    @pytest.mark.asyncio
    async def test_status_command_exception(self, handler, mock_update, mock_context):
        """Test /status command when an exception occurs."""
        with patch('bot.handlers.commands.notification_service.test_connection') as mock_test_connection, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            # Mock exception
            mock_test_connection.side_effect = Exception("Connection failed")
            
            await handler.status_command(mock_update, mock_context)
            
            # Verify error message was sent
            expected_message = MESSAGES['ERROR_GENERIC'].format(error_id="Connecti")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "Error in status command",
                error="Connection failed"
            )

    @pytest.mark.asyncio
    async def test_system_command_success(self, handler, mock_update, mock_context):
        """Test /system command successful execution."""
        with patch('bot.handlers.commands.format_system_info') as mock_format, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            mock_format.return_value = "System info formatted"
            
            await handler.system_command(mock_update, mock_context)
            
            # Verify formatter was called
            mock_format.assert_called_once_with(markdown=True)
            
            # Verify message was sent
            mock_update.message.reply_text.assert_called_once_with(
                "System info formatted",
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "System command received",
                user_id=123456789
            )

    @pytest.mark.asyncio
    async def test_system_command_exception(self, handler, mock_update, mock_context):
        """Test /system command when an exception occurs."""
        with patch('bot.handlers.commands.format_system_info') as mock_format, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            # Mock exception
            mock_format.side_effect = Exception("System error")
            
            await handler.system_command(mock_update, mock_context)
            
            # Verify error message was sent
            expected_message = MESSAGES['ERROR_GENERIC'].format(error_id="System e")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "Error in system command",
                error="System error"
            )

    @pytest.mark.asyncio
    async def test_subscribe_command_no_args(self, handler, mock_update, mock_context):
        """Test /subscribe command without arguments."""
        # No arguments provided
        mock_context.args = []
        
        await handler.subscribe_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_update.message.reply_text.assert_called_once_with(
            MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
            parse_mode='Markdown'
        )

    @pytest.mark.asyncio
    async def test_subscribe_command_success(self, handler, mock_update, mock_context):
        """Test /subscribe command successful subscription."""
        mock_context.args = ['system']
        
        with patch.object(handler.subscription_service, 'subscribe') as mock_subscribe, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            mock_subscribe.return_value = True
            
            await handler.subscribe_command(mock_update, mock_context)
            
            # Verify subscription service was called
            mock_subscribe.assert_called_once_with(
                user_id=123456789,
                chat_id=123456789,
                subscription_type='system'
            )
            
            # Verify success message was sent
            expected_message = MESSAGES['SUBSCRIPTION_SUCCESS'].format(
                subscription_type='system'
            )
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "User subscribed",
                user_id=123456789,
                subscription_type='system'
            )

    @pytest.mark.asyncio
    async def test_subscribe_command_invalid_type(self, handler, mock_update, mock_context):
        """Test /subscribe command with invalid subscription type."""
        mock_context.args = ['invalid']
        
        with patch.object(handler.subscription_service, 'subscribe') as mock_subscribe:
            mock_subscribe.return_value = False
            
            await handler.subscribe_command(mock_update, mock_context)
            
            # Verify error message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
                parse_mode='Markdown'
            )

    @pytest.mark.asyncio
    async def test_subscribe_command_exception(self, handler, mock_update, mock_context):
        """Test /subscribe command when an exception occurs."""
        mock_context.args = ['system']
        
        with patch.object(handler.subscription_service, 'subscribe') as mock_subscribe, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            # Mock exception
            mock_subscribe.side_effect = Exception("Database error")
            
            await handler.subscribe_command(mock_update, mock_context)
            
            # Verify error message was sent
            expected_message = MESSAGES['ERROR_GENERIC'].format(error_id="Database")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "Error in subscribe command",
                error="Database error"
            )

    @pytest.mark.asyncio
    async def test_unsubscribe_command_no_args(self, handler, mock_update, mock_context):
        """Test /unsubscribe command without arguments."""
        mock_context.args = []
        
        await handler.unsubscribe_command(mock_update, mock_context)
        
        # Verify error message was sent
        mock_update.message.reply_text.assert_called_once_with(
            MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
            parse_mode='Markdown'
        )

    @pytest.mark.asyncio
    async def test_unsubscribe_command_success(self, handler, mock_update, mock_context):
        """Test /unsubscribe command successful unsubscription."""
        mock_context.args = ['system']
        
        with patch.object(handler.subscription_service, 'unsubscribe') as mock_unsubscribe, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            mock_unsubscribe.return_value = True
            
            await handler.unsubscribe_command(mock_update, mock_context)
            
            # Verify unsubscription service was called
            mock_unsubscribe.assert_called_once_with(
                user_id=123456789,
                subscription_type='system'
            )
            
            # Verify success message was sent
            expected_message = MESSAGES['UNSUBSCRIPTION_SUCCESS'].format(
                subscription_type='system'
            )
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "User unsubscribed",
                user_id=123456789,
                subscription_type='system'
            )

    @pytest.mark.asyncio
    async def test_unsubscribe_command_invalid_type(self, handler, mock_update, mock_context):
        """Test /unsubscribe command with invalid subscription type."""
        mock_context.args = ['invalid']
        
        with patch.object(handler.subscription_service, 'unsubscribe') as mock_unsubscribe:
            mock_unsubscribe.return_value = False
            
            await handler.unsubscribe_command(mock_update, mock_context)
            
            # Verify error message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['INVALID_SUBSCRIPTION_TYPE'],
                parse_mode='Markdown'
            )

    @pytest.mark.asyncio
    async def test_subscriptions_command_with_subscriptions(self, handler, mock_update, mock_context):
        """Test /subscriptions command when user has subscriptions."""
        with patch.object(handler.subscription_service, 'get_subscriptions') as mock_get:
            mock_get.return_value = ['system', 'errors']
            
            await handler.subscriptions_command(mock_update, mock_context)
            
            # Verify service was called
            mock_get.assert_called_once_with(123456789)
            
            # Verify message format
            expected_message = MESSAGES['SUBSCRIPTIONS_LIST'].format(
                subscriptions="• `system`\n• `errors`"
            )
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )

    @pytest.mark.asyncio
    async def test_subscriptions_command_no_subscriptions(self, handler, mock_update, mock_context):
        """Test /subscriptions command when user has no subscriptions."""
        with patch.object(handler.subscription_service, 'get_subscriptions') as mock_get:
            mock_get.return_value = []
            
            await handler.subscriptions_command(mock_update, mock_context)
            
            # Verify message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['NO_SUBSCRIPTIONS'],
                parse_mode='Markdown'
            )

    @pytest.mark.asyncio
    async def test_subscriptions_command_exception(self, handler, mock_update, mock_context):
        """Test /subscriptions command when an exception occurs."""
        with patch.object(handler.subscription_service, 'get_subscriptions') as mock_get, \
             patch('bot.handlers.commands.logger') as mock_logger:
            
            # Mock exception
            mock_get.side_effect = Exception("Database error")
            
            await handler.subscriptions_command(mock_update, mock_context)
            
            # Verify error message was sent
            expected_message = MESSAGES['ERROR_GENERIC'].format(error_id="Database")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "Error in subscriptions command",
                error="Database error"
            )

    @pytest.mark.asyncio
    async def test_test_command(self, handler, mock_update, mock_context):
        """Test /test command."""
        with patch('bot.handlers.commands.logger') as mock_logger, \
             patch('bot.handlers.commands.datetime.datetime') as mock_datetime:
            
            mock_now = MagicMock()
            mock_now.strftime.return_value = "2025-08-10 12:00:00 UTC"
            mock_datetime.now.return_value = mock_now
            
            await handler.test_command(mock_update, mock_context)
            
            # Verify message was sent
            expected_message = MESSAGES['TEST_NOTIFICATION'].format(
                timestamp="2025-08-10 12:00:00 UTC"
            )
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "Test command received",
                user_id=123456789
            )

    @pytest.mark.asyncio
    async def test_test_command_exception(self, handler, mock_update, mock_context):
        """Test /test command when an exception occurs."""
        with patch('bot.handlers.commands.logger') as mock_logger, \
             patch('bot.handlers.commands.datetime.datetime') as mock_datetime:
            
            # Mock exception
            mock_datetime.now.side_effect = Exception("Time error")
            
            await handler.test_command(mock_update, mock_context)
            
            # Verify error message was sent
            expected_message = MESSAGES['ERROR_GENERIC'].format(error_id="Time err")
            mock_update.message.reply_text.assert_called_once_with(
                expected_message,
                parse_mode='Markdown'
            )
            
            # Verify error logging
            mock_logger.error.assert_called_once_with(
                "Error in test command",
                error="Time error"
            )

    @pytest.mark.asyncio
    async def test_unknown_command(self, handler, mock_update, mock_context):
        """Test unknown command handler."""
        mock_update.message.text = "/unknown"
        
        with patch('bot.handlers.commands.logger') as mock_logger:
            await handler.unknown_command(mock_update, mock_context)
            
            # Verify message was sent
            mock_update.message.reply_text.assert_called_once_with(
                MESSAGES['COMMAND_NOT_FOUND'],
                parse_mode='Markdown'
            )
            
            # Verify logging
            mock_logger.info.assert_called_once_with(
                "Unknown command received",
                user_id=123456789,
                command="/unknown"
            )

    def test_global_handler_instance(self):
        """Test that global handler instance is created."""
        assert command_handlers is not None
        assert isinstance(command_handlers, CommandHandlers)


class TestCommandHandlersIntegration:
    """Integration tests for command handlers."""

    @pytest.mark.asyncio
    async def test_command_flow_subscribe_and_list(self):
        """Test the flow of subscribing and listing subscriptions."""
        handler = CommandHandlers()
        
        # Mock update and context
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=User)
        update.effective_user.id = 123456789
        update.effective_chat = MagicMock(spec=Chat)
        update.effective_chat.id = 123456789
        update.message = MagicMock(spec=Message)
        update.message.reply_text = AsyncMock()
        
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.args = ['system']
        
        with patch.object(handler.subscription_service, 'subscribe') as mock_subscribe, \
             patch.object(handler.subscription_service, 'get_subscriptions') as mock_get, \
             patch('bot.handlers.commands.logger'):
            
            # Mock successful subscription
            mock_subscribe.return_value = True
            mock_get.return_value = ['system']
            
            # Test subscribe
            await handler.subscribe_command(update, context)
            
            # Test list subscriptions
            context.args = []  # No args for subscriptions command
            await handler.subscriptions_command(update, context)
            
            # Verify calls
            assert mock_subscribe.call_count == 1
            assert mock_get.call_count == 1
            assert update.message.reply_text.call_count == 2
