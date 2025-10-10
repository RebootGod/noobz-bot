"""
Multi-Account Manager untuk handle multiple Telegram accounts.
Auto-switch between accounts when flood limit detected.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError, PeerFloodError
from dataclasses import dataclass

from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class AccountStatus:
    """Status information for a Telegram account."""
    account_id: int
    client: TelegramClient
    is_available: bool = True
    cooldown_until: Optional[datetime] = None
    total_messages_sent: int = 0
    last_flood_wait: Optional[int] = None


class MultiAccountManager:
    """
    Manager untuk handle multiple Telegram accounts dengan auto-fallback.
    """
    
    def __init__(self):
        """Initialize multi-account manager."""
        self.settings = get_settings()
        self.accounts: List[AccountStatus] = []
        self.current_account_index: int = 0
        self._initialized = False
    
    async def initialize(self, primary_client=None):
        """
        Initialize semua Telegram accounts.
        
        Args:
            primary_client: Optional primary TelegramClient (if already initialized)
        """
        if self._initialized:
            return
        
        logger.info("Initializing Multi-Account Manager...")
        
        # Use existing primary client or initialize new one
        from services.telegram_client import TelegramHandler
        
        if primary_client:
            # Reuse existing primary client to avoid database lock
            logger.info("Using existing primary account client")
            self.accounts.append(AccountStatus(
                account_id=1,
                client=primary_client,
                is_available=True
            ))
            logger.info(f"✅ Primary account initialized: {self.settings.telegram_phone}")
        else:
            # Initialize new primary client (fallback)
            primary_handler = TelegramHandler()
            primary_client = await primary_handler.initialize()
            
            self.accounts.append(AccountStatus(
                account_id=1,
                client=primary_client,
                is_available=True
            ))
            logger.info(f"✅ Primary account initialized: {self.settings.telegram_phone}")
        
        # Initialize secondary account if configured
        if self.settings.has_secondary_account():
            try:
                secondary_handler = TelegramHandler(use_secondary=True)
                secondary_client = await secondary_handler.initialize()
                
                self.accounts.append(AccountStatus(
                    account_id=2,
                    client=secondary_client,
                    is_available=True
                ))
                
                logger.info(f"✅ Secondary account initialized: {self.settings.telegram_phone_2}")
            except Exception as e:
                logger.warning(f"Failed to initialize secondary account: {e}")
        
        self._initialized = True
        logger.info(f"Multi-Account Manager initialized with {len(self.accounts)} account(s)")
    
    def get_available_client(self) -> Optional[TelegramClient]:
        """
        Get an available Telegram client.
        Auto-switch to next available account if current is on cooldown.
        
        Returns:
            Available TelegramClient or None if all accounts are limited
        """
        if not self.accounts:
            return None
        
        # Check current account first
        current = self.accounts[self.current_account_index]
        if self._is_account_available(current):
            return current.client
        
        # Try other accounts
        for i, account in enumerate(self.accounts):
            if i == self.current_account_index:
                continue
            
            if self._is_account_available(account):
                logger.info(f"Switching to account {account.account_id}")
                self.current_account_index = i
                return account.client
        
        # All accounts are limited
        logger.error("All accounts are currently limited!")
        return None
    
    def _is_account_available(self, account: AccountStatus) -> bool:
        """
        Check if account is available (not on cooldown).
        
        Args:
            account: AccountStatus to check
            
        Returns:
            True if account is available
        """
        if not account.is_available and account.cooldown_until:
            # Check if cooldown expired
            if datetime.now() >= account.cooldown_until:
                account.is_available = True
                account.cooldown_until = None
                logger.info(f"Account {account.account_id} cooldown expired, now available")
                return True
            return False
        
        return account.is_available
    
    async def send_with_fallback(
        self,
        target_entity: Any,
        message: str = None,
        file: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send message dengan automatic fallback ke account lain jika flood detected.
        
        Args:
            target_entity: Target Telegram entity
            message: Text message
            file: File path untuk send file
            **kwargs: Additional arguments untuk send_message/send_file
            
        Returns:
            Result dictionary
        """
        attempts = 0
        max_attempts = len(self.accounts) * 2  # Try each account twice
        
        while attempts < max_attempts:
            client = self.get_available_client()
            
            if not client:
                return {
                    'success': False,
                    'message': 'All accounts are currently rate limited. Please try again later.',
                    'error': 'flood_limit'
                }
            
            try:
                # Get current account
                account = self.accounts[self.current_account_index]
                
                # Send message
                if file:
                    await client.send_file(target_entity, file, caption=message, **kwargs)
                else:
                    await client.send_message(target_entity, message, **kwargs)
                
                # Success!
                account.total_messages_sent += 1
                logger.info(f"Message sent successfully using account {account.account_id}")
                
                return {
                    'success': True,
                    'account_id': account.account_id,
                    'message': f'Sent via account {account.account_id}'
                }
            
            except FloodWaitError as e:
                # Flood limit detected!
                account = self.accounts[self.current_account_index]
                wait_seconds = e.seconds
                
                logger.warning(
                    f"FloodWaitError on account {account.account_id}: "
                    f"Need to wait {wait_seconds} seconds"
                )
                
                # Mark account as limited
                account.is_available = False
                account.cooldown_until = datetime.now() + timedelta(seconds=wait_seconds)
                account.last_flood_wait = wait_seconds
                
                # Try next account
                attempts += 1
                continue
            
            except (UserPrivacyRestrictedError, PeerFloodError) as e:
                # User privacy or peer flood error
                logger.error(f"Privacy/Flood error: {e}")
                return {
                    'success': False,
                    'message': f'Cannot send message: {str(e)}',
                    'error': 'privacy_restricted'
                }
            
            except Exception as e:
                logger.error(f"Unexpected error sending message: {e}")
                return {
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'error': 'unknown'
                }
        
        # Max attempts reached
        return {
            'success': False,
            'message': 'Failed to send message after trying all accounts',
            'error': 'max_attempts_reached'
        }
    
    def get_account_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all accounts.
        
        Returns:
            List of account status dictionaries
        """
        status_list = []
        
        for account in self.accounts:
            status = {
                'account_id': account.account_id,
                'is_available': self._is_account_available(account),
                'total_messages_sent': account.total_messages_sent,
                'last_flood_wait': account.last_flood_wait
            }
            
            if account.cooldown_until:
                remaining = (account.cooldown_until - datetime.now()).total_seconds()
                status['cooldown_remaining_seconds'] = max(0, int(remaining))
            
            status_list.append(status)
        
        return status_list
    
    async def disconnect_all(self):
        """Disconnect all Telegram clients."""
        for account in self.accounts:
            try:
                await account.client.disconnect()
                logger.info(f"Disconnected account {account.account_id}")
            except Exception as e:
                logger.error(f"Error disconnecting account {account.account_id}: {e}")


# Global instance
_multi_account_manager: Optional[MultiAccountManager] = None


def get_multi_account_manager() -> MultiAccountManager:
    """
    Get global MultiAccountManager instance.
    
    Returns:
        MultiAccountManager instance
    """
    global _multi_account_manager
    if _multi_account_manager is None:
        _multi_account_manager = MultiAccountManager()
    return _multi_account_manager
