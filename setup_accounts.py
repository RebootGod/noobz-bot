"""
Setup wizard untuk configure semua Telegram accounts.
Complete setup dari awal untuk primary dan secondary accounts.
"""

import asyncio
import logging
import sys
import os

from config.settings import get_settings
from services.telegram_client import TelegramHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def setup_account(account_type: str, use_secondary: bool = False):
    """
    Setup a Telegram account.
    
    Args:
        account_type: 'primary' atau 'secondary'
        use_secondary: True untuk secondary account
    """
    try:
        settings = get_settings()
        
        if use_secondary and not settings.has_secondary_account():
            logger.warning(f"⚠️ Secondary account not configured in .env")
            logger.info("Please add TELEGRAM_PHONE_2, TELEGRAM_API_ID_2, and TELEGRAM_API_HASH_2")
            return False
        
        phone = settings.telegram_phone_2 if use_secondary else settings.telegram_phone
        session_name = settings.session_name_2 if use_secondary else settings.session_name
        
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"SETUP {account_type.upper()} ACCOUNT")
        logger.info("=" * 60)
        logger.info(f"Phone number: {phone}")
        logger.info("")
        
        # Initialize account
        logger.info("Connecting to Telegram...")
        handler = TelegramHandler(use_secondary=use_secondary)
        client = await handler.initialize()
        
        # Get user info
        me = handler.get_me()
        logger.info("")
        logger.info("✅ SUCCESS!")
        logger.info(f"Logged in as: {me.first_name} (@{me.username})")
        logger.info(f"Phone: {me.phone}")
        logger.info(f"Session file: {session_name}.session")
        logger.info("=" * 60)
        
        # Disconnect
        await handler.disconnect()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup {account_type} account: {e}")
        return False


async def clean_sessions():
    """Remove existing session files."""
    settings = get_settings()
    
    sessions = [
        f"{settings.session_name}.session",
        f"{settings.session_name_2}.session"
    ]
    
    removed = False
    for session_file in sessions:
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.info(f"🗑️  Removed old session: {session_file}")
                removed = True
            except Exception as e:
                logger.warning(f"Failed to remove {session_file}: {e}")
    
    return removed


async def main():
    """Main setup wizard."""
    try:
        settings = get_settings()
        
        logger.info("")
        logger.info("🤖 NOOBZ BOT - ACCOUNT SETUP WIZARD")
        logger.info("=" * 60)
        logger.info("")
        logger.info("This wizard will help you setup your Telegram accounts.")
        logger.info("")
        
        # Check for existing sessions
        primary_exists = os.path.exists(f"{settings.session_name}.session")
        secondary_exists = os.path.exists(f"{settings.session_name_2}.session")
        
        if primary_exists or secondary_exists:
            logger.info("⚠️  Existing session files detected:")
            if primary_exists:
                logger.info(f"  - {settings.session_name}.session")
            if secondary_exists:
                logger.info(f"  - {settings.session_name_2}.session")
            logger.info("")
            
            response = input("Do you want to remove existing sessions and start fresh? (y/n): ")
            if response.lower() == 'y':
                await clean_sessions()
                logger.info("")
            else:
                logger.info("Keeping existing sessions...")
                logger.info("")
        
        # Setup primary account
        logger.info("📱 Step 1: Setup Primary Account")
        logger.info(f"Phone: {settings.telegram_phone}")
        logger.info("")
        
        if not primary_exists or response.lower() == 'y':
            success = await setup_account('primary', use_secondary=False)
            if not success:
                logger.error("\n❌ Failed to setup primary account!")
                return False
        else:
            logger.info("⏭️  Skipping (session already exists)")
        
        # Setup secondary account if configured
        if settings.has_secondary_account():
            logger.info("")
            logger.info("📱 Step 2: Setup Secondary Account (Backup)")
            logger.info(f"Phone: {settings.telegram_phone_2}")
            logger.info("")
            
            response = input("Setup secondary account now? (y/n): ")
            if response.lower() == 'y':
                success = await setup_account('secondary', use_secondary=True)
                if not success:
                    logger.warning("\n⚠️ Failed to setup secondary account")
                    logger.info("You can setup later with: python setup_secondary_account.py")
            else:
                logger.info("⏭️  Skipping secondary account")
                logger.info("You can setup later with: python setup_secondary_account.py")
        else:
            logger.info("")
            logger.info("ℹ️  No secondary account configured in .env")
            logger.info("If you want multi-account support, add these to .env:")
            logger.info("  TELEGRAM_PHONE_2=+628xxx")
            logger.info("  TELEGRAM_API_ID_2=xxx")
            logger.info("  TELEGRAM_API_HASH_2=xxx")
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ SETUP COMPLETE!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("You can now run the bot with:")
        logger.info("  python main.py")
        logger.info("")
        logger.info("Or on production (VPS):")
        logger.info("  sudo systemctl restart noobz-bot")
        logger.info("=" * 60)
        
        return True
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️ Setup cancelled by user")
        return False
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
