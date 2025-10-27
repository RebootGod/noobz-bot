"""
Module: TMDB Service
Purpose: Fetch TMDB data via Noobz Laravel API

This service calls Laravel's TMDB endpoints which use the existing
TmdbDataService.php. Avoids code duplication and maintains single
source of truth for TMDB data processing.

Author: RebootGod
Date: 2025
"""

import logging
from typing import Optional, Dict, Any, List
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TmdbService:
    """
    Service for fetching TMDB data via Laravel API
    
    Calls Laravel's /api/bot/tmdb/* endpoints which use
    existing TmdbDataService.php for data fetching.
    """

    def __init__(self, settings: Settings):
        """
        Initialize TMDB service
        
        Args:
            settings: Application settings with API configuration
        """
        self.settings = settings
        self.api_url = settings.NOOBZ_API_URL
        self.api_token = settings.NOOBZ_BOT_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        logger.info("TmdbService initialized (using Laravel API)")

    async def get_movie(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Get movie details from TMDB via Laravel API
        
        Calls: GET /api/bot/tmdb/movie/{tmdb_id}
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            Dict with movie data or None if failed
            
        Example response:
            {
                'tmdb_id': 550,
                'imdb_id': 'tt0137523',
                'title': 'Fight Club',
                'original_title': 'Fight Club',
                'overview': 'A ticking-time-bomb...',
                'release_date': '1999-10-15',
                'year': 1999,
                'runtime': 139,
                'vote_average': 8.4,
                'genres': [{'id': 18, 'name': 'Drama'}],
                'poster_url': 'https://image.tmdb.org/...',
                'backdrop_url': 'https://image.tmdb.org/...'
            }
        """
        try:
            import aiohttp
            
            url = f"{self.api_url}/api/bot/tmdb/movie/{tmdb_id}"
            
            logger.info(f"Fetching movie data: TMDB ID {tmdb_id}")
            logger.info(f"Request URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 404:
                        logger.warning(f"Movie not found: TMDB ID {tmdb_id}")
                        return None
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to fetch movie data: Status {response.status}, Response: {error_text}")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('success'):
                        logger.error(f"API returned error: {data.get('error', {}).get('message')}")
                        return None
                    
                    movie_data = data.get('data', {})
                    logger.info(f"Movie fetched: {movie_data.get('title')} ({movie_data.get('year')})")
                    
                    return movie_data
        
        except Exception as e:
            logger.error(f"Exception fetching movie data: {str(e)}", exc_info=True)
            return None

    async def get_series(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Get series details from TMDB via Laravel API
        
        Calls: GET /api/bot/tmdb/series/{tmdb_id}
        
        Args:
            tmdb_id: TMDB series ID
            
        Returns:
            Dict with series data or None if failed
            
        Example response:
            {
                'tmdb_id': 1396,
                'imdb_id': 'tt0903747',
                'title': 'Breaking Bad',
                'original_title': 'Breaking Bad',
                'overview': 'A high school chemistry teacher...',
                'first_air_date': '2008-01-20',
                'last_air_date': '2013-09-29',
                'year': 2008,
                'number_of_seasons': 5,
                'number_of_episodes': 62,
                'vote_average': 8.9,
                'genres': [{'id': 18, 'name': 'Drama'}],
                'seasons': [...],
                'poster_url': 'https://image.tmdb.org/...',
                'backdrop_url': 'https://image.tmdb.org/...'
            }
        """
        try:
            import aiohttp
            
            url = f"{self.api_url}/api/bot/tmdb/series/{tmdb_id}"
            
            logger.info(f"Fetching series data: TMDB ID {tmdb_id}")
            logger.info(f"Request URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 404:
                        logger.warning(f"Series not found: TMDB ID {tmdb_id}")
                        return None
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to fetch series data: Status {response.status}, Response: {error_text}")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('success'):
                        logger.error(f"API returned error: {data.get('error', {}).get('message')}")
                        return None
                    
                    series_data = data.get('data', {})
                    logger.info(f"Series fetched: {series_data.get('title')} ({series_data.get('year')}) - {series_data.get('number_of_seasons')} seasons")
                    
                    return series_data
        
        except Exception as e:
            logger.error(f"Exception fetching series data: {str(e)}", exc_info=True)
            return None

    async def get_season(
        self, 
        tmdb_id: int, 
        season_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get season details from TMDB via Laravel API
        
        Calls: GET /api/bot/tmdb/series/{tmdb_id}/season/{season_number}
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number (1-based)
            
        Returns:
            Dict with season data including episodes list or None if failed
            
        Example response:
            {
                'tmdb_id': 1396,
                'season_id': 3572,
                'season_number': 1,
                'name': 'Season 1',
                'overview': 'The first season...',
                'air_date': '2008-01-20',
                'episode_count': 7,
                'poster_url': 'https://image.tmdb.org/...',
                'episodes': [
                    {
                        'episode_number': 1,
                        'name': 'Pilot',
                        'overview': 'Walter White...',
                        'air_date': '2008-01-20',
                        'runtime': 58,
                        'still_path': '/...',
                        'vote_average': 8.0
                    },
                    ...
                ]
            }
        """
        try:
            import aiohttp
            
            url = f"{self.api_url}/api/bot/tmdb/series/{tmdb_id}/season/{season_number}"
            
            logger.info(f"Fetching season data: TMDB ID {tmdb_id}, Season {season_number}")
            logger.info(f"Request URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 404:
                        logger.warning(f"Season not found: TMDB ID {tmdb_id}, Season {season_number}")
                        return None
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to fetch season data: Status {response.status}, Response: {error_text}")
                        return None
                    
                    data = await response.json()
                    
                    if not data.get('success'):
                        logger.error(f"API returned error: {data.get('error', {}).get('message')}")
                        return None
                    
                    season_data = data.get('data', {})
                    episode_count = len(season_data.get('episodes', []))
                    logger.info(f"Season fetched: {season_data.get('name')} - {episode_count} episodes")
                    
                    return season_data
        
        except Exception as e:
            logger.error(f"Exception fetching season data: {str(e)}", exc_info=True)
            return None

    def get_episode_list(self, season_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract episode list from season data
        
        Args:
            season_data: Season data from get_season()
            
        Returns:
            List of episode dictionaries
        """
        return season_data.get('episodes', [])

    def format_movie_info(self, movie_data: Dict[str, Any]) -> str:
        """
        Format movie data into readable text
        
        Args:
            movie_data: Movie data from get_movie()
            
        Returns:
            Formatted string with movie information
        """
        title = movie_data.get('title', 'Unknown')
        year = movie_data.get('year', 'N/A')
        runtime = movie_data.get('runtime')
        rating = movie_data.get('vote_average', 0)
        overview = movie_data.get('overview', 'No overview available')
        
        runtime_str = f"{runtime} min" if runtime else "N/A"
        
        genres = movie_data.get('genres', [])
        genre_names = [g['name'] for g in genres] if genres else []
        genres_str = ', '.join(genre_names) if genre_names else 'N/A'
        
        info = f"🎬 **{title}** ({year})\n\n"
        info += f"⭐ Rating: {rating}/10\n"
        info += f"⏱️ Runtime: {runtime_str}\n"
        info += f"🎭 Genres: {genres_str}\n\n"
        info += f"📝 {overview}"
        
        return info

    def format_series_info(self, series_data: Dict[str, Any]) -> str:
        """
        Format series data into readable text
        
        Args:
            series_data: Series data from get_series()
            
        Returns:
            Formatted string with series information
        """
        title = series_data.get('title', 'Unknown')
        year = series_data.get('year', 'N/A')
        seasons = series_data.get('number_of_seasons', 0)
        episodes = series_data.get('number_of_episodes', 0)
        rating = series_data.get('vote_average', 0)
        overview = series_data.get('overview', 'No overview available')
        status = series_data.get('status', 'Unknown')
        
        genres = series_data.get('genres', [])
        genre_names = [g['name'] for g in genres] if genres else []
        genres_str = ', '.join(genre_names) if genre_names else 'N/A'
        
        info = f"📺 **{title}** ({year})\n\n"
        info += f"⭐ Rating: {rating}/10\n"
        info += f"📊 Status: {status}\n"
        info += f"🎬 {seasons} seasons, {episodes} episodes\n"
        info += f"🎭 Genres: {genres_str}\n\n"
        info += f"📝 {overview}"
        
        return info
