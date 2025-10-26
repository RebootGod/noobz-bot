"""
Movie Upload Handler (Part 2)
Continuation of movie upload flow - download URL and final upload.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from ui.messages import MovieMessages, ErrorMessages
from ui.keyboards_movie import MovieUploadKeyboards, format_movie_state_summary
from ui.keyboards_main_auth import MainMenuKeyboards
from ui.formatters import URLFormatters
from utils.validators import InputValidator

logger = logging.getLogger(__name__)


class MovieUploadHandlerPart2:
    """Continuation of movie upload handler for download URL and upload operations."""
    
    def __init__(self, main_handler):
        """
        Initialize part 2 handler.
        
        Args:
            main_handler: Reference to main MovieUploadHandler instance
        """
        self.main_handler = main_handler
        self.session_service = main_handler.session_service
        self.noobz_api_service = main_handler.noobz_api_service
        logger.info("MovieUploadHandlerPart2 initialized")
    
    async def prompt_download_url(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Prompt user to enter download URL (optional).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Set state
            context.user_data['awaiting_movie_download_url'] = True
            
            # Send prompt
            prompt = MovieMessages.ask_download_url()
            await query.edit_message_text(prompt, parse_mode='HTML')
            
            logger.info(f"User {update.effective_user.id} prompted for download URL")
            
        except Exception as e:
            logger.error(f"Error in prompt_download_url: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def handle_download_url_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle download URL input from user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting download URL
            if not context.user_data.get('awaiting_movie_download_url', False):
                return
            
            user = update.effective_user
            download_url = update.message.text.strip()
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Check if user wants to skip
            if download_url.lower() in ['-', 'skip', 'no']:
                context.user_data['movie_upload']['download_url'] = None
                context.user_data['awaiting_movie_download_url'] = False
                
                success_text = "ℹ️ Download URL skipped\n\n"
                success_text += format_movie_state_summary(
                    context.user_data['movie_upload']
                )
                
                keyboard = MovieUploadKeyboards.movie_form(context.user_data['movie_upload'])
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=success_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                logger.info(f"User {user.id} skipped download URL")
                return
            
            # Validate URL
            if not InputValidator.validate_url(download_url):
                error_msg = ErrorMessages.invalid_input(
                    "Invalid URL format.\nPlease enter a valid HTTP/HTTPS URL or '-' to skip."
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                return
            
            # Save to state
            context.user_data['movie_upload']['download_url'] = download_url
            context.user_data['awaiting_movie_download_url'] = False
            
            # Show updated form
            success_text = "✅ Download URL set\n\n"
            success_text += format_movie_state_summary(
                context.user_data['movie_upload']
            )
            
            keyboard = MovieUploadKeyboards.movie_form(context.user_data['movie_upload'])
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} set download URL")
            
        except Exception as e:
            logger.error(f"Error in handle_download_url_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_movie_download_url'] = False
    
    async def confirm_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Show upload confirmation with movie preview.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            state = context.user_data.get('movie_upload', {})
            
            # Build confirmation message
            confirm_text = "📋 <b>Review & Confirm</b>\n\n"
            confirm_text += f"🎬 <b>{state['title']} ({state['year']})</b>\n"
            confirm_text += f"🆔 TMDB ID: {state['tmdb_id']}\n"
            confirm_text += f"🔗 Embed: {URLFormatters.truncate_url(state['embed_url'], 40)}\n"
            
            if state.get('download_url'):
                confirm_text += f"📥 Download: {URLFormatters.truncate_url(state['download_url'], 40)}\n"
            else:
                confirm_text += "📥 Download: <i>Not provided</i>\n"
            
            confirm_text += "\n⚠️ <b>Ready to upload?</b>"
            
            keyboard = MovieUploadKeyboards.upload_confirmation()
            
            await query.edit_message_text(
                confirm_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {update.effective_user.id} reviewing upload")
            
        except Exception as e:
            logger.error(f"Error in confirm_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def execute_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Execute movie upload to Noobz API.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            state = context.user_data.get('movie_upload', {})
            
            # Check session
            session = self.session_service.get_active_session(user.id)
            if not session:
                await query.edit_message_text(
                    "❌ Session expired. Use /start to login again."
                )
                return
            
            # Show uploading message
            await query.edit_message_text(
                "⏳ <b>Uploading movie...</b>\n\nPlease wait...",
                parse_mode='HTML'
            )
            
            # Upload to Noobz API
            result = await self.noobz_api_service.upload_movie(
                tmdb_id=state['tmdb_id'],
                embed_url=state['embed_url'],
                download_url=state.get('download_url')
            )
            
            # Debug: Log actual API response
            logger.info(f"API Response: success={result.get('success')}, message={result.get('message')}, data_keys={list(result.get('data', {}).keys())}")
            
            if result['success']:
                # Upload successful
                success_msg = MovieMessages.upload_success(
                    state['title'],
                    state['year'],
                    state['tmdb_id'],
                    URLFormatters.extract_domain(state['embed_url'])
                )
                
                keyboard = MovieUploadKeyboards.post_upload_actions()
                
                await query.edit_message_text(
                    success_msg,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                # Clear upload state
                context.user_data.pop('movie_upload', None)
                
                logger.info(f"User {user.id} uploaded movie: {state['title']} (TMDB: {state['tmdb_id']})")
                
            else:
                # Upload failed
                error_msg = result.get('message', 'Unknown error')
                
                # Check if movie already exists
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    fail_msg = MovieMessages.movie_exists()
                else:
                    fail_msg = MovieMessages.upload_error(error_msg)
                
                # Show back button
                keyboard = MainMenuKeyboards.back_and_home()
                
                await query.edit_message_text(
                    fail_msg,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                logger.warning(
                    f"User {user.id} movie upload failed: {error_msg} "
                    f"(TMDB: {state['tmdb_id']})"
                )
            
        except Exception as e:
            logger.error(f"Error in execute_upload: {e}", exc_info=True)
            
            error_msg = ErrorMessages.api_error()
            keyboard = MainMenuKeyboards.back_and_home()
            
            try:
                await query.edit_message_text(
                    error_msg,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            except:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
    
    async def cancel_upload(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Cancel movie upload and clear state.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Clear upload state
            context.user_data.pop('movie_upload', None)
            context.user_data.pop('awaiting_movie_tmdb_id', None)
            context.user_data.pop('awaiting_movie_embed_url', None)
            context.user_data.pop('awaiting_movie_download_url', None)
            
            # Show cancellation message
            from ui.keyboards_main_auth import MainMenuKeyboards
            
            session = self.session_service.get_active_session(update.effective_user.id)
            is_master = session['is_master'] if session else False
            
            keyboard = MainMenuKeyboards.main_menu(is_master)
            
            await query.edit_message_text(
                "❌ <b>Upload Cancelled</b>\n\nReturning to main menu...",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {update.effective_user.id} cancelled movie upload")
            
        except Exception as e:
            logger.error(f"Error in cancel_upload: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")


def register_handlers(application, session_service, tmdb_service, noobz_api_service):
    """
    Register movie upload handlers.
    
    Args:
        application: Telegram application instance
        session_service: Session management service
        tmdb_service: TMDB service
        noobz_api_service: Noobz API service
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Importing MovieUploadHandler...")
        from .movie_upload_handler import MovieUploadHandler
        logger.info("MovieUploadHandler imported successfully")
        
        # Create main handler
        logger.info("Creating main handler...")
        main_handler = MovieUploadHandler(session_service, tmdb_service, noobz_api_service)
        logger.info("Main handler created")
        
        # Create part 2 handler
        logger.info("Creating part 2 handler...")
        part2_handler = MovieUploadHandlerPart2(main_handler)
        logger.info("Part 2 handler created")
    except Exception as e:
        logger.error(f"Error creating movie handlers: {e}", exc_info=True)
        raise
    
    # Create unified message handler that routes based on state
    async def unified_movie_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Route to appropriate handler based on awaiting state"""
        logger.info("🎯 Unified movie input handler called")
        
        # Check which input we're awaiting
        if context.user_data.get('awaiting_movie_tmdb_id', False):
            logger.info("→ Routing to TMDB ID handler")
            await main_handler.handle_tmdb_id_input(update, context)
        elif context.user_data.get('awaiting_movie_embed_url', False):
            logger.info("→ Routing to Embed URL handler")
            await main_handler.handle_embed_url_input(update, context)
        elif context.user_data.get('awaiting_movie_download_url', False):
            logger.info("→ Routing to Download URL handler")
            await part2_handler.handle_download_url_input(update, context)
        else:
            logger.info("→ No movie input awaited, skipping")
    
    # Register SINGLE message handler in group 0
    logger.info("Registering unified movie input handler in group 0...")
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            unified_movie_input_handler
        ),
        group=0
    )
    
    logger.info("MovieUploadHandler registered successfully (group 0)")
    
    return main_handler, part2_handler

