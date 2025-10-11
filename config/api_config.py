"""
API configuration untuk Noobz API client.
Manage connection settings ke Laravel backend.
"""

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class ApiConfig:
    """
    Configuration untuk API client connection.
    Manage URL, token, dan settings lainnya.
    """
    
    def __init__(self):
        """Initialize API configuration dari environment variables."""
        # Noobz API Base URL
        self.api_base_url = os.getenv(
            'NOOBZ_API_URL', 
            'https://noobz.space'
        ).rstrip('/')
        
        # API Bearer Token
        self.api_token = os.getenv('NOOBZ_BOT_TOKEN', '')
        if not self.api_token:
            raise ValueError(
                "NOOBZ_BOT_TOKEN is required in .env file. "
                "This token must match TELEGRAM_BOT_TOKEN in Laravel .env"
            )
        
        # API Endpoints
        self.endpoint_movies = f"{self.api_base_url}/api/bot/movies"
        self.endpoint_series = f"{self.api_base_url}/api/bot/series"
        self.endpoint_seasons = f"{self.api_base_url}/api/bot/series/{{tmdb_id}}/seasons"
        self.endpoint_episodes = f"{self.api_base_url}/api/bot/series/{{tmdb_id}}/episodes"
        
        # Request Configuration
        self.request_timeout = int(os.getenv('API_REQUEST_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('API_MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('API_RETRY_DELAY', '5'))
        
        # Debug Mode
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    def get_headers(self) -> dict:
        """
        Get HTTP headers untuk API requests.
        
        Returns:
            Dictionary of HTTP headers
        """
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'NoobzBot/1.0',
        }
    
    def get_season_endpoint(self, tmdb_id: int) -> str:
        """
        Get endpoint URL untuk season upload.
        
        Args:
            tmdb_id: TMDB ID dari series
            
        Returns:
            Full endpoint URL
        """
        return self.endpoint_seasons.format(tmdb_id=tmdb_id)
    
    def get_episode_endpoint(self, tmdb_id: int) -> str:
        """
        Get endpoint URL untuk episode upload.
        
        Args:
            tmdb_id: TMDB ID dari series
            
        Returns:
            Full endpoint URL
        """
        return self.endpoint_episodes.format(tmdb_id=tmdb_id)
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """
        Validate API configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.api_token:
            return False, "API token is missing"
        
        if not self.api_base_url:
            return False, "API base URL is missing"
        
        if self.request_timeout <= 0:
            return False, "Request timeout must be positive"
        
        if self.max_retries < 0:
            return False, "Max retries must be non-negative"
        
        return True, None


# Singleton instance
_api_config_instance = None


def get_api_config() -> ApiConfig:
    """
    Get singleton instance of ApiConfig.
    
    Returns:
        ApiConfig instance
        
    Raises:
        ValueError: Jika configuration invalid
    """
    global _api_config_instance
    if _api_config_instance is None:
        _api_config_instance = ApiConfig()
        
        # Validate configuration
        is_valid, error = _api_config_instance.validate_config()
        if not is_valid:
            raise ValueError(f"Invalid API configuration: {error}")
    
    return _api_config_instance
