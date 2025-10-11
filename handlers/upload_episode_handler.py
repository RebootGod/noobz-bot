"""
Handler untuk /uploadepisode command.
Upload episode ke Noobz API via bot.
"""

import logging
from typing import Dict, Any
from config.auth_config import get_auth_config
from services.noobz_api_client import get_api_client
from services.upload_validator import UploadValidator
from services.tmdb_fetch_service import get_tmdb_fetch_service
from utils.upload_parser import UploadParser
from utils.upload_formatter import UploadFormatter

logger = logging.getLogger(__name__)


class UploadEpisodeHandler:
    """Handler untuk upload episode command."""
    
    def __init__(self, client):
        """
        Initialize upload episode handler.
        
        Args:
            client: Telethon client instance
        """
        self.client = client
        self.auth_config = get_auth_config()
        self.api_client = get_api_client()
        self.tmdb_service = get_tmdb_fetch_service()
    
    async def handle(self, parsed_command) -> Dict[str, Any]:
        """
        Handle /uploadepisode command.
        
        Args:
            parsed_command: Parsed command object
            
        Returns:
            Dict dengan success status dan message
        """
        try:
            user_id = getattr(parsed_command, 'user_id', None)
            username = getattr(parsed_command, 'username', 'unknown')
            message_text = getattr(parsed_command, 'message', '')
            
            # Check authorization
            if not self.auth_config.is_authorized(user_id):
                logger.warning(f"Unauthorized upload attempt by user {user_id}")
                return {
                    'success': False,
                    'message': UploadFormatter.format_unauthorized()
                }
            
            # Parse message
            success, parsed_data, error = UploadParser.parse_episode_upload(message_text)
            if not success:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            tmdb_id = parsed_data['tmdb_id']
            season_number = parsed_data['season_number']
            episode_number = parsed_data['episode_number']
            embed_url = parsed_data['embed_url']
            download_url = parsed_data.get('download_url')
            
            # Validate data
            is_valid, error = UploadValidator.validate_episode_upload(
                tmdb_id, season_number, episode_number, embed_url, download_url
            )
            if not is_valid:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            # Check series exists
            series_exists, series_title = await self.tmdb_service.check_series_exists(
                tmdb_id
            )
            if not series_exists:
                return {
                    'success': False,
                    'message': UploadFormatter.format_error(
                        f"Series dengan TMDB ID {tmdb_id} tidak ditemukan di TMDB.",
                        "Pastikan TMDB ID benar"
                    )
                }
            
            # Check season exists
            season_exists, season_name = await self.tmdb_service.check_season_exists(
                tmdb_id, season_number
            )
            if not season_exists:
                return {
                    'success': False,
                    'message': UploadFormatter.format_error(
                        f"Season {season_number} tidak ditemukan untuk series ini.",
                        f"Series: {series_title}"
                    )
                }
            
            # Check episode exists
            episode_exists, episode_title = await self.tmdb_service.check_episode_exists(
                tmdb_id, season_number, episode_number
            )
            if not episode_exists:
                return {
                    'success': False,
                    'message': UploadFormatter.format_error(
                        f"Episode S{season_number:02d}E{episode_number:02d} "
                        f"tidak ditemukan di TMDB.",
                        f"Series: {series_title}"
                    )
                }
            
            # Upload ke API
            success, response_data, error = await self.api_client.upload_episode(
                tmdb_id=tmdb_id,
                season_number=season_number,
                episode_number=episode_number,
                embed_url=embed_url,
                download_url=download_url,
                telegram_username=username
            )
            
            if not success:
                # Handle 404 errors
                if response_data and response_data.get('success') == False:
                    error_msg = response_data.get('message', '')
                    
                    if 'Series not found' in error_msg:
                        return {
                            'success': False,
                            'message': UploadFormatter.format_api_error(
                                404,
                                f"Series '{series_title}' belum ada di database.\n"
                                f"Upload series dulu: /uploadseries {tmdb_id}"
                            )
                        }
                    elif 'Season not found' in error_msg:
                        return {
                            'success': False,
                            'message': UploadFormatter.format_api_error(
                                404,
                                f"Season {season_number} belum ada di database.\n"
                                f"Upload season dulu: /uploadseason {tmdb_id} season: {season_number}"
                            )
                        }
                
                # Handle validation errors
                if response_data and 'errors' in response_data:
                    errors = response_data['errors']
                    error_msg = "\n".join([
                        f"- {field}: {', '.join(msgs)}"
                        for field, msgs in errors.items()
                    ])
                    return {
                        'success': False,
                        'message': UploadFormatter.format_validation_error(error_msg)
                    }
                else:
                    return {
                        'success': False,
                        'message': UploadFormatter.format_error(
                            error or "Unknown error occurred"
                        )
                    }
            
            # Success response
            skipped = response_data.get('skipped', False)
            job_id = response_data.get('data', {}).get('job_id', 'unknown')
            
            logger.info(
                f"Episode upload {'skipped' if skipped else 'queued'}: "
                f"TMDB {tmdb_id} S{season_number}E{episode_number} by user {user_id}"
            )
            
            return {
                'success': True,
                'message': UploadFormatter.format_episode_success(
                    series_title=series_title,
                    season_number=season_number,
                    episode_number=episode_number,
                    episode_title=episode_title,
                    tmdb_id=tmdb_id,
                    job_id=job_id,
                    skipped=skipped
                )
            }
            
        except Exception as e:
            logger.error(f"Error in upload episode handler: {e}", exc_info=True)
            return {
                'success': False,
                'message': UploadFormatter.format_error(
                    "Unexpected error occurred. Please try again later.",
                    str(e)
                )
            }
