"""
Telegram Client handler menggunakan Telethon.
Manage connection, authentication, dan provide client instance.
"""

import logging
from typing import Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User

from config.settings import get_settings

logger = logging.getLogger(__name__)


class TelegramHandler:
    """
    Handler untuk manage Telethon client.
    Support multiple accounts dengan parameter use_secondary.
    """
    
    def __init__(self, use_secondary: bool = False):
        """
        Initialize handler.
        
        Args:
            use_secondary: If True, use secondary account configuration
        """
        self.settings = get_settings()
        self.use_secondary = use_secondary
        self._is_connected = False
        self._me: Optional[User] = None
        self._client: Optional[TelegramClient] = None
        self._config = None  # Store config for later use
    
    async def initialize(self) -> TelegramClient:
        """
        Initialize dan connect Telegram client.
        
        Returns:
            TelegramClient instance
            
        Raises:
            Exception: Jika gagal connect atau authenticate
        """
        if self._client is not None and self._is_connected:
            logger.info("Telegram client already connected")
            return self._client
        
        try:
            # Get config for primary or secondary account
            if self.use_secondary:
                config = self.settings.get_telegram_config_2()
                if not config:
                    raise ValueError("Secondary account not configured in .env")
                logger.info("Using secondary Telegram account")
            else:
                config = self.settings.get_telegram_config()
                logger.info("Using primary Telegram account")
            
            # Store config for authorization
            self._config = config
            
            # Create client instance
            self._client = TelegramClient(
                config['session_name'],
                config['api_id'],
                config['api_hash']
            )
            
            logger.info("Connecting to Telegram...")
            await self._client.connect()
            
            # Check if authorized
            if not await self._client.is_user_authorized():
                logger.info("Client not authorized, starting authorization...")
                await self._authorize()
            
            # Get current user info
            self._me = await self._client.get_me()
            self._is_connected = True
            
            logger.info(f"Successfully connected as {self._me.first_name} (@{self._me.username})")
            return self._client
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            raise
    
    async def _authorize(self):
        """
        Authorize client dengan phone number.
        
        Raises:
            Exception: Jika gagal authorize
        """
        try:
            # Get phone from stored config
            phone = self._config['phone'] if self._config else self.settings.telegram_phone
            
            # Validate phone format
            if not phone.startswith('+'):
                raise ValueError(
                    f"Invalid phone format: '{phone}'. "
                    f"Phone must start with + and country code. "
                    f"Example: +62812345678900 (for Indonesia)"
                )
            
            await self._client.send_code_request(phone)
            
            # Prompt untuk code
            code = input('Enter the code you received: ')
            
            try:
                await self._client.sign_in(phone, code)
            except SessionPasswordNeededError:
                # Jika ada 2FA
                password = input('Two-factor authentication enabled. Please enter your password: ')
                await self._client.sign_in(password=password)
                
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect client."""
        if self._client and self._is_connected:
            await self._client.disconnect()
            self._is_connected = False
            logger.info("Telegram client disconnected")
    
    def get_client(self) -> Optional[TelegramClient]:
        """
        Get current client instance.
        
        Returns:
            TelegramClient instance atau None jika belum initialized
        """
        return self._client
    
    def is_connected(self) -> bool:
        """
        Check apakah client connected.
        
        Returns:
            True jika connected
        """
        return self._is_connected
    
    def get_me(self) -> Optional[User]:
        """
        Get current user info.
        
        Returns:
            User object atau None
        """
        return self._me
    
    async def get_saved_messages_chat(self):
        """
        Get Saved Messages chat entity.
        
        Returns:
            Chat entity untuk Saved Messages
        """
        if not self._client or not self._is_connected:
            raise Exception("Client not connected")
        
        # Saved Messages adalah chat dengan diri sendiri
        return await self._client.get_entity('me')
    
    async def send_message(
        self, 
        entity, 
        message: str, 
        parse_mode: str = 'markdown'
    ):
        """
        Send message ke entity tertentu.
        
        Args:
            entity: Target entity (user, chat, channel)
            message: Message text
            parse_mode: Parse mode untuk formatting (markdown/html)
            
        Returns:
            Sent message object
        """
        if not self._client or not self._is_connected:
            raise Exception("Client not connected")
        
        return await self._client.send_message(
            entity,
            message,
            parse_mode=parse_mode
        )
    
    async def get_dialogs(self, limit: Optional[int] = None):
        """
        Get list of dialogs (chats, channels, groups).
        
        Args:
            limit: Maximum number of dialogs to get
            
        Returns:
            List of dialogs
        """
        if not self._client or not self._is_connected:
            raise Exception("Client not connected")
        
        return await self._client.get_dialogs(limit=limit)


# Global instance
_telegram_handler: Optional[TelegramHandler] = None


def get_telegram_handler() -> TelegramHandler:
    """
    Get global TelegramHandler instance (primary account).
    
    Returns:
        TelegramHandler instance
    """
    global _telegram_handler
    if _telegram_handler is None:
        _telegram_handler = TelegramHandler(use_secondary=False)
    return _telegram_handler
