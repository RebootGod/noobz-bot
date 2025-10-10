"""
TMDB TV Service - TV series-related operations.
Handles TV series search and details fetching.
"""

import logging
from typing import Dict, Any, List, Optional

from services.tmdb_base import TMDBBase

logger = logging.getLogger(__name__)


class TMDBTV(TMDBBase):
    """
    Service untuk TV series-related operations.
    """
    
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
