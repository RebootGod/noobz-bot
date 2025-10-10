"""
TMDB Service untuk fetch movie/series data.
Handle API calls ke The Movie Database (TMDB).
"""

import logging
import re
from typing import Optional, Dict, Any, List
import aiohttp

from config.settings import get_settings

logger = logging.getLogger(__name__)


class TMDBService:
    """
    Service untuk interact dengan TMDB API.
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        """Initialize TMDB service."""
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
    
    async def get_movie_by_id(self, movie_id: int) -> Dict[str, Any]:
        """
        Get movie details by TMDB ID with Indonesian language priority.
        
        Args:
            movie_id: TMDB movie ID
            
        Returns:
            Dictionary berisi movie details (Indonesian if available, English fallback)
            
        Raises:
            Exception: Jika movie tidak ditemukan atau request gagal
        """
        try:
            endpoint = f"/movie/{movie_id}"
            
            # Try Indonesian first
            params_id = {'language': 'id-ID'}
            movie_data_id = await self._make_request(endpoint, params_id)
            
            # Get English version for fallback
            params_en = {'language': 'en-US'}
            movie_data_en = await self._make_request(endpoint, params_en)
            
            # Merge: Use Indonesian if available, fallback to English
            movie_data = movie_data_id.copy()
            
            # Fallback overview to English if Indonesian is empty
            if not movie_data.get('overview') or movie_data.get('overview').strip() == '':
                movie_data['overview'] = movie_data_en.get('overview', '')
            
            # Fallback title to English if Indonesian version has non-Latin characters
            # (Korean, Chinese, Japanese, etc.) or is empty
            title_id = movie_data.get('title', '')
            if not title_id or self._is_non_latin(title_id):
                movie_data['title'] = movie_data_en.get('title', 'Unknown')
                logger.info(f"Using English title instead of: {title_id}")
            
            # Fallback runtime to English version if not available in Indonesian
            if not movie_data.get('runtime'):
                movie_data['runtime'] = movie_data_en.get('runtime')
                if movie_data.get('runtime'):
                    logger.info(f"Using English runtime: {movie_data['runtime']} minutes")
            
            logger.info(f"Successfully fetched movie: {movie_data.get('title')}")
            return movie_data
        except Exception as e:
            logger.error(f"Failed to fetch movie {movie_id}: {e}")
            raise
    
    async def get_tv_by_id(self, tv_id: int) -> Dict[str, Any]:
        """
        Get TV series details by TMDB ID with Indonesian language priority.
        
        Args:
            tv_id: TMDB TV series ID
            
        Returns:
            Dictionary berisi TV series details (Indonesian if available, English fallback)
            
        Raises:
            Exception: Jika series tidak ditemukan atau request gagal
        """
        try:
            endpoint = f"/tv/{tv_id}"
            
            # Try Indonesian first
            params_id = {'language': 'id-ID'}
            tv_data_id = await self._make_request(endpoint, params_id)
            
            # Get English version for fallback
            params_en = {'language': 'en-US'}
            tv_data_en = await self._make_request(endpoint, params_en)
            
            # Merge: Use Indonesian if available, fallback to English
            tv_data = tv_data_id.copy()
            
            # Fallback overview to English if Indonesian is empty
            if not tv_data.get('overview') or tv_data.get('overview').strip() == '':
                tv_data['overview'] = tv_data_en.get('overview', '')
            
            # Fallback name to English if Indonesian version has non-Latin characters
            # (Korean, Chinese, Japanese, etc.) or is empty
            name_id = tv_data.get('name', '')
            if not name_id or self._is_non_latin(name_id):
                tv_data['name'] = tv_data_en.get('name', 'Unknown')
                logger.info(f"Using English name instead of: {name_id}")
            
            # Fallback episode_run_time to English version if not available in Indonesian
            if not tv_data.get('episode_run_time'):
                tv_data['episode_run_time'] = tv_data_en.get('episode_run_time')
                if tv_data.get('episode_run_time'):
                    logger.info(f"Using English episode_run_time: {tv_data['episode_run_time']}")
            
            logger.info(f"Successfully fetched TV series: {tv_data.get('name')}")
            return tv_data
        except Exception as e:
            logger.error(f"Failed to fetch TV series {tv_id}: {e}")
            raise
    
    async def search_movie(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search movies by title.
        
        Args:
            query: Search query (movie title)
            year: Release year (optional, untuk filter)
            
        Returns:
            List of movie dictionaries
            
        Raises:
            Exception: Jika search gagal
        """
        try:
            params = {
                'query': query,
                'language': 'id-ID'
            }
            
            if year:
                params['year'] = year
            
            endpoint = "/search/movie"
            result = await self._make_request(endpoint, params)
            
            movies = result.get('results', [])
            logger.info(f"Found {len(movies)} movies for query: {query}")
            return movies
            
        except Exception as e:
            logger.error(f"Failed to search movie '{query}': {e}")
            raise
    
    async def search_tv(self, query: str, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search TV series by title.
        
        Args:
            query: Search query (series title)
            year: First air date year (optional, untuk filter)
            
        Returns:
            List of TV series dictionaries
            
        Raises:
            Exception: Jika search gagal
        """
        try:
            params = {
                'query': query,
                'language': 'id-ID'
            }
            
            if year:
                params['first_air_date_year'] = year
            
            endpoint = "/search/tv"
            result = await self._make_request(endpoint, params)
            
            tv_shows = result.get('results', [])
            logger.info(f"Found {len(tv_shows)} TV series for query: {query}")
            return tv_shows
            
        except Exception as e:
            logger.error(f"Failed to search TV series '{query}': {e}")
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


# Global instance
_tmdb_service: Optional[TMDBService] = None


def get_tmdb_service() -> TMDBService:
    """
    Get global TMDBService instance.
    
    Returns:
        TMDBService instance
    """
    global _tmdb_service
    if _tmdb_service is None:
        _tmdb_service = TMDBService()
    return _tmdb_service
