"""
Setup script untuk PRIMARY ACCOUNT (Account 1)
Jalankan ini untuk login akun pertama yang akan dipakai sebagai primary account.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.telegram_client import TelegramHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Setup primary account (Account 1)"""
    
    print("\n" + "=" * 60)
    print("SETUP PRIMARY ACCOUNT (Account 1)")
    print("=" * 60)
    print("\nScript ini untuk login AKUN PERTAMA (primary account)")
    print("Session file: noobz_bot_session.session")
    print()
    
    # Load environment variables
    load_dotenv()
    
    phone = os.getenv('TELEGRAM_PHONE')
    if not phone:
        print("\n❌ Error: TELEGRAM_PHONE not found in .env file!")
        print("Please add TELEGRAM_PHONE to your .env file")
        sys.exit(1)
    
    print(f"📱 Phone number: {phone}")
    print("⚠️  PENTING: Pastikan ini nomor telepon yang BENAR untuk primary account!")
    print("   Kamu akan menerima kode login ke nomor ini.")
    print()
    
    confirm = input("Lanjutkan setup dengan nomor ini? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Setup cancelled")
        sys.exit(0)
    print()
    
    # Check if session already exists
    session_file = Path("noobz_bot_session.session")
    if session_file.exists():
        print("⚠️  WARNING: Session file already exists!")
        print(f"   File: {session_file}")
        remove = input("Remove existing session and re-login? (y/n): ").lower()
        if remove == 'y':
            session_file.unlink()
            print("✅ Old session removed")
        else:
            print("❌ Setup cancelled")
            sys.exit(0)
    
    print("\n" + "-" * 60)
    print("Connecting to Telegram...")
    print("-" * 60)
    
    # Initialize Telegram client (primary account)
    telegram = TelegramHandler(use_secondary=False)
    
    try:
        # Start client (will prompt for login if needed)
        await telegram.start()
        
        # Get account info
        me = await telegram.client.get_me()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"Logged in as: {me.first_name} {me.last_name or ''}".strip())
        print(f"Username: @{me.username or 'No username'}")
        print(f"Phone: {me.phone}")
        print(f"User ID: {me.id}")
        print(f"Session file: noobz_bot_session.session")
        print("=" * 60)
        print()
        print("✅ Primary account setup complete!")
        print()
        print("💡 Next steps:")
        print("   1. Setup secondary account: python setup_account_2.py")
        print("   2. Or start the bot: python main.py")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during setup: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        await telegram.stop()

if __name__ == '__main__':
    asyncio.run(main())
