"""
Configuration settings untuk Noobz Bot.
Load environment variables dan provide access ke seluruh aplikasi.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables dari .env file
load_dotenv()


class Settings:
    """
    Class untuk manage semua configuration settings.
    Singleton pattern untuk ensure consistency.
    """
    
    _instance: Optional['Settings'] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize settings dari environment variables."""
        if self._initialized:
            return
            
        # Telegram Configuration (Primary Account)
        self.telegram_api_id = self._get_env('TELEGRAM_API_ID', required=True, cast=int)
        self.telegram_api_hash = self._get_env('TELEGRAM_API_HASH', required=True)
        self.telegram_phone = self._get_env('TELEGRAM_PHONE', required=True)
        
        # Telegram Configuration (Secondary Account - Optional)
        self.telegram_api_id_2 = self._get_env('TELEGRAM_API_ID_2', cast=int)
        self.telegram_api_hash_2 = self._get_env('TELEGRAM_API_HASH_2')
        self.telegram_phone_2 = self._get_env('TELEGRAM_PHONE_2')
        
        # Gemini AI Configuration
        self.gemini_api_key = self._get_env('GEMINI_API_KEY', required=True)
        
        # Gemini Model Configuration
        self.gemini_model = self._get_env(
            'GEMINI_MODEL', 
            default='gemini-2.0-flash-exp'
        )
        
        # TMDB Configuration
        self.tmdb_api_key = self._get_env('TMDB_API_KEY', required=True)
        
        # Website Configuration
        self.website_url = self._get_env('WEBSITE_URL', default='https://noobz.space')
        
        # Bot Configuration
        self.bot_name = self._get_env('BOT_NAME', default='Noobz Announcement Bot')
        self.debug = self._get_env('DEBUG', default='False', cast=bool)
        
        # Session Configuration
        self.session_name = 'noobz_bot_session'
        self.session_name_2 = 'noobz_bot_session_2'
        
        self._initialized = True
    
    def _get_env(
        self, 
        key: str, 
        default: Optional[str] = None, 
        required: bool = False,
        cast: type = str
    ) -> any:
        """
        Get environment variable dengan validation.
        
        Args:
            key: Environment variable key
            default: Default value jika tidak ditemukan
            required: Raise error jika True dan variable tidak ditemukan
            cast: Type casting untuk value (int, bool, str)
            
        Returns:
            Environment variable value
            
        Raises:
            ValueError: Jika required=True dan variable tidak ditemukan
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(
                f"Environment variable '{key}' is required but not found. "
                f"Please check your .env file."
            )
        
        if value is None:
            return None
        
        # Type casting
        if cast == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif cast == int:
            return int(value)
        elif cast == float:
            return float(value)
        
        return value
    
    def validate(self) -> bool:
        """
        Validate semua required settings.
        
        Returns:
            True jika semua settings valid
            
        Raises:
            ValueError: Jika ada settings yang invalid
        """
        # Validate Telegram settings
        if not isinstance(self.telegram_api_id, int) or self.telegram_api_id <= 0:
            raise ValueError("TELEGRAM_API_ID must be a positive integer")
        
        if not self.telegram_api_hash or len(self.telegram_api_hash) < 10:
            raise ValueError("TELEGRAM_API_HASH is invalid")
        
        if not self.telegram_phone.startswith('+'):
            raise ValueError("TELEGRAM_PHONE must start with country code (e.g., +62)")
        
        # Validate secondary account if provided
        if self.telegram_phone_2:
            if not self.telegram_api_id_2 or not isinstance(self.telegram_api_id_2, int):
                raise ValueError("TELEGRAM_API_ID_2 required when TELEGRAM_PHONE_2 is set")
            if not self.telegram_api_hash_2:
                raise ValueError("TELEGRAM_API_HASH_2 required when TELEGRAM_PHONE_2 is set")
            if not self.telegram_phone_2.startswith('+'):
                raise ValueError("TELEGRAM_PHONE_2 must start with country code (e.g., +62)")
        
        # Validate API keys
        if not self.gemini_api_key or len(self.gemini_api_key) < 10:
            raise ValueError("GEMINI_API_KEY is invalid")
        
        if not self.tmdb_api_key or len(self.tmdb_api_key) < 10:
            raise ValueError("TMDB_API_KEY is invalid")
        
        return True
    
    def has_secondary_account(self) -> bool:
        """
        Check if secondary Telegram account is configured.
        
        Returns:
            True if secondary account is configured
        """
        return bool(
            self.telegram_phone_2 and 
            self.telegram_api_id_2 and 
            self.telegram_api_hash_2
        )
    
    def get_telegram_config(self) -> dict:
        """
        Get Telegram configuration sebagai dictionary.
        
        Returns:
            Dictionary berisi Telegram config
        """
        return {
            'api_id': self.telegram_api_id,
            'api_hash': self.telegram_api_hash,
            'phone': self.telegram_phone,
            'session_name': self.session_name
        }
    
    def get_telegram_config_2(self) -> dict:
        """
        Get secondary Telegram configuration sebagai dictionary.
        
        Returns:
            Dictionary berisi Telegram config untuk account kedua
        """
        if not self.has_secondary_account():
            return None
        
        return {
            'api_id': self.telegram_api_id_2,
            'api_hash': self.telegram_api_hash_2,
            'phone': self.telegram_phone_2,
            'session_name': self.session_name_2
        }
    
    def __repr__(self) -> str:
        """String representation (hide sensitive data)."""
        return (
            f"Settings("
            f"telegram_api_id={self.telegram_api_id}, "
            f"telegram_phone={self.telegram_phone}, "
            f"website_url={self.website_url}, "
            f"debug={self.debug}"
            f")"
        )


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get global settings instance.
    
    Returns:
        Settings instance
    """
    return settings
