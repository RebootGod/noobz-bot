"""
Series Upload Handler (Part 1)
Handles series creation, TMDB fetch, and season selection.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from services.session_service import SessionService
from services.tmdb_service import TmdbService
from services.noobz_api_service import NoobzApiService
from services.context_service import ContextService
from ui.messages import SeriesMessages, ErrorMessages
from ui.keyboards_series import SeriesUploadKeyboards
from ui.formatters import SeriesFormatters
from utils.validators import InputValidator

logger = logging.getLogger(__name__)


class SeriesUploadHandler:
    """Handler for series upload operations - Part 1: Creation & Season Selection."""
    
    def __init__(
        self,
        session_service: SessionService,
        tmdb_service: TmdbService,
        noobz_api_service: NoobzApiService,
        context_service: ContextService
    ):
        """
        Initialize series upload handler.
        
        Args:
            session_service: Session management service
            tmdb_service: TMDB data service
            noobz_api_service: Noobz API client service
            context_service: Upload context service
        """
        self.session_service = session_service
        self.tmdb_service = tmdb_service
        self.noobz_api_service = noobz_api_service
        self.context_service = context_service
        logger.info("SeriesUploadHandler initialized")
    
    async def start_series_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Start series upload flow - prompt for TMDB ID.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Check session
            session = self.session_service.get_active_session(user.id)
            if not session:
                await query.edit_message_text(
                    "❌ Session expired. Use /start to login again."
                )
                return
            
            # Clear any existing series state
            context.user_data.pop('series_upload', None)
            
            # Set state to awaiting TMDB ID
            context.user_data['awaiting_series_tmdb_id'] = True
            
            # Send prompt
            prompt = SeriesMessages.ask_tmdb_id()
            await query.edit_message_text(prompt, parse_mode='HTML')
            
            logger.info(f"User {user.id} started series upload")
            
        except Exception as e:
            logger.error(f"Error in start_series_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error starting upload")
    
    async def handle_tmdb_id_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle TMDB ID input for series.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting series TMDB ID
            if not context.user_data.get('awaiting_series_tmdb_id', False):
                return
            
            user = update.effective_user
            tmdb_id_str = update.message.text.strip()
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Validate TMDB ID
            if not InputValidator.validate_tmdb_id(tmdb_id_str):
                error_msg = ErrorMessages.invalid_input(
                    "TMDB ID must be a positive number.\nExample: 1396 (Breaking Bad)"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                return
            
            tmdb_id = int(tmdb_id_str)
            
            # Send fetching message
            fetching_msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=SeriesMessages.tmdb_fetching()
            )
            
            # Fetch series data from TMDB
            series_data = await self.tmdb_service.get_series(tmdb_id)
            
            if not series_data:
                # TMDB fetch failed
                await fetching_msg.edit_text(
                    SeriesMessages.tmdb_fetch_error(tmdb_id),
                    parse_mode='HTML'
                )
                context.user_data['awaiting_series_tmdb_id'] = False
                return
            
            # Clear awaiting state
            context.user_data['awaiting_series_tmdb_id'] = False
            
            # Show series info and creating message
            series_info = SeriesFormatters.format_series_info(series_data)
            creating_msg = SeriesMessages.series_creating()
            
            await fetching_msg.edit_text(
                f"{series_info}\n\n{creating_msg}",
                parse_mode='HTML'
            )
            
            # Create series in database
            result = await self.noobz_api_service.create_series(tmdb_id)
            
            # Deep checking: avoid showing both error and success for ambiguous API responses
            error_msg = result.get('message', '') or ''
            is_success = result.get('success', False)
            
            # If API returns ambiguous message but status indicates success, treat as success
            if not is_success and not ('queued successfully' in error_msg.lower() or 'created successfully' in error_msg.lower()):
                # Check if series already exists
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    fail_msg = SeriesMessages.series_exists(series_data['title'])
                else:
                    fail_msg = SeriesMessages.series_create_error(error_msg or 'Unknown error')
                
                await fetching_msg.edit_text(
                    fail_msg,
                    parse_mode='HTML'
                )
                logger.warning(f"User {user.id} series creation failed: {error_msg}")
                return
            
            # Success - save to context service
            series_id = result.get('series_id')
            
            self.context_service.save_context(
                telegram_user_id=user.id,
                context_type='series',
                series_tmdb_id=tmdb_id,
                series_title=series_data['title'],
                series_id=series_id
            )
            
            # Show success and season selection
            success_msg = SeriesMessages.series_created(series_data['title'])
            
            # Build season selection keyboard
            seasons = series_data.get('seasons', [])
            keyboard = SeriesUploadKeyboards.season_selection(
                tmdb_id=tmdb_id,
                seasons=seasons
            )
            
            await fetching_msg.edit_text(
                f"{success_msg}\n\n{series_info}",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(
                f"User {user.id} created series: {series_data['title']} "
                f"(TMDB: {tmdb_id}, DB ID: {series_id})"
            )
            
        except Exception as e:
            logger.error(f"Error in handle_series_tmdb_id_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_series_tmdb_id'] = False
    
    async def handle_season_selection(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle season selection callback.
        Format: series_season_{tmdb_id}_{season_number}
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Check session
            session = self.session_service.get_active_session(user.id)
            if not session:
                await query.edit_message_text(
                    "❌ Session expired. Use /start to login again."
                )
                return
            
            # Parse callback data: series_season_{tmdb_id}_{season_number}
            callback_parts = query.data.split('_')
            if len(callback_parts) < 4:
                await query.answer("❌ Invalid callback data")
                return
            
            tmdb_id = int(callback_parts[2])
            season_number = int(callback_parts[3])
            
            # Get series context
            series_context = self.context_service.get_context(user.id, 'series')
            
            if not series_context or series_context['series_tmdb_id'] != tmdb_id:
                # No context or mismatch - fetch series data again
                series_data = await self.tmdb_service.get_series(tmdb_id)
                if not series_data:
                    await query.edit_message_text(
                        ErrorMessages.api_error(),
                        parse_mode='HTML'
                    )
                    return
                
                series_title = series_data['title']
                series_id = None
            else:
                series_title = series_context['series_title']
                series_id = series_context.get('series_id')
            
            # Update context with season info
            self.context_service.save_context(
                telegram_user_id=user.id,
                context_type='season',
                series_tmdb_id=tmdb_id,
                series_title=series_title,
                season_number=season_number,
                series_id=series_id
            )
            
            # Show checking status message
            checking_msg = SeriesMessages.checking_episode_status(
                series_title, 
                season_number
            )
            
            await query.edit_message_text(
                checking_msg,
                parse_mode='HTML'
            )
            
            # Import part 2 handler to continue flow
            from .series_upload_handler_2 import SeriesUploadHandlerPart2
            
            # Create part 2 handler
            part2_handler = SeriesUploadHandlerPart2(self)
            
            # Continue to episode status checking
            await part2_handler.show_episode_status(update, context, tmdb_id, season_number)
            
            logger.info(
                f"User {user.id} selected season {season_number} "
                f"for series {series_title} (TMDB: {tmdb_id})"
            )
            
        except Exception as e:
            logger.error(f"Error in handle_season_selection: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error selecting season")
    
    async def cancel_series_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Cancel series upload and clear state.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Clear upload context
            self.context_service.clear_context(user.id)
            
            # Clear user data
            context.user_data.pop('series_upload', None)
            context.user_data.pop('awaiting_series_tmdb_id', None)
            
            # Show cancellation message
            from ui.keyboards_main_auth import MainMenuKeyboards
            
            session = self.session_service.get_active_session(user.id)
            is_master = session['is_master'] if session else False
            
            keyboard = MainMenuKeyboards.main_menu(is_master)
            
            await query.edit_message_text(
                "❌ <b>Upload Cancelled</b>\n\nReturning to main menu...",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} cancelled series upload")
            
        except Exception as e:
            logger.error(f"Error in cancel_series_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
