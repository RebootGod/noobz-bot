"""
TMDB Base Service - Core functionality and helpers.
Handles session management, API requests, and common utilities.
"""

import logging
import re
from typing import Optional, Dict, Any
import aiohttp

from config.settings import get_settings

logger = logging.getLogger(__name__)


class TMDBBase:
    """
    Base class untuk TMDB service.
    Provides session management dan common utilities.
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        """Initialize TMDB base service."""
        self.settings = get_settings()
        self.api_key = self.settings.tmdb_api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get atau create aiohttp session.
        
        Returns:
            aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def _is_non_latin(self, text: str) -> bool:
        """
        Check if text contains non-Latin characters (Korean, Chinese, Japanese, etc.).
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains CJK (Chinese-Japanese-Korean) or other non-Latin characters
        """
        if not text:
            return False
        
        # Unicode ranges for CJK characters
        # Hangul (Korean): \uAC00-\uD7AF
        # Hiragana/Katakana (Japanese): \u3040-\u309F, \u30A0-\u30FF
        # CJK Unified Ideographs (Chinese/Japanese/Korean): \u4E00-\u9FFF
        cjk_pattern = re.compile(r'[\uAC00-\uD7AF\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]')
        
        return bool(cjk_pattern.search(text))
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request ke TMDB API.
        
        Args:
            endpoint: API endpoint (e.g., '/movie/550')
            params: Query parameters
            
        Returns:
            Response JSON sebagai dictionary
            
        Raises:
            Exception: Jika request gagal
        """
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"TMDB API request failed: {e}")
            raise
    
    def get_poster_url(self, poster_path: Optional[str]) -> Optional[str]:
        """
        Get full URL untuk poster image.
        
        Args:
            poster_path: Poster path dari TMDB
            
        Returns:
            Full poster URL atau None
        """
        if not poster_path:
            return None
        return f"{self.IMAGE_BASE_URL}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: Optional[str]) -> Optional[str]:
        """
        Get full URL untuk backdrop image.
        
        Args:
            backdrop_path: Backdrop path dari TMDB
            
        Returns:
            Full backdrop URL atau None
        """
        if not backdrop_path:
            return None
        return f"{self.IMAGE_BASE_URL}{backdrop_path}"
