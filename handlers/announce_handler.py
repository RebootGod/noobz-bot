"""
Announce Handler untuk handle /announce command.
Process announcement generation dan send ke target channel/group.
"""

import logging
from typing import Optional

from services.tmdb_service import get_tmdb_service
from services.gemini_service import get_gemini_service
from services.multi_account_manager import get_multi_account_manager
from utils.message_parser import ParsedCommand
from utils.chat_finder import ChatFinder
from utils.message_formatter import get_message_formatter
from handlers.announce_content_search import search_content

logger = logging.getLogger(__name__)


class AnnounceHandler:
    """
    Handler untuk /announce command.
    """
    
    def __init__(self, telegram_client):
        """
        Initialize handler.
        
        Args:
            telegram_client: TelegramClient instance
        """
        self.client = telegram_client
        self.tmdb_service = get_tmdb_service()
        self.gemini_service = get_gemini_service()
        self.multi_account_manager = get_multi_account_manager()
        self.chat_finder = ChatFinder(telegram_client)
        self.formatter = get_message_formatter()
    
    async def handle(self, parsed_command: ParsedCommand) -> dict:
        """
        Handle /announce command.
        
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
            
            # Step 1: Find target chat
            logger.info(f"Finding target chat: {parsed_command.target}")
            target_entity = await self._find_target(parsed_command.target)
            
            if not target_entity:
                return {
                    'success': False,
                    'message': f"Channel/group '{parsed_command.target}' tidak ditemukan"
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
                logger.info("No media type/title provided, generating announcement from context only")
            
            # Step 3: Generate announcement dengan AI
            logger.info("Generating announcement with Gemini AI...")
            try:
                announcement = await self._generate_announcement(
                    movie_info, 
                    parsed_command.custom_prompt,
                    parsed_command.custom_synopsis
                )
            except Exception as e:
                logger.error(f"Failed to generate announcement: {e}")
                return {
                    'success': False,
                    'message': f"Gagal generate announcement: {str(e)}"
                }
            
            # Step 4: Format announcement
            formatted_message = self.formatter.format_announcement(
                announcement, 
                movie_info  # Can be None if no TMDB ID
            )
            
            # Step 5: Send ke target
            logger.info(f"Sending announcement to {parsed_command.target}...")
            
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
                    target_entity,
                    message=formatted_message,
                    file=poster_url,
                    parse_mode='markdown'
                )
                
                if not result['success']:
                    logger.error(f"Failed to send with multi-account: {result.get('message')}")
                    return {
                        'success': False,
                        'message': f"Gagal mengirim announcement: {result.get('message')}"
                    }
                
                logger.info(f"Successfully sent announcement via {result.get('account_id', 'unknown')}")
            else:
                # Fallback to direct send (single account mode)
                try:
                    if poster_url:
                        await self.client.send_file(
                            target_entity,
                            poster_url,
                            caption=formatted_message,
                            parse_mode='markdown'
                        )
                    else:
                        await self.client.send_message(
                            target_entity,
                            formatted_message,
                            parse_mode='markdown'
                        )
                    logger.info("Successfully sent announcement (single account mode)")
                except Exception as e:
                    logger.error(f"Failed to send message: {e}")
                    return {
                        'success': False,
                        'message': f"Gagal mengirim announcement: {str(e)}"
                    }
            
            return {
                'success': True,
                'message': f"Announcement berhasil dikirim ke {parsed_command.target}",
                'preview': formatted_message[:100] + '...' if len(formatted_message) > 100 else formatted_message
            }
            
        except Exception as e:
            logger.error(f"Failed to handle announce command: {e}")
            return {
                'success': False,
                'message': f"Error: {str(e)}"
            }
    
    async def _find_target(self, target_name: str):
        """
        Find target channel/group.
        
        Args:
            target_name: Nama channel/group
            
        Returns:
            Entity jika ditemukan, None jika tidak
        """
        try:
            # Try fuzzy match first
            entity = await self.chat_finder.find_by_name(target_name, exact_match=False)
            return entity
        except Exception as e:
            logger.error(f"Error finding target: {e}")
            return None
    
    async def _generate_announcement(
        self, 
        movie_info: Optional[dict], 
        custom_prompt: Optional[str],
        custom_synopsis: Optional[str] = None
    ) -> str:
        """
        Generate announcement dengan Gemini AI.
        
        Args:
            movie_info: Movie info dari TMDB (optional)
            custom_prompt: Custom prompt dari user (optional)
            custom_synopsis: Custom synopsis dari user dengan [sinopsis] tag (optional)
            
        Returns:
            Generated announcement text
        """
        try:
            if movie_info:
                # Generate dengan movie info
                announcement = await self.gemini_service.generate_announcement(
                    movie_info,
                    custom_prompt,
                    custom_synopsis
                )
            else:
                # Generate dengan custom prompt saja
                if not custom_prompt:
                    raise Exception("Tidak ada movie info atau custom prompt")
                
                announcement = await self.gemini_service.generate_custom_content(
                    custom_prompt
                )
            
            return announcement
            
        except Exception as e:
            logger.error(f"Error generating announcement: {e}")
            raise


def create_announce_handler(telegram_client) -> AnnounceHandler:
    """
    Factory function untuk create AnnounceHandler.
    
    Args:
        telegram_client: TelegramClient instance
        
    Returns:
        AnnounceHandler instance
    """
    return AnnounceHandler(telegram_client)
