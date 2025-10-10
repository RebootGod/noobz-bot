"""
Setup script untuk initialize primary Telegram account.
Run this script to login and create session for primary account.
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


async def setup_primary_account():
    """
    Setup primary Telegram account.
    """
    try:
        settings = get_settings()
        
        logger.info("=" * 60)
        logger.info("SETUP PRIMARY TELEGRAM ACCOUNT")
        logger.info("=" * 60)
        logger.info(f"Phone number: {settings.telegram_phone}")
        logger.info("")
        logger.info("This will create a new session for your primary account.")
        logger.info("You will need to:")
        logger.info("  1. Enter the code sent to your Telegram app")
        logger.info("  2. Enter 2FA password if enabled")
        logger.info("")
        
        # Initialize primary account
        logger.info("Initializing primary account...")
        handler = TelegramHandler(use_secondary=False)
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
        logger.info(f"Session file: {settings.session_name}.session")
        logger.info("")
        logger.info("Primary account is now ready to use!")
        logger.info("=" * 60)
        
        # Disconnect
        await handler.disconnect()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup primary account: {e}")
        return False


async def main():
    """Main function."""
    success = await setup_primary_account()
    
    if success:
        logger.info("\n✅ Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. (Optional) Setup secondary account: python setup_secondary_account.py")
        logger.info("  2. Run the bot: python main.py")
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
