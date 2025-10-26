"""
Unified Input Handler
Routes text input to appropriate handler based on user state.
Handles both movie and series upload flows.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class UnifiedInputHandler:
    """Unified handler that routes text input based on user state."""
    
    def __init__(self, movie_handler, movie_handler_2, series_handler):
        """
        Initialize unified handler.
        
        Args:
            movie_handler: MovieUploadHandler instance
            movie_handler_2: MovieUploadHandlerPart2 instance
            series_handler: SeriesUploadHandler instance
        """
        self.movie_handler = movie_handler
        self.movie_handler_2 = movie_handler_2
        self.series_handler = series_handler
        logger.info("UnifiedInputHandler initialized")
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Route text input to appropriate handler based on state.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            logger.info("🎯 Unified input handler called")
            
            # Check movie upload states
            if context.user_data.get('awaiting_movie_tmdb_id', False):
                logger.info("→ Routing to Movie TMDB ID handler")
                await self.movie_handler.handle_tmdb_id_input(update, context)
                return
            
            if context.user_data.get('awaiting_movie_embed_url', False):
                logger.info("→ Routing to Movie Embed URL handler")
                await self.movie_handler.handle_embed_url_input(update, context)
                return
            
            if context.user_data.get('awaiting_movie_download_url', False):
                logger.info("→ Routing to Movie Download URL handler")
                await self.movie_handler_2.handle_download_url_input(update, context)
                return
            
            # Check series upload states
            if context.user_data.get('awaiting_series_tmdb_id', False):
                logger.info("→ Routing to Series TMDB ID handler")
                await self.series_handler.handle_tmdb_id_input(update, context)
                return
            
            # No state matched
            logger.info("→ No input awaited, ignoring")
            
        except Exception as e:
            logger.error(f"Error in unified input handler: {e}", exc_info=True)
