"""
TMDB Movie Service - Movie-related operations.
Handles movie search and details fetching.
"""

import logging
from typing import Dict, Any, List, Optional

from services.tmdb_base import TMDBBase

logger = logging.getLogger(__name__)


class TMDBMovie(TMDBBase):
    """
    Service untuk movie-related operations.
    """
    
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
