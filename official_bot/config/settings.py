"""
Official Bot Settings
Loads configuration from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Noobz API Configuration
    NOOBZ_API_URL = os.getenv('NOOBZ_API_URL', 'https://noobz.space')
    NOOBZ_BOT_TOKEN = os.getenv('NOOBZ_BOT_TOKEN')
    
    # TMDB Configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    
    # Database Configuration
    DATABASE_PATH = Path(__file__).parent.parent / os.getenv('DATABASE_PATH', 'bot_secure.db')
    
    # Security Configuration
    SESSION_EXPIRY_HOURS = int(os.getenv('SESSION_EXPIRY_HOURS', '24'))
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    BCRYPT_ROUNDS = 12  # Cost factor for bcrypt
    
    # Bulk Upload Configuration
    MAX_BULK_EPISODES = int(os.getenv('MAX_BULK_EPISODES', '20'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = Path(__file__).parent.parent / os.getenv('LOG_FILE', 'bot.log')
    
    # Development
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        required = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('NOOBZ_BOT_TOKEN', cls.NOOBZ_BOT_TOKEN),
            ('TMDB_API_KEY', cls.TMDB_API_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please check your .env file."
            )
    
    @classmethod
    def get_api_headers(cls):
        """Get headers for Noobz API requests"""
        return {
            'Authorization': f'Bearer {cls.NOOBZ_BOT_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }


# Create settings instance
settings = Settings()


def init_settings():
    """Initialize and validate settings"""
    try:
        settings.validate()
        return True
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return False
