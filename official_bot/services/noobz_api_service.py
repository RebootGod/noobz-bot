"""
Module: Noobz API Service (Part 1)
Purpose: HTTP client for Laravel backend API calls

Handles basic content creation:
- Movie upload
- Series creation
- Season creation

For episode operations, see noobz_api_service_2.py

Author: RebootGod
Date: 2025
"""

import logging
from typing import Optional, Dict, Any, List
import aiohttp
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NoobzApiService:
    """
    Service for communicating with Laravel backend API
    
    All endpoints require bot authentication via Bearer token.
    Base URL: https://noobz.space/api/bot
    """

    def __init__(self, settings: Settings):
        """
        Initialize Noobz API service
        
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
        
        logger.info("NoobzApiService initialized")

    async def upload_movie(
        self,
        tmdb_id: int,
        embed_url: str,
        download_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload movie to Laravel backend
        
        Calls: POST /api/bot/movies
        
        Args:
            tmdb_id: TMDB movie ID
            embed_url: Embed URL (e.g., vidsrc.to)
            download_url: Optional download URL
            
        Returns:
            Dict with success status and movie data
            
        Example response:
            {
                'success': True,
                'data': {
                    'movie_id': 123,
                    'title': 'Fight Club',
                    'year': 1999,
                    'slug': 'fight-club-1999',
                    'status': 'published'
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/movies"
            
            payload = {
                'tmdb_id': tmdb_id,
                'embed_url': embed_url
            }
            
            if download_url:
                payload['download_url'] = download_url
            
            logger.info(f"Uploading movie: TMDB ID {tmdb_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 409:
                        logger.warning(f"Movie already exists: {response_data.get('message')}")
                        return {
                            'success': False,
                            'error': 'ALREADY_EXISTS',
                            'message': response_data.get('message', 'Movie already exists')
                        }
                    
                    if response.status != 201:
                        error_msg = response_data.get('message', 'Unknown error')
                        logger.error(f"Failed to upload movie: {error_msg}")
                        return {
                            'success': False,
                            'error': 'UPLOAD_FAILED',
                            'message': error_msg
                        }
                    
                    logger.info(f"Movie uploaded successfully: {response_data.get('data', {}).get('title')}")
                    
                    return {
                        'success': True,
                        'data': response_data.get('data', {})
                    }
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout uploading movie")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception uploading movie: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }

    async def create_series(self, tmdb_id: int) -> Dict[str, Any]:
        """
        Create series in Laravel backend
        
        Calls: POST /api/bot/series
        
        Args:
            tmdb_id: TMDB series ID
            
        Returns:
            Dict with success status and series data
            
        Example response:
            {
                'success': True,
                'data': {
                    'series_id': 456,
                    'title': 'Breaking Bad',
                    'year': 2008,
                    'slug': 'breaking-bad-2008',
                    'number_of_seasons': 5
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/series"
            
            payload = {'tmdb_id': tmdb_id}
            
            logger.info(f"Creating series: TMDB ID {tmdb_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 409:
                        logger.warning(f"Series already exists: {response_data.get('message')}")
                        return {
                            'success': False,
                            'error': 'ALREADY_EXISTS',
                            'message': response_data.get('message', 'Series already exists')
                        }
                    
                    if response.status != 201:
                        error_msg = response_data.get('message', 'Unknown error')
                        logger.error(f"Failed to create series: {error_msg}")
                        return {
                            'success': False,
                            'error': 'CREATE_FAILED',
                            'message': error_msg
                        }
                    
                    logger.info(f"Series created successfully: {response_data.get('data', {}).get('title')}")
                    
                    return {
                        'success': True,
                        'data': response_data.get('data', {})
                    }
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout creating series")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception creating series: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }

    async def create_season(
        self, 
        tmdb_id: int, 
        season_number: int
    ) -> Dict[str, Any]:
        """
        Create season in Laravel backend
        
        Calls: POST /api/bot/series/{tmdb_id}/seasons
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number to create
            
        Returns:
            Dict with success status and season data
            
        Example response:
            {
                'success': True,
                'data': {
                    'season_id': 789,
                    'season_number': 1,
                    'name': 'Season 1',
                    'episode_count': 7
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/series/{tmdb_id}/seasons"
            
            payload = {'season_number': season_number}
            
            logger.info(f"Creating season: Series {tmdb_id}, Season {season_number}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 409:
                        logger.warning(f"Season already exists: {response_data.get('message')}")
                        return {
                            'success': False,
                            'error': 'ALREADY_EXISTS',
                            'message': response_data.get('message', 'Season already exists')
                        }
                    
                    if response.status != 201:
                        error_msg = response_data.get('message', 'Unknown error')
                        logger.error(f"Failed to create season: {error_msg}")
                        return {
                            'success': False,
                            'error': 'CREATE_FAILED',
                            'message': error_msg
                        }
                    
                    logger.info(f"Season created successfully: Season {season_number}")
                    
                    return {
                        'success': True,
                        'data': response_data.get('data', {})
                    }
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout creating season")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception creating season: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }
