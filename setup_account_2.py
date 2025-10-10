"""
Setup script untuk SECONDARY ACCOUNT (Account 2)
Jalankan ini untuk login akun kedua yang akan dipakai sebagai backup account.
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
    """Setup secondary account (Account 2)"""
    
    print("\n" + "=" * 60)
    print("SETUP SECONDARY ACCOUNT (Account 2)")
    print("=" * 60)
    print("\nScript ini untuk login AKUN KEDUA (backup account)")
    print("Session file: noobz_bot_session_2.session")
    print()
    
    # Load environment variables
    load_dotenv()
    
    phone = os.getenv('TELEGRAM_PHONE_2')
    if not phone:
        print("\n❌ Error: TELEGRAM_PHONE_2 not found in .env file!")
        print("Please add these to your .env file:")
        print("  TELEGRAM_PHONE_2=+xxxxxxxxxxxxx")
        print("  TELEGRAM_API_ID_2=xxxxxxxxx (optional, will use primary if not set)")
        print("  TELEGRAM_API_HASH_2=xxxxxxxxx (optional, will use primary if not set)")
        sys.exit(1)
    
    print(f"📱 Phone number: {phone}")
    print("⚠️  PENTING: Pastikan ini nomor telepon yang BENAR untuk secondary account!")
    print("   Kamu akan menerima kode login ke nomor ini.")
    print()
    
    confirm = input("Lanjutkan setup dengan nomor ini? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Setup cancelled")
        sys.exit(0)
    print()
    
    # Check if session already exists
    session_file = Path("noobz_bot_session_2.session")
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
    
    # Initialize Telegram client (secondary account)
    telegram = TelegramHandler(use_secondary=True)
    
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
        print(f"Session file: noobz_bot_session_2.session")
        print("=" * 60)
        print()
        print("✅ Secondary account setup complete!")
        print()
        print("💡 Next step:")
        print("   Start the bot: python main.py")
        print()
        print("📝 Note: Bot will use Account 1 as primary and automatically")
        print("   switch to Account 2 if it hits flood limits.")
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
