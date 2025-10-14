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
            
            # Step 2: Get movie/series info
            movie_info = None
            
            # Check if user wants to search TMDB
            if parsed_command.media_type:
                # Check if using TMDB ID search (Priority 1)
                if parsed_command.media_id:
                    # Direct fetch by TMDB ID
                    logger.info(f"Fetching {parsed_command.media_type} by TMDB ID: {parsed_command.media_id}")
                    try:
                        if parsed_command.media_type == 'movies':
                            movie_info = await self.tmdb_service.get_movie_by_id(parsed_command.media_id)
                        else:  # series
                            movie_info = await self.tmdb_service.get_tv_by_id(parsed_command.media_id)
                        
                        if not movie_info:
                            return {
                                'success': False,
                                'message': f"{parsed_command.media_type.capitalize()} dengan TMDB ID {parsed_command.media_id} tidak ditemukan"
                            }
                    except Exception as e:
                        logger.error(f"Failed to fetch {parsed_command.media_type} by ID {parsed_command.media_id}: {e}")
                        return {
                            'success': False,
                            'message': f"Gagal mengambil data {parsed_command.media_type} dengan TMDB ID {parsed_command.media_id}: {str(e)}"
                        }
                else:
                    # Search by title (Priority 2)
                    # User specified media type, berarti mau search
                    search_query = None
                    
                    # Priority 1: Use title_year if provided (format: [Judul 2024])
                    if parsed_command.title_year:
                        search_query = parsed_command.title_year
                        logger.info(f"Searching {parsed_command.media_type} with title+year: {search_query}")
                    # Priority 2: Use custom_prompt as search query
                    elif parsed_command.custom_prompt:
                        search_query = parsed_command.custom_prompt.strip()
                        logger.info(f"Searching {parsed_command.media_type} with prompt as query: {search_query}")
                    
                    if search_query:
                        movie_info = await search_content(
                            self.tmdb_service,
                            parsed_command.media_type, 
                            search_query
                        )
                        
                        if not movie_info:
                            return {
                                'success': False,
                                'message': f"{parsed_command.media_type.capitalize()} '{search_query}' tidak ditemukan di TMDB"
                            }
                    else:
                        return {
                            'success': False,
                            'message': f"Tidak ada judul untuk dicari. Format: /infofilm @user [movies/series] <judul film>"
                        }
            else:
                # Context-only mode: tidak ada movie info
                logger.info("No media type provided, sending context-only message")
            
            # Step 3: Format/generate info message
            if movie_info:
                if parsed_command.use_gemini:
                    # Generate enhanced description dengan Gemini
                    logger.info("Generating enhanced info with Gemini AI...")
                    try:
                        from services.gemini_service import get_gemini_service
                        gemini_service = get_gemini_service()
                        
                        enhanced_text = await gemini_service.generate_announcement(
                            movie_info,
                            parsed_command.custom_prompt,
                            parsed_command.custom_synopsis
                        )
                        
                        # Format dengan enhancement
                        info_message = self.formatter.format_announcement(enhanced_text, movie_info)
                    except Exception as e:
                        logger.error(f"Failed to generate with Gemini: {e}")
                        # Fallback to standard format
                        info_message = self.formatter.format_movie_info(movie_info)
                else:
                    # Standard format tanpa AI
                    info_message = self.formatter.format_movie_info(movie_info)
                
                title = movie_info.get('title') or movie_info.get('name', 'Unknown')
            else:
                # Context-only message
                if parsed_command.use_gemini:
                    # Generate dengan Gemini for context-only
                    logger.info("Generating context message with Gemini AI...")
                    try:
                        from services.gemini_service import get_gemini_service
                        gemini_service = get_gemini_service()
                        
                        info_message = await gemini_service.generate_custom_content(
                            parsed_command.custom_prompt
                        )
                    except Exception as e:
                        logger.error(f"Failed to generate with Gemini: {e}")
                        info_message = parsed_command.custom_prompt
                else:
                    # Raw text
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
