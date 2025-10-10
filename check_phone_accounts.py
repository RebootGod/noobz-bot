"""
Diagnostic script to check which Telegram account each phone number belongs to.
This helps identify if phone numbers are correctly mapped to accounts.
"""

import asyncio
import sys
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_phone_account(api_id: int, api_hash: str, phone: str) -> dict:
    """
    Check which Telegram account a phone number belongs to.
    
    Returns:
        dict with account info (name, username, phone) or error
    """
    client = TelegramClient(
        f'temp_check_{phone.replace("+", "")}',
        api_id,
        api_hash
    )
    
    try:
        await client.connect()
        logger.info(f"Connected to Telegram for phone: {phone}")
        
        if await client.is_user_authorized():
            # Already logged in - get account info
            me = await client.get_me()
            return {
                'success': True,
                'name': f"{me.first_name} {me.last_name or ''}".strip(),
                'username': me.username or 'No username',
                'phone': me.phone,
                'id': me.id,
                'logged_in': True
            }
        else:
            # Need to send code
            logger.info(f"Not logged in. Sending code to {phone}...")
            await client.send_code_request(phone)
            
            code = input(f'\nEnter the code you received for {phone}: ')
            
            try:
                await client.sign_in(phone, code)
                me = await client.get_me()
                
                return {
                    'success': True,
                    'name': f"{me.first_name} {me.last_name or ''}".strip(),
                    'username': me.username or 'No username',
                    'phone': me.phone,
                    'id': me.id,
                    'logged_in': False
                }
            except SessionPasswordNeededError:
                logger.warning("This account has 2FA enabled!")
                password = input('Enter your 2FA password: ')
                await client.sign_in(password=password)
                me = await client.get_me()
                
                return {
                    'success': True,
                    'name': f"{me.first_name} {me.last_name or ''}".strip(),
                    'username': me.username or 'No username',
                    'phone': me.phone,
                    'id': me.id,
                    'logged_in': False
                }
                
    except Exception as e:
        logger.error(f"Error checking {phone}: {e}")
        return {
            'success': False,
            'error': str(e),
            'phone': phone
        }
    finally:
        await client.disconnect()
        # Clean up temp session
        import os
        session_file = f'temp_check_{phone.replace("+", "")}.session'
        if os.path.exists(session_file):
            os.remove(session_file)
            logger.info(f"Cleaned up temp session: {session_file}")

async def main():
    print("=" * 60)
    print("TELEGRAM PHONE NUMBER DIAGNOSTIC")
    print("=" * 60)
    print("\nThis script will help you identify which Telegram account")
    print("each phone number belongs to.\n")
    
    # Get credentials
    api_id = input("Enter TELEGRAM_API_ID: ").strip()
    api_hash = input("Enter TELEGRAM_API_HASH: ").strip()
    
    if not api_id or not api_hash:
        print("\n❌ Error: API credentials are required!")
        sys.exit(1)
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("\n❌ Error: API ID must be a number!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("PHONE NUMBERS TO CHECK")
    print("=" * 60)
    
    phones = []
    while True:
        phone = input("\nEnter phone number (with +, or 'done' to finish): ").strip()
        if phone.lower() == 'done':
            break
        if not phone.startswith('+'):
            print("⚠️  Phone must start with + and country code!")
            continue
        phones.append(phone)
        print(f"✅ Added: {phone}")
    
    if not phones:
        print("\n❌ No phone numbers to check!")
        sys.exit(1)
    
    # Check each phone
    results = []
    for phone in phones:
        print("\n" + "=" * 60)
        print(f"Checking phone: {phone}")
        print("=" * 60)
        
        result = await check_phone_account(api_id, api_hash, phone)
        results.append(result)
        
        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"   Name: {result['name']}")
            print(f"   Username: @{result['username']}")
            print(f"   Phone: {result['phone']}")
            print(f"   ID: {result['id']}")
        else:
            print(f"\n❌ FAILED!")
            print(f"   Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for result in results:
        if result['success']:
            print(f"\n📱 {result['phone']}")
            print(f"   → {result['name']} (@{result['username']})")
        else:
            print(f"\n📱 {result['phone']}")
            print(f"   → Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("\n💡 TIP: Make sure your .env file has:")
    print("   TELEGRAM_PHONE = phone for account you want as PRIMARY")
    print("   TELEGRAM_PHONE_2 = phone for account you want as SECONDARY")
    print()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(0)
