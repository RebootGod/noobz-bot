"""
TMDB Fetch Service untuk bot upload commands.
Simplified TMDB fetching untuk validation purposes saja.
"""

import logging
from typing import Optional, Dict, Any
import aiohttp
from config.settings import get_settings

logger = logging.getLogger(__name__)


class TmdbFetchService:
    """
    Lightweight TMDB service untuk fetch basic info.
    Digunakan untuk validate TMDB ID sebelum upload.
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self):
        """Initialize TMDB fetch service."""
        self.settings = get_settings()
        self.api_key = self.settings.tmdb_api_key
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get atau create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make request ke TMDB API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response JSON or None if error
        """
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"TMDB 404: {endpoint}")
                    return None
                else:
                    logger.error(f"TMDB error {response.status}: {endpoint}")
                    return None
        except Exception as e:
            logger.error(f"TMDB request failed: {str(e)}")
            return None
    
    async def check_movie_exists(self, tmdb_id: int) -> tuple[bool, Optional[str]]:
        """
        Check apakah movie dengan TMDB ID ada.
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            Tuple of (exists, title)
        """
        data = await self._make_request(f"/movie/{tmdb_id}")
        if data:
            title = data.get('title', 'Unknown')
            logger.info(f"TMDB movie found: {title} (ID: {tmdb_id})")
            return True, title
        return False, None
    
    async def check_series_exists(self, tmdb_id: int) -> tuple[bool, Optional[str]]:
        """
        Check apakah series dengan TMDB ID ada.
        
        Args:
            tmdb_id: TMDB series ID
            
        Returns:
            Tuple of (exists, title)
        """
        data = await self._make_request(f"/tv/{tmdb_id}")
        if data:
            title = data.get('name', 'Unknown')
            logger.info(f"TMDB series found: {title} (ID: {tmdb_id})")
            return True, title
        return False, None
    
    async def check_season_exists(
        self,
        tmdb_id: int,
        season_number: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check apakah season ada untuk series.
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number
            
        Returns:
            Tuple of (exists, season_name)
        """
        data = await self._make_request(f"/tv/{tmdb_id}/season/{season_number}")
        if data:
            name = data.get('name', f'Season {season_number}')
            logger.info(f"TMDB season found: {name} (Series ID: {tmdb_id})")
            return True, name
        return False, None
    
    async def check_episode_exists(
        self,
        tmdb_id: int,
        season_number: int,
        episode_number: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check apakah episode ada.
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number
            episode_number: Episode number
            
        Returns:
            Tuple of (exists, episode_name)
        """
        endpoint = f"/tv/{tmdb_id}/season/{season_number}/episode/{episode_number}"
        data = await self._make_request(endpoint)
        if data:
            name = data.get('name', f'Episode {episode_number}')
            logger.info(
                f"TMDB episode found: {name} "
                f"(Series ID: {tmdb_id}, S{season_number}E{episode_number})"
            )
            return True, name
        return False, None
    
    async def get_movie_info(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Get basic movie info.
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            Movie data or None
        """
        return await self._make_request(f"/movie/{tmdb_id}")
    
    async def get_series_info(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Get basic series info.
        
        Args:
            tmdb_id: TMDB series ID
            
        Returns:
            Series data or None
        """
        return await self._make_request(f"/tv/{tmdb_id}")


# Singleton instance
_tmdb_fetch_instance = None


def get_tmdb_fetch_service() -> TmdbFetchService:
    """
    Get singleton instance of TmdbFetchService.
    
    Returns:
        TmdbFetchService instance
    """
    global _tmdb_fetch_instance
    if _tmdb_fetch_instance is None:
        _tmdb_fetch_instance = TmdbFetchService()
    return _tmdb_fetch_instance
