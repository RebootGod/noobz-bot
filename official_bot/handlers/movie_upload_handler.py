"""
Movie Upload Handler
Handles movie upload flow with form-style UI.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime

from services.session_service import SessionService
from services.tmdb_service import TmdbService
from services.noobz_api_service import NoobzApiService
from ui.messages import MovieMessages, ErrorMessages
from ui.keyboards_movie import (
    MovieUploadKeyboards,
    MoviePreviewKeyboards,
    get_movie_status_emoji,
    format_movie_state_summary
)
from ui.formatters import MovieFormatters, URLFormatters
from utils.validators import InputValidator

logger = logging.getLogger(__name__)


class MovieUploadHandler:
    """Handler for movie upload operations with form-style UI."""
    
    def __init__(
        self,
        session_service: SessionService,
        tmdb_service: TmdbService,
        noobz_api_service: NoobzApiService
    ):
        """
        Initialize movie upload handler.
        
        Args:
            session_service: Session management service
            tmdb_service: TMDB data service
            noobz_api_service: Noobz API client service
        """
        self.session_service = session_service
        self.tmdb_service = tmdb_service
        self.noobz_api_service = noobz_api_service
        logger.info("MovieUploadHandler initialized")
    
    async def start_movie_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Start movie upload flow - show form with empty state.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            logger.info(f"start_movie_upload called by user {update.effective_user.id}")
            
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Check session
            session = self.session_service.get_active_session(user.id)
            logger.info(f"Session check: {session is not None}")
            
            if not session:
                await query.edit_message_text(
                    "❌ Session expired. Use /start to login again."
                )
                return
            
            # Initialize movie state in context
            context.user_data['movie_upload'] = {
                'tmdb_id': None,
                'title': None,
                'year': None,
                'embed_url': None,
                'download_url': None,
                'tmdb_data': None
            }
            
            # Show initial form
            await self._show_movie_form(query, context)
            
            logger.info(f"User {user.id} started movie upload")
            
        except Exception as e:
            logger.error(f"Error in start_movie_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error starting upload")
    
    async def _show_movie_form(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Display movie upload form with current state.
        
        Args:
            query: Callback query object
            context: Telegram context object
        """
        state = context.user_data.get('movie_upload', {})
        
        # Build form display text
        form_text = get_movie_status_emoji(state)
        form_text += "\n\n" + format_movie_state_summary(state)
        
        # Get keyboard based on current state
        keyboard = MovieUploadKeyboards.movie_form(state)
        
        await query.edit_message_text(
            form_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def prompt_tmdb_id(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Prompt user to enter TMDB ID.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Set state to awaiting TMDB ID
            context.user_data['awaiting_movie_tmdb_id'] = True
            logger.info(f"Set awaiting_movie_tmdb_id=True for user {update.effective_user.id}")
            
            # Send prompt
            prompt = MovieMessages.ask_tmdb_id()
            await query.edit_message_text(prompt, parse_mode='HTML')
            
            logger.info(f"User {update.effective_user.id} prompted for TMDB ID")
            
        except Exception as e:
            logger.error(f"Error in prompt_tmdb_id: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def handle_tmdb_id_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle TMDB ID input from user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting TMDB ID
            awaiting = context.user_data.get('awaiting_movie_tmdb_id', False)
            logger.info(f"handle_tmdb_id_input called, awaiting={awaiting}")
            
            if not awaiting:
                logger.info("Not awaiting TMDB ID, skipping")
                return  # Skip processing, let other handlers try
            
            user = update.effective_user
            tmdb_id_str = update.message.text.strip()
            logger.info(f"Processing TMDB ID input: {tmdb_id_str}")
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Validate TMDB ID
            if not InputValidator.validate_tmdb_id(tmdb_id_str):
                error_msg = ErrorMessages.invalid_input(
                    "TMDB ID must be a positive number.\nExample: 550"
                )
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                # Keep awaiting state
                return
            
            tmdb_id = int(tmdb_id_str)
            
            # Send fetching message
            fetching_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=MovieMessages.tmdb_fetching()
            )
            
            # Fetch movie data from TMDB
            movie_data = await self.tmdb_service.get_movie(tmdb_id)
            
            if not movie_data:
                # TMDB fetch failed
                await fetching_msg.edit_text(
                    MovieMessages.tmdb_fetch_failed(),
                    reply_markup=MoviePreviewKeyboards.tmdb_fetch_error(),
                    parse_mode='HTML'
                )
                context.user_data['awaiting_movie_tmdb_id'] = False
                return
            
            # Success - save to state
            context.user_data['movie_upload']['tmdb_id'] = tmdb_id
            context.user_data['movie_upload']['title'] = movie_data.get('title')
            context.user_data['movie_upload']['year'] = movie_data.get('year')
            context.user_data['movie_upload']['tmdb_data'] = movie_data
            context.user_data['awaiting_movie_tmdb_id'] = False
            
            # Show movie preview
            preview_text = "✅ TMDB ID set\n\n"
            preview_text += MovieFormatters.format_movie_info(movie_data)
            preview_text += "\n\n" + format_movie_state_summary(
                context.user_data['movie_upload']
            )
            
            keyboard = MovieUploadKeyboards.movie_form(context.user_data['movie_upload'])
            
            await fetching_msg.edit_text(
                preview_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} set TMDB ID: {tmdb_id}")
            
        except Exception as e:
            logger.error(f"Error in handle_tmdb_id_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_movie_tmdb_id'] = False
    
    async def prompt_embed_url(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Prompt user to enter embed URL.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Set state
            context.user_data['awaiting_movie_embed_url'] = True
            logger.info(f"Set awaiting_movie_embed_url=True for user {update.effective_user.id}")
            
            # Send prompt
            prompt = MovieMessages.ask_embed_url()
            await query.edit_message_text(prompt, parse_mode='HTML')
            
            logger.info(f"User {update.effective_user.id} prompted for embed URL")
            
        except Exception as e:
            logger.error(f"Error in prompt_embed_url: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    async def handle_embed_url_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle embed URL input from user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            logger.info(f"handle_embed_url_input called, awaiting={context.user_data.get('awaiting_movie_embed_url', False)}")
            
            # Check if we're expecting embed URL
            if not context.user_data.get('awaiting_movie_embed_url', False):
                logger.info("Not awaiting embed URL, skipping")
                return  # Skip processing, let other handlers try
            
            user = update.effective_user
            embed_url = update.message.text.strip()
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Basic URL validation only (no whitelist)
            url_check = InputValidator.validate_url(embed_url, check_https=False)
            if not url_check['valid']:
                error_msg = ErrorMessages.invalid_input(
                    f"Invalid URL format.\n{url_check['error']}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                return
            
            # Save to state
            context.user_data['movie_upload']['embed_url'] = embed_url
            context.user_data['awaiting_movie_embed_url'] = False
            
            # Show updated form
            success_text = "✅ Embed URL set\n\n"
            success_text += format_movie_state_summary(
                context.user_data['movie_upload']
            )
            
            keyboard = MovieUploadKeyboards.movie_form(context.user_data['movie_upload'])
            
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} set embed URL")
            
        except Exception as e:
            logger.error(f"Error in handle_embed_url_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_movie_embed_url'] = False
