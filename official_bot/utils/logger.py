"""
Logging Configuration
Setup colored logging for the bot
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import settings

try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


class BotLogger:
    """Bot logging manager"""
    
    def __init__(self):
        self.logger = None
        self.log_file = settings.LOG_FILE
        self.log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    def setup(self):
        """Setup logging configuration"""
        # Create logger
        self.logger = logging.getLogger('official_bot')
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        self._setup_file_handler(file_formatter)
        
        # Console handler
        self._setup_console_handler()
        
        return self.logger
    
    def _setup_file_handler(self, formatter):
        """Setup file handler"""
        try:
            # Create logs directory if not exists
            log_dir = self.log_file.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create file handler
            file_handler = logging.FileHandler(
                self.log_file,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
    
    def _setup_console_handler(self):
        """Setup console handler with colors"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        if HAS_COLORLOG:
            # Colored console output
            color_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s | %(levelname)-8s%(reset)s | %(name)s | %(message)s',
                datefmt='%H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(color_formatter)
        else:
            # Simple console output
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """Get logger instance"""
        if self.logger is None:
            self.setup()
        return self.logger


# Create global logger instance
_bot_logger = BotLogger()
logger = _bot_logger.get_logger()


# Convenience functions
def debug(message: str):
    """Log debug message"""
    logger.debug(message)


def info(message: str):
    """Log info message"""
    logger.info(message)


def warning(message: str):
    """Log warning message"""
    logger.warning(message)


def error(message: str):
    """Log error message"""
    logger.error(message)


def critical(message: str):
    """Log critical message"""
    logger.critical(message)


def log_upload(user_id: int, upload_type: str, title: str, success: bool = True):
    """
    Log upload activity
    
    Args:
        user_id: Telegram user ID
        upload_type: Type of upload (movie, series, episode)
        title: Content title
        success: Whether upload was successful
    """
    status = "✅ SUCCESS" if success else "❌ FAILED"
    logger.info(f"{status} | User {user_id} | {upload_type} | {title}")


def log_auth(user_id: int, username: str, is_master: bool = False):
    """
    Log authentication
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        is_master: Whether user is master
    """
    role = "MASTER" if is_master else "ADMIN"
    logger.info(f"🔐 AUTH | User {user_id} (@{username}) | {role}")


def log_error(context: str, error: Exception):
    """
    Log error with context
    
    Args:
        context: Error context (e.g., "movie_upload", "tmdb_fetch")
        error: Exception object
    """
    logger.error(f"❌ ERROR | {context} | {type(error).__name__}: {str(error)}")


def log_api_call(method: str, url: str, status_code: int):
    """
    Log API call
    
    Args:
        method: HTTP method (GET, POST, PUT)
        url: API URL
        status_code: Response status code
    """
    logger.debug(f"🌐 API | {method} {url} | Status: {status_code}")


# Initialize logger on import
logger.info("🤖 Official Bot Logger Initialized")
