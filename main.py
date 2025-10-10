"""
Main entry point untuk Noobz Bot.
Initialize services dan run bot loop.
"""

import asyncio
import logging
import sys
from telethon import events

from config.settings import get_settings
from services.telegram_client import get_telegram_handler
from services.gemini_service import get_gemini_service
from services.multi_account_manager import get_multi_account_manager
from utils.message_parser import get_message_parser
from utils.message_formatter import get_message_formatter
from handlers.announce_handler import create_announce_handler
from handlers.infofilm_handler import create_infofilm_handler
from handlers.help_handler import create_help_handler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)


class NoobzBot:
    """
    Main bot class untuk Noobz Announcement Bot.
    """
    
    def __init__(self):
        """Initialize bot."""
        self.settings = get_settings()
        self.telegram_handler = get_telegram_handler()
        self.gemini_service = get_gemini_service()
        self.multi_account_manager = get_multi_account_manager()
        self.message_parser = get_message_parser()
        self.formatter = get_message_formatter()
        
        self.client = None
        self.announce_handler = None
        self.infofilm_handler = None
        self.help_handler = None
        self._is_running = False
    
    async def initialize(self):
        """Initialize semua services."""
        try:
            logger.info("=" * 50)
            logger.info(f"Starting {self.settings.bot_name}")
            logger.info("=" * 50)
            
            # Validate settings
            logger.info("Validating settings...")
            self.settings.validate()
            
            # Initialize Telegram client
            logger.info("Initializing Telegram client...")
            self.client = await self.telegram_handler.initialize()
            
            # Initialize Gemini AI
            logger.info("Initializing Gemini AI...")
            logger.info(f"Using model: {self.settings.gemini_model}")
            self.gemini_service.initialize(model_name=self.settings.gemini_model)
            
            # Initialize Multi-Account Manager (if secondary account configured)
            if self.settings.has_secondary_account():
                logger.info("Initializing Multi-Account Manager...")
                await self.multi_account_manager.initialize()
                
                # Show account status
                status = self.multi_account_manager.get_account_status()
                logger.info(f"📊 Active accounts: {len(status)}")
                for acc_status in status:
                    logger.info(f"  Account {acc_status['account_id']}: {'✅ Available' if acc_status['is_available'] else '❌ Limited'}")
            else:
                logger.info("Multi-Account Manager: Disabled (no secondary account configured)")
            
            # Initialize handlers
            logger.info("Initializing command handlers...")
            self.announce_handler = create_announce_handler(self.client)
            self.infofilm_handler = create_infofilm_handler(self.client)
            self.help_handler = create_help_handler(self.client)
            
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def start(self):
        """Start bot dan listen untuk messages."""
        try:
            await self.initialize()
            
            # Register event handlers
            self._register_handlers()
            
            # Get user info
            me = self.telegram_handler.get_me()
            logger.info(f"Bot is running as: {me.first_name} (@{me.username})")
            logger.info("Listening for commands in Saved Messages...")
            logger.info("Press Ctrl+C to stop")
            
            self._is_running = True
            
            # Run until disconnected
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("Received stop signal")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise
        finally:
            await self.shutdown()
    
    def _register_handlers(self):
        """Register event handlers untuk Telegram messages."""
        
        @self.client.on(events.NewMessage(chats='me'))
        async def handle_new_message(event):
            """Handle new messages di Saved Messages."""
            try:
                message_text = event.message.text
                
                if not message_text:
                    return
                
                # Check if message is a command
                if not self.message_parser.is_command(message_text):
                    return
                
                logger.info(f"Received command: {message_text[:50]}...")
                
                # Send processing notification
                await event.respond(self.formatter.format_info("Processing..."))
                
                # Parse command
                parsed_command = self.message_parser.parse(message_text)
                
                # Handle based on command type
                if parsed_command.command == 'announce':
                    result = await self.announce_handler.handle(parsed_command)
                elif parsed_command.command == 'infofilm':
                    result = await self.infofilm_handler.handle(parsed_command)
                elif parsed_command.command == 'help':
                    result = await self.help_handler.handle(parsed_command)
                elif parsed_command.command == 'unknown':
                    result = {
                        'success': False,
                        'message': parsed_command.error_message
                    }
                else:
                    result = {
                        'success': False,
                        'message': 'Unknown command'
                    }
                
                # Send result
                if result['success']:
                    response = self.formatter.format_success(result['message'])
                else:
                    response = self.formatter.format_error(result['message'])
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                error_msg = self.formatter.format_error(f"Internal error: {str(e)}")
                await event.respond(error_msg)
        
        logger.info("Event handlers registered")
    
    async def shutdown(self):
        """Shutdown bot dan cleanup resources."""
        if self._is_running:
            logger.info("Shutting down bot...")
            
            # Disconnect Multi-Account Manager if initialized
            if self.settings.has_secondary_account():
                logger.info("Disconnecting multi-account manager...")
                await self.multi_account_manager.disconnect_all()
            
            # Disconnect Telegram
            await self.telegram_handler.disconnect()
            
            self._is_running = False
            logger.info("Bot stopped")
    
    def is_running(self) -> bool:
        """Check if bot is running."""
        return self._is_running


async def main():
    """Main function."""
    bot = NoobzBot()
    
    try:
        await bot.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
