"""
Handler untuk /uploadseries command.
Upload series ke Noobz API via bot.
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


class UploadSeriesHandler:
    """Handler untuk upload series command."""
    
    def __init__(self, client):
        """
        Initialize upload series handler.
        
        Args:
            client: Telethon client instance
        """
        self.client = client
        self.auth_config = get_auth_config()
        self.api_client = get_api_client()
        self.tmdb_service = get_tmdb_fetch_service()
    
    async def handle(self, parsed_command) -> Dict[str, Any]:
        """
        Handle /uploadseries command.
        
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
            success, parsed_data, error = UploadParser.parse_series_upload(message_text)
            if not success:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            tmdb_id = parsed_data['tmdb_id']
            
            # Validate data
            is_valid, error = UploadValidator.validate_series_upload(tmdb_id)
            if not is_valid:
                return {
                    'success': False,
                    'message': UploadFormatter.format_validation_error(error)
                }
            
            # Check TMDB existence
            exists, title = await self.tmdb_service.check_series_exists(tmdb_id)
            if not exists:
                return {
                    'success': False,
                    'message': UploadFormatter.format_error(
                        f"Series dengan TMDB ID {tmdb_id} tidak ditemukan di TMDB.",
                        "Pastikan TMDB ID benar"
                    )
                }
            
            # Upload ke API
            success, response_data, error = await self.api_client.upload_series(
                tmdb_id=tmdb_id,
                telegram_username=username
            )
            
            if not success:
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
                f"Series upload {'skipped' if skipped else 'queued'}: "
                f"TMDB {tmdb_id} by user {user_id}"
            )
            
            return {
                'success': True,
                'message': UploadFormatter.format_series_success(
                    title=title,
                    tmdb_id=tmdb_id,
                    job_id=job_id,
                    skipped=skipped
                )
            }
            
        except Exception as e:
            logger.error(f"Error in upload series handler: {e}", exc_info=True)
            return {
                'success': False,
                'message': UploadFormatter.format_error(
                    "Unexpected error occurred. Please try again later.",
                    str(e)
                )
            }
