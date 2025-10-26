"""
Module: Noobz API Service (Part 2)
Purpose: HTTP client for episode operations

Handles episode-specific operations:
- Episode creation
- Episode status checking
- Episode URL updates
- Bulk episode processing

Continuation from noobz_api_service.py

Author: RebootGod
Date: 2025
"""

import logging
from typing import Optional, Dict, Any, List
import aiohttp
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NoobzApiServiceEpisodes:
    """
    Service for episode-related API operations
    
    Extends NoobzApiService with episode management features.
    """

    def __init__(self, settings: Settings):
        """
        Initialize episode API service
        
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
        
        logger.info("NoobzApiServiceEpisodes initialized")

    async def create_episode(
        self,
        tmdb_id: int,
        season_number: int,
        episode_number: int,
        embed_url: str,
        download_url: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create episode in Laravel backend
        
        Calls: POST /api/bot/series/{tmdb_id}/episodes
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number
            episode_number: Episode number
            embed_url: Embed URL (e.g., vidsrc.to)
            download_url: Optional download URL
            title: Optional episode title (for manual mode)
            
        Returns:
            Dict with success status and episode data
            
        Example response:
            {
                'success': True,
                'data': {
                    'episode_id': 101,
                    'episode_number': 2,
                    'title': 'Cat\'s in the Bag...',
                    'status': 'published'
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/series/{tmdb_id}/episodes"
            
            payload = {
                'season_number': season_number,
                'episode_number': episode_number,
                'embed_url': embed_url
            }
            
            if download_url:
                payload['download_url'] = download_url
            
            if title:
                payload['title'] = title
            
            logger.info(f"Creating episode: S{season_number:02d}E{episode_number:02d}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    response_data = await response.json()
                    
                    # DEBUG: Log raw response from Laravel
                    logger.info(f"🔍 RAW API Response (Episode) - Status: {response.status}, Data: {response_data}")
                    
                    if response.status == 409:
                        logger.warning(f"Episode already exists: {response_data.get('message')}")
                        return {
                            'success': False,
                            'error': 'ALREADY_EXISTS',
                            'message': response_data.get('message', 'Episode already exists')
                        }
                    
                    # Accept both 200 and 201 as success
                    if response.status not in [200, 201]:
                        error_msg = response_data.get('message', 'Unknown error')
                        logger.error(f"Failed to create episode: {error_msg}")
                        return {
                            'success': False,
                            'error': 'CREATE_FAILED',
                            'message': error_msg
                        }
                    
                    logger.info(f"Episode created successfully: E{episode_number:02d}")
                    
                    return {
                        'success': True,
                        'data': response_data.get('data', {}),
                        'message': response_data.get('message', 'Episode created successfully')
                    }
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout creating episode")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception creating episode: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }

    async def get_episodes_status(
        self,
        tmdb_id: int,
        season_number: int
    ) -> Dict[str, Any]:
        """
        Get episode status for a season
        
        Calls: GET /api/bot/series/{tmdb_id}/episodes-status?season={season_number}
        
        Args:
            tmdb_id: TMDB series ID
            season_number: Season number to check
            
        Returns:
            Dict with episode status information
            
        Example response:
            {
                'success': True,
                'tmdb_data_available': True,
                'data': {
                    'series': {...},
                    'season': {...},
                    'episodes': [
                        {
                            'episode_number': 1,
                            'title': 'Pilot',
                            'exists': True,
                            'complete': True,
                            'needs_update': False
                        },
                        {
                            'episode_number': 2,
                            'title': 'Cat\'s in the Bag...',
                            'exists': True,
                            'complete': False,
                            'needs_update': True,
                            'episode_id': 790
                        },
                        ...
                    ]
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/series/{tmdb_id}/episodes-status"
            params = {'season': season_number}
            
            logger.info(f"Checking episode status: Series {tmdb_id}, Season {season_number}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    params=params,
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    if response.status == 404:
                        logger.warning(f"Series or season not found: {tmdb_id}/S{season_number}")
                        return {
                            'success': False,
                            'error': 'NOT_FOUND',
                            'message': 'Series or season not found'
                        }
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to get episode status: Status {response.status}")
                        return {
                            'success': False,
                            'error': 'REQUEST_FAILED',
                            'message': f"Status {response.status}"
                        }
                    
                    response_data = await response.json()
                    
                    if not response_data.get('success'):
                        logger.error(f"API returned error: {response_data.get('message')}")
                        return response_data
                    
                    episodes = response_data.get('data', {}).get('episodes', [])
                    complete = len([e for e in episodes if e.get('complete')])
                    total = len(episodes)
                    
                    logger.info(f"Episode status retrieved: {complete}/{total} complete")
                    
                    return response_data
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout getting episode status")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception getting episode status: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }

    async def update_episode_urls(
        self,
        episode_id: int,
        embed_url: str,
        download_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update episode URLs
        
        Calls: PUT /api/bot/episodes/{episode_id}
        
        Args:
            episode_id: Episode ID from database
            embed_url: New embed URL
            download_url: Optional download URL
            
        Returns:
            Dict with success status
            
        Example response:
            {
                'success': True,
                'message': 'Episode URLs updated successfully',
                'data': {
                    'episode_id': 790,
                    'episode_number': 2,
                    'title': 'Cat\'s in the Bag...',
                    'embed_url': 'https://vidsrc.to/...',
                    'status': 'published'
                }
            }
        """
        try:
            url = f"{self.api_url}/bot/episodes/{episode_id}"
            
            payload = {'embed_url': embed_url}
            
            if download_url:
                payload['download_url'] = download_url
            
            logger.info(f"Updating episode URLs: Episode ID {episode_id}")
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url, 
                    json=payload, 
                    headers=self.headers, 
                    timeout=30
                ) as response:
                    
                    response_data = await response.json()
                    
                    if response.status == 409:
                        logger.warning(f"Episode already has URLs: {response_data.get('message')}")
                        return {
                            'success': False,
                            'error': 'ALREADY_HAS_URLS',
                            'message': response_data.get('message', 'Episode already has URLs')
                        }
                    
                    if response.status == 404:
                        logger.error(f"Episode not found: ID {episode_id}")
                        return {
                            'success': False,
                            'error': 'NOT_FOUND',
                            'message': 'Episode not found'
                        }
                    
                    if response.status != 200:
                        error_msg = response_data.get('message', 'Unknown error')
                        logger.error(f"Failed to update episode: {error_msg}")
                        return {
                            'success': False,
                            'error': 'UPDATE_FAILED',
                            'message': error_msg
                        }
                    
                    logger.info(f"Episode URLs updated successfully: ID {episode_id}")
                    
                    return {
                        'success': True,
                        'data': response_data.get('data', {})
                    }
        
        except aiohttp.ClientTimeout:
            logger.error("Request timeout updating episode")
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': 'Request timeout'
            }
        except Exception as e:
            logger.error(f"Exception updating episode: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'EXCEPTION',
                'message': str(e)
            }

    async def bulk_create_episodes(
        self,
        episodes_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple episodes (sequential processing)
        
        Args:
            episodes_data: List of episode data dicts with keys:
                - tmdb_id: Series TMDB ID
                - season_number: Season number
                - episode_number: Episode number
                - embed_url: Embed URL
                - download_url: Optional download URL
                - title: Optional episode title
                
        Returns:
            Dict with bulk operation results
            
        Example response:
            {
                'success': True,
                'total': 5,
                'succeeded': 4,
                'failed': 1,
                'results': [
                    {'episode_number': 2, 'success': True, ...},
                    {'episode_number': 3, 'success': True, ...},
                    ...
                ]
            }
        """
        results = []
        succeeded = 0
        failed = 0
        
        for episode_data in episodes_data:
            result = await self.create_episode(
                tmdb_id=episode_data['tmdb_id'],
                season_number=episode_data['season_number'],
                episode_number=episode_data['episode_number'],
                embed_url=episode_data['embed_url'],
                download_url=episode_data.get('download_url'),
                title=episode_data.get('title')
            )
            
            if result['success']:
                succeeded += 1
            else:
                failed += 1
            
            results.append({
                'episode_number': episode_data['episode_number'],
                'success': result['success'],
                'data': result.get('data'),
                'error': result.get('error'),
                'message': result.get('message')
            })
        
        logger.info(f"Bulk episode creation complete: {succeeded}/{len(episodes_data)} succeeded")
        
        return {
            'success': True,
            'total': len(episodes_data),
            'succeeded': succeeded,
            'failed': failed,
            'results': results
        }
