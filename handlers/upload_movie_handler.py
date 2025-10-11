"""
Handler untuk /uploadmovie command.
Upload movie ke Noobz API via bot.
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


class UploadMovieHandler:
    """Handler untuk upload movie command."""
    
    def __init__(self, client):
        """
        Initialize upload movie handler.
        
        Args:
            client: Telethon client instance
        """
        self.client = client
        self.auth_config = get_auth_config()
        self.api_client = get_api_client()
        self.tmdb_service = get_tmdb_fetch_service()
    
    async def handle(self, parsed_command) -> Dict[str, Any]:
        """
        Handle /uploadmovie command.
        
        Args:
            parsed_command: Parsed command object with user_id, message
            
        Returns:
            Dict dengan success status dan message
        """
        try:
            user_id = parsed_command.get('user_id')
            username = parsed_command.get('username', 'unknown')
            message_text = parsed_command.get('message', '')
            
            # Check authorization
            if not self.auth_config.is_authorized(user_id):
                logger.warning(f"Unauthorized upload attempt by user {user_id}")
                return {
                    'success': False,
                    'message': UploadFormatter.format_unauthorized()
                }
            
            # Parse message
            success, parsed_data, error = UploadParser.parse_movie_upload(message_text)
            if not success:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            tmdb_id = parsed_data['tmdb_id']
            embed_url = parsed_data['embed_url']
            download_url = parsed_data.get('download_url')
            
            # Validate data
            is_valid, error = UploadValidator.validate_movie_upload(
                tmdb_id, embed_url, download_url
            )
            if not is_valid:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            # Check TMDB existence
            exists, title = await self.tmdb_service.check_movie_exists(tmdb_id)
            if not exists:
                return {
                    'success': False,
                    'message': UploadFormatter.format_error(
                        f"Movie dengan TMDB ID {tmdb_id} tidak ditemukan di TMDB.",
                        "Pastikan TMDB ID benar"
                    )
                }
            
            # Upload ke API
            success, response_data, error = await self.api_client.upload_movie(
                tmdb_id=tmdb_id,
                embed_url=embed_url,
                download_url=download_url,
                telegram_username=username
            )
            
            if not success:
                # Handle API errors
                if response_data and 'errors' in response_data:
                    # Validation errors dari Laravel
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
                f"Movie upload {'skipped' if skipped else 'queued'}: "
                f"TMDB {tmdb_id} by user {user_id}"
            )
            
            return {
                'success': True,
                'message': UploadFormatter.format_movie_success(
                    title=title,
                    tmdb_id=tmdb_id,
                    job_id=job_id,
                    skipped=skipped
                )
            }
            
        except Exception as e:
            logger.error(f"Error in upload movie handler: {e}", exc_info=True)
            return {
                'success': False,
                'message': UploadFormatter.format_error(
                    "Unexpected error occurred. Please try again later.",
                    str(e)
                )
            }
