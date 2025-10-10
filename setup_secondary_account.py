"""
Setup script untuk initialize secondary Telegram account.
Run this script to login and create session for secondary account.
"""

import asyncio
import logging
import sys

from config.settings import get_settings
from services.telegram_client import TelegramHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def setup_secondary_account():
    """
    Setup secondary Telegram account.
    """
    try:
        settings = get_settings()
        
        # Check if secondary account is configured
        if not settings.has_secondary_account():
            logger.error("❌ Secondary account not configured!")
            logger.info("Please add these to your .env file:")
            logger.info("  TELEGRAM_API_ID_2=your_api_id")
            logger.info("  TELEGRAM_API_HASH_2=your_api_hash")
            logger.info("  TELEGRAM_PHONE_2=+62your_phone")
            return False
        
        logger.info("=" * 60)
        logger.info("SETUP SECONDARY TELEGRAM ACCOUNT")
        logger.info("=" * 60)
        logger.info(f"Phone number: {settings.telegram_phone_2}")
        logger.info("")
        logger.info("This will create a new session for your secondary account.")
        logger.info("You will need to:")
        logger.info("  1. Enter the code sent to your Telegram app")
        logger.info("  2. Enter 2FA password if enabled")
        logger.info("")
        
        # Initialize secondary account
        logger.info("Initializing secondary account...")
        handler = TelegramHandler(use_secondary=True)
        client = await handler.initialize()
        
        # Get user info
        me = handler.get_me()
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ SUCCESS!")
        logger.info("=" * 60)
        logger.info(f"Logged in as: {me.first_name}")
        logger.info(f"Username: @{me.username}")
        logger.info(f"Phone: {me.phone}")
        logger.info(f"Session file: {settings.session_name_2}.session")
        logger.info("")
        logger.info("Secondary account is now ready to use!")
        logger.info("You can now run the bot with multi-account support.")
        logger.info("=" * 60)
        
        # Disconnect
        await handler.disconnect()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup secondary account: {e}")
        return False


async def main():
    """Main function."""
    success = await setup_secondary_account()
    
    if success:
        logger.info("\n✅ Setup completed successfully!")
        logger.info("You can now run: python main.py")
        sys.exit(0)
    else:
        logger.error("\n❌ Setup failed!")
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
