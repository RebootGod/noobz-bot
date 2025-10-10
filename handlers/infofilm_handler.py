"""
InfoFilm Handler untuk handle /infofilm command.
Process film search dan send info ke target user.
"""

import logging
from typing import Optional, Dict, Any

from services.tmdb_service import get_tmdb_service
from services.multi_account_manager import get_multi_account_manager
from utils.message_parser import ParsedCommand
from utils.chat_finder import ChatFinder
from utils.message_formatter import get_message_formatter
from handlers.announce_content_search import search_content

logger = logging.getLogger(__name__)


class InfoFilmHandler:
    """
    Handler untuk /infofilm command.
    """
    
    def __init__(self, telegram_client):
        """
        Initialize handler.
        
        Args:
            telegram_client: TelegramClient instance
        """
        self.client = telegram_client
        self.tmdb_service = get_tmdb_service()
        self.multi_account_manager = get_multi_account_manager()
        self.chat_finder = ChatFinder(telegram_client)
        self.formatter = get_message_formatter()
    
    async def handle(self, parsed_command: ParsedCommand) -> dict:
        """
        Handle /infofilm command.
        
        Args:
            parsed_command: ParsedCommand object
            
        Returns:
            Result dictionary dengan status dan message
        """
        try:
            # Validate command
            if not parsed_command.is_valid:
                return {
                    'success': False,
                    'message': parsed_command.error_message
                }
            
            # Step 1: Find target user
            logger.info(f"Finding target user: @{parsed_command.target}")
            target_user = await self._find_user(parsed_command.target)
            
            if not target_user:
                return {
                    'success': False,
                    'message': f"User @{parsed_command.target} tidak ditemukan"
                }
            
            # Step 2: Get movie/series info jika ada media_type + title_year (OPTIONAL)
            movie_info = None
            if parsed_command.media_type and parsed_command.title_year:
                logger.info(f"Searching {parsed_command.media_type} with title: {parsed_command.title_year}")
                movie_info = await search_content(
                    self.tmdb_service,
                    parsed_command.media_type, 
                    parsed_command.title_year
                )
                
                if not movie_info:
                    return {
                        'success': False,
                        'message': f"{parsed_command.media_type.capitalize()} '{parsed_command.title_year}' tidak ditemukan"
                    }
            else:
                # Context-only mode: tidak ada movie info
                logger.info("No media type/title provided, sending context-only message")
            
            # Step 3: Format info message
            if movie_info:
                info_message = self.formatter.format_movie_info(movie_info)
                title = movie_info.get('title') or movie_info.get('name', 'Unknown')
            else:
                # Context-only message
                info_message = parsed_command.custom_prompt
                title = "Info"
            
            # Step 4: Send ke target user
            logger.info(f"Sending info to @{parsed_command.target}...")
            
            # Use multi-account manager if available, otherwise use direct client
            use_multi_account = (
                self.multi_account_manager._initialized and 
                len(self.multi_account_manager.accounts) > 0
            )
            
            # Send poster image if available (only if movie_info exists)
            poster_path = movie_info.get('poster_path') if movie_info else None
            poster_url = None
            if poster_path:
                poster_url = self.tmdb_service.get_poster_url(poster_path)
            
            # Send with multi-account fallback
            if use_multi_account:
                result = await self.multi_account_manager.send_with_fallback(
                    target_user,
                    message=info_message,
                    file=poster_url,
                    parse_mode='markdown'
                )
                
                if not result['success']:
                    logger.error(f"Failed to send with multi-account: {result.get('message')}")
                    return {
                        'success': False,
                        'message': f"Gagal mengirim info: {result.get('message')}"
                    }
                
                logger.info(f"Successfully sent info via {result.get('account_id', 'unknown')}")
            else:
                # Fallback to direct send (single account mode)
                try:
                    if poster_url:
                        await self.client.send_file(
                            target_user,
                            poster_url,
                            caption=info_message,
                            parse_mode='markdown'
                        )
                    else:
                        await self.client.send_message(
                            target_user,
                            info_message,
                            parse_mode='markdown'
                        )
                    logger.info("Successfully sent info (single account mode)")
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
                    return {
                        'success': False,
                        'message': f"Gagal mengirim info: {str(e)}"
                    }
            
            return {
                'success': True,
                'message': f"Info '{title}' berhasil dikirim ke @{parsed_command.target}",
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Failed to handle infofilm command: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    async def _find_user(self, username: str):
        """
        Find user by username.
        
        Args:
            username: Username (tanpa @)
            
        Returns:
            User entity jika ditemukan, None jika tidak
        """
        try:
            user = await self.chat_finder.find_user_by_username(username)
            return user
        except Exception as e:
            logger.error(f"Error finding user: {e}")
            return None


def create_infofilm_handler(telegram_client) -> InfoFilmHandler:
    """
    Factory function untuk create InfoFilmHandler.
    
    Args:
        telegram_client: TelegramClient instance
        
    Returns:
        InfoFilmHandler instance
    """
    return InfoFilmHandler(telegram_client)
