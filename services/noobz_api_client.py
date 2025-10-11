"""
Noobz API Client untuk komunikasi dengan Laravel backend.
Handle HTTP requests ke bot upload API endpoints.
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any
from config.api_config import get_api_config

logger = logging.getLogger(__name__)


class NoobzApiClient:
    """
    Async HTTP client untuk Noobz API.
    Handle upload requests ke Laravel backend.
    """
    
    def __init__(self):
        """Initialize API client with configuration."""
        self.config = get_api_config()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.config.get_headers(),
                timeout=aiohttp.ClientTimeout(total=self.config.request_timeout)
            )
    
    async def close(self):
        """Close aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def _make_request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Make HTTP request dengan retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc)
            url: Target URL
            json_data: JSON payload
            retry_count: Current retry attempt
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        await self._ensure_session()
        
        try:
            async with self.session.request(
                method,
                url,
                json=json_data
            ) as response:
                response_json = await response.json()
                
                if response.status in [200, 202]:
                    logger.info(f"API request successful: {method} {url}")
                    return True, response_json, None
                elif response.status == 404:
                    error_msg = response_json.get('message', 'Resource not found')
                    logger.warning(f"API 404: {error_msg}")
                    return False, response_json, error_msg
                elif response.status == 401:
                    error_msg = "Unauthorized - Invalid bot token"
                    logger.error(f"API 401: {error_msg}")
                    return False, None, error_msg
                elif response.status == 422:
                    # Validation error
                    errors = response_json.get('errors', {})
                    error_msg = response_json.get('message', 'Validation failed')
                    logger.warning(f"API validation error: {error_msg}")
                    return False, response_json, error_msg
                else:
                    error_msg = response_json.get('message', f'HTTP {response.status}')
                    logger.error(f"API error {response.status}: {error_msg}")
                    
                    # Retry on server errors (5xx)
                    if response.status >= 500 and retry_count < self.config.max_retries:
                        await asyncio.sleep(self.config.retry_delay)
                        return await self._make_request(
                            method, url, json_data, retry_count + 1
                        )
                    
                    return False, response_json, error_msg
                    
        except asyncio.TimeoutError:
            error_msg = f"Request timeout after {self.config.request_timeout}s"
            logger.error(f"API timeout: {error_msg}")
            
            if retry_count < self.config.max_retries:
                await asyncio.sleep(self.config.retry_delay)
                return await self._make_request(
                    method, url, json_data, retry_count + 1
                )
            
            return False, None, error_msg
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(f"API client error: {error_msg}")
            
            if retry_count < self.config.max_retries:
                await asyncio.sleep(self.config.retry_delay)
                return await self._make_request(
                    method, url, json_data, retry_count + 1
                )
            
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"API unexpected error: {error_msg}", exc_info=True)
            return False, None, error_msg
    
    async def upload_movie(
        self,
        tmdb_id: int,
        embed_url: str,
        download_url: Optional[str],
        telegram_username: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Upload movie ke Noobz API.
        
        Args:
            tmdb_id: TMDB ID dari movie
            embed_url: URL untuk embed player
            download_url: URL untuk download (optional)
            telegram_username: Telegram username uploader
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        payload = {
            'tmdb_id': tmdb_id,
            'embed_url': embed_url,
            'telegram_username': telegram_username
        }
        
        if download_url:
            payload['download_url'] = download_url
        
        logger.info(f"Uploading movie TMDB ID {tmdb_id}")
        return await self._make_request(
            'POST',
            self.config.endpoint_movies,
            payload
        )
    
    async def upload_series(
        self,
        tmdb_id: int,
        telegram_username: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Upload series ke Noobz API.
        
        Args:
            tmdb_id: TMDB ID dari series
            telegram_username: Telegram username uploader
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        payload = {
            'tmdb_id': tmdb_id,
            'telegram_username': telegram_username
        }
        
        logger.info(f"Uploading series TMDB ID {tmdb_id}")
        return await self._make_request(
            'POST',
            self.config.endpoint_series,
            payload
        )
    
    async def upload_season(
        self,
        tmdb_id: int,
        season_number: int,
        telegram_username: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Upload season ke Noobz API.
        
        Args:
            tmdb_id: TMDB ID dari series
            season_number: Nomor season
            telegram_username: Telegram username uploader
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        payload = {
            'tmdb_id': tmdb_id,
            'season_number': season_number,
            'telegram_username': telegram_username
        }
        
        endpoint = self.config.get_season_endpoint(tmdb_id)
        logger.info(f"Uploading season {season_number} for series TMDB ID {tmdb_id}")
        return await self._make_request('POST', endpoint, payload)
    
    async def upload_episode(
        self,
        tmdb_id: int,
        season_number: int,
        episode_number: int,
        embed_url: str,
        download_url: Optional[str],
        telegram_username: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Upload episode ke Noobz API.
        
        Args:
            tmdb_id: TMDB ID dari series
            season_number: Nomor season
            episode_number: Nomor episode
            embed_url: URL untuk embed player
            download_url: URL untuk download (optional)
            telegram_username: Telegram username uploader
            
        Returns:
            Tuple of (success, response_data, error_message)
        """
        payload = {
            'tmdb_id': tmdb_id,
            'season_number': season_number,
            'episode_number': episode_number,
            'embed_url': embed_url,
            'telegram_username': telegram_username
        }
        
        if download_url:
            payload['download_url'] = download_url
        
        endpoint = self.config.get_episode_endpoint(tmdb_id)
        logger.info(
            f"Uploading episode S{season_number}E{episode_number} "
            f"for series TMDB ID {tmdb_id}"
        )
        return await self._make_request('POST', endpoint, payload)


# Singleton instance
_api_client_instance = None


def get_api_client() -> NoobzApiClient:
    """
    Get singleton instance of NoobzApiClient.
    
    Returns:
        NoobzApiClient instance
    """
    global _api_client_instance
    if _api_client_instance is None:
        _api_client_instance = NoobzApiClient()
    return _api_client_instance
