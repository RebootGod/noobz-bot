"""
Announce Handler untuk handle /announce command.
Process announcement generation dan send ke target channel/group.
"""

import logging
from typing import Optional

from services.tmdb_service import get_tmdb_service
from services.gemini_service import get_gemini_service
from utils.message_parser import ParsedCommand
from utils.chat_finder import ChatFinder
from utils.message_formatter import get_message_formatter

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
            
            # Step 2: Get movie info jika ada TMDB ID
            movie_info = None
            if parsed_command.tmdb_id:
                logger.info(f"Fetching movie info for TMDB ID: {parsed_command.tmdb_id}")
                movie_info = await self._get_movie_info(parsed_command.tmdb_id)
                
                if not movie_info:
                    return {
                        'success': False,
                        'message': f"Film dengan ID {parsed_command.tmdb_id} tidak ditemukan"
                    }
            
            # Step 3: Generate announcement dengan AI
            logger.info("Generating announcement with Gemini AI...")
            announcement = await self._generate_announcement(
                movie_info, 
                parsed_command.custom_prompt
            )
            
            # Step 4: Format announcement
            formatted_message = self.formatter.format_announcement(
                announcement, 
                movie_info
            )
            
            # Step 5: Send ke target
            logger.info(f"Sending announcement to {parsed_command.target}...")
            await self.client.send_message(
                target_entity,
                formatted_message,
                parse_mode='markdown'
            )
            
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
    
    async def _get_movie_info(self, tmdb_id: int) -> Optional[dict]:
        """
        Get movie info dari TMDB.
        
        Args:
            tmdb_id: TMDB movie ID
            
        Returns:
            Movie info dictionary atau None
        """
        try:
            # Try as movie first
            try:
                movie_info = await self.tmdb_service.get_movie_by_id(tmdb_id)
                return movie_info
            except:
                # If failed, try as TV series
                tv_info = await self.tmdb_service.get_tv_by_id(tmdb_id)
                return tv_info
        except Exception as e:
            logger.error(f"Error fetching movie info: {e}")
            return None
    
    async def _generate_announcement(
        self, 
        movie_info: Optional[dict], 
        custom_prompt: Optional[str]
    ) -> str:
        """
        Generate announcement dengan Gemini AI.
        
        Args:
            movie_info: Movie info dari TMDB (optional)
            custom_prompt: Custom prompt dari user (optional)
            
        Returns:
            Generated announcement text
        """
        try:
            if movie_info:
                # Generate dengan movie info
                announcement = await self.gemini_service.generate_announcement(
                    movie_info,
                    custom_prompt
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
