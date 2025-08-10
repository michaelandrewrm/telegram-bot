"""Main Telegram bot application."""

import asyncio
import logging
import structlog
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .config import config
from .handlers.commands import command_handlers
from .services.monitoring import monitoring_service
from .services.scheduler import scheduler_service
from .constants import COMMANDS

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.log_level.upper()),
    filename=config.log_file
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class TelegramBot:
    """Main Telegram bot class."""
    
    def __init__(self):
        self.application = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize the bot application."""
        try:
            # Create application
            self.application = Application.builder().token(config.telegram_bot_token).build()
            
            # Add handlers
            self._add_handlers()
            
            logger.info("Bot initialized successfully")
            
        except Exception as e:
            logger.error("Error initializing bot", error=str(e))
            raise
    
    def _add_handlers(self):
        """Add command and message handlers."""
        # Command handlers
        self.application.add_handler(
            CommandHandler(COMMANDS['START'], command_handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['HELP'], command_handlers.help_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['STATUS'], command_handlers.status_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['SUBSCRIBE'], command_handlers.subscribe_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['UNSUBSCRIBE'], command_handlers.unsubscribe_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['LIST_SUBSCRIPTIONS'], command_handlers.subscriptions_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['SYSTEM_INFO'], command_handlers.system_command)
        )
        self.application.add_handler(
            CommandHandler(COMMANDS['TEST'], command_handlers.test_command)
        )
        
        # Unknown command handler (should be last)
        self.application.add_handler(
            MessageHandler(filters.COMMAND, command_handlers.unknown_command)
        )
        
        logger.info("Handlers added to bot application")
    
    async def start_polling(self):
        """Start the bot with polling."""
        try:
            if not self.application:
                await self.initialize()
            
            self.is_running = True
            
            # Start services
            await self._start_services()
            
            # Start polling with the correct async method
            logger.info("Starting bot polling")
            async with self.application:
                await self.application.start()
                await self.application.updater.start_polling(
                    poll_interval=config.polling_interval,
                    timeout=10,
                    bootstrap_retries=3,
                    drop_pending_updates=True
                )
                
                # Keep running until stopped
                while self.is_running:
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error("Error starting bot polling", error=str(e))
            raise
        finally:
            await self._stop_services()
    
    async def start_webhook(self, webhook_url: str, port: int = 8443):
        """Start the bot with webhook."""
        try:
            if not self.application:
                await self.initialize()
            
            self.is_running = True
            
            # Start services
            await self._start_services()
            
            # Start webhook
            logger.info("Starting bot webhook", webhook_url=webhook_url, port=port)
            await self.application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=config.telegram_bot_token,
                webhook_url=f"{webhook_url}/{config.telegram_bot_token}",
                secret_token=config.webhook_secret
            )
            
        except Exception as e:
            logger.error("Error starting bot webhook", error=str(e))
            raise
        finally:
            await self._stop_services()
    
    async def _start_services(self):
        """Start background services."""
        try:
            # Start scheduler service
            if config.enable_scheduling:
                await scheduler_service.start()
            
            # Start monitoring service
            if config.enable_monitoring:
                asyncio.create_task(monitoring_service.start_monitoring())
            
            logger.info("Background services started")
            
        except Exception as e:
            logger.error("Error starting services", error=str(e))
    
    async def _stop_services(self):
        """Stop background services."""
        try:
            # Stop monitoring service
            if config.enable_monitoring:
                await monitoring_service.stop_monitoring()
            
            # Stop scheduler service
            if config.enable_scheduling:
                await scheduler_service.stop()
            
            logger.info("Background services stopped")
            
        except Exception as e:
            logger.error("Error stopping services", error=str(e))
    
    async def stop(self):
        """Stop the bot."""
        try:
            self.is_running = False
            
            # Stop services first
            await self._stop_services()
            
            logger.info("Bot stopped")
            
        except Exception as e:
            logger.error("Error stopping bot", error=str(e))


async def main():
    """Main entry point."""
    bot = TelegramBot()
    
    try:
        # Determine run mode
        if config.webhook_url:
            await bot.start_webhook(config.webhook_url)
        else:
            await bot.start_polling()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Bot crashed", error=str(e))
    finally:
        try:
            await bot.stop()
        except Exception as stop_error:
            logger.error("Error during bot cleanup", error=str(stop_error))


if __name__ == "__main__":
    asyncio.run(main())
