"""
InfoFilm Handler untuk handle /infofilm command.
Process film search dan send info ke target user.
"""

import logging
from typing import Optional, Dict, Any

from services.tmdb_service import get_tmdb_service
from utils.message_parser import ParsedCommand
from utils.chat_finder import ChatFinder
from utils.message_formatter import get_message_formatter

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
            
            # Step 2: Search film/series
            logger.info(
                f"Searching {parsed_command.content_type}: {parsed_command.keyword} "
                f"({parsed_command.year or 'any year'})"
            )
            
            search_results = await self._search_content(
                parsed_command.content_type,
                parsed_command.keyword,
                parsed_command.year
            )
            
            if not search_results:
                return {
                    'success': False,
                    'message': f"Tidak ditemukan hasil untuk '{parsed_command.keyword}'"
                }
            
            # Step 3: Get first result (best match)
            best_match = search_results[0]
            content_id = best_match['id']
            
            # Get full details
            logger.info(f"Fetching full details for ID: {content_id}")
            content_info = await self._get_full_info(
                content_id,
                parsed_command.content_type
            )
            
            if not content_info:
                return {
                    'success': False,
                    'message': "Gagal mengambil detail film"
                }
            
            # Step 4: Format info message
            info_message = self.formatter.format_movie_info(
                content_info,
                parsed_command.content_type
            )
            
            # Step 5: Send ke target user
            title = content_info.get('title') or content_info.get('name', 'Unknown')
            logger.info(f"Sending info to @{parsed_command.target}...")
            
            # Send poster image if available
            poster_path = content_info.get('poster_path')
            if poster_path:
                poster_url = self.tmdb_service.get_poster_url(poster_path)
                if poster_url:
                    try:
                        await self.client.send_file(
                            target_user,
                            poster_url,
                            caption=info_message,
                            parse_mode='markdown'
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send poster, sending text only: {e}")
                        await self.client.send_message(
                            target_user,
                            info_message,
                            parse_mode='markdown'
                        )
                else:
                    # No poster URL, send text only
                    await self.client.send_message(
                        target_user,
                        info_message,
                        parse_mode='markdown'
                    )
            else:
                # No poster, send text only
                await self.client.send_message(
                    target_user,
                    info_message,
                    parse_mode='markdown'
                )
            
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
    
    async def _search_content(
        self, 
        content_type: str, 
        keyword: str, 
        year: Optional[int]
    ) -> list:
        """
        Search movie atau TV series.
        
        Args:
            content_type: 'movie' atau 'tv'
            keyword: Search keyword
            year: Year filter (optional)
            
        Returns:
            List of search results
        """
        try:
            if content_type == 'movie':
                results = await self.tmdb_service.search_movie(keyword, year)
            else:
                results = await self.tmdb_service.search_tv(keyword, year)
            
            return results
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def _get_full_info(self, content_id: int, content_type: str) -> Optional[Dict[str, Any]]:
        """
        Get full details untuk movie/TV series.
        
        Args:
            content_id: TMDB ID
            content_type: 'movie' atau 'tv'
            
        Returns:
            Full details dictionary atau None
        """
        try:
            if content_type == 'movie':
                info = await self.tmdb_service.get_movie_by_id(content_id)
            else:
                info = await self.tmdb_service.get_tv_by_id(content_id)
            
            return info
        except Exception as e:
            logger.error(f"Error getting full info: {e}")
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
