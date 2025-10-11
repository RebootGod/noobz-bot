"""
Authentication configuration untuk Telegram bot.
Manage whitelist users yang bisa akses upload commands.
"""

from typing import List, Set
import os
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    """
    Configuration untuk authentication dan authorization.
    Manage whitelist Telegram user IDs yang bisa upload content.
    """
    
    def __init__(self):
        """Initialize authentication configuration."""
        # Whitelist Telegram User IDs (comma-separated di .env)
        whitelist_str = os.getenv('TELEGRAM_UPLOAD_WHITELIST', '')
        
        # Parse comma-separated string ke set of integers
        self.whitelist_user_ids: Set[int] = set()
        if whitelist_str:
            try:
                self.whitelist_user_ids = {
                    int(user_id.strip()) 
                    for user_id in whitelist_str.split(',') 
                    if user_id.strip()
                }
            except ValueError as e:
                print(f"Error parsing TELEGRAM_UPLOAD_WHITELIST: {e}")
                self.whitelist_user_ids = set()
        
        # Admin User IDs (untuk logging purposes)
        admin_str = os.getenv('TELEGRAM_ADMIN_IDS', '')
        self.admin_user_ids: Set[int] = set()
        if admin_str:
            try:
                self.admin_user_ids = {
                    int(user_id.strip()) 
                    for user_id in admin_str.split(',') 
                    if user_id.strip()
                }
            except ValueError as e:
                print(f"Error parsing TELEGRAM_ADMIN_IDS: {e}")
                self.admin_user_ids = set()
    
    def is_authorized(self, user_id: int) -> bool:
        """
        Check apakah user ID ada di whitelist.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True jika user authorized, False jika tidak
        """
        return user_id in self.whitelist_user_ids
    
    def is_admin(self, user_id: int) -> bool:
        """
        Check apakah user ID adalah admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True jika user adalah admin, False jika tidak
        """
        return user_id in self.admin_user_ids
    
    def get_whitelist_count(self) -> int:
        """
        Get jumlah user di whitelist.
        
        Returns:
            Jumlah user yang authorized
        """
        return len(self.whitelist_user_ids)
    
    def get_whitelist_users(self) -> List[int]:
        """
        Get list semua whitelisted user IDs.
        
        Returns:
            List of authorized user IDs
        """
        return sorted(list(self.whitelist_user_ids))


# Singleton instance
_auth_config_instance = None


def get_auth_config() -> AuthConfig:
    """
    Get singleton instance of AuthConfig.
    
    Returns:
        AuthConfig instance
    """
    global _auth_config_instance
    if _auth_config_instance is None:
        _auth_config_instance = AuthConfig()
    return _auth_config_instance
