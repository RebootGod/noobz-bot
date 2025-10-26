"""
Authentication Handler
Handles password input, validation, and session creation.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from services.auth_service import AuthService
from services.session_service import SessionService
from ui.messages import AuthMessages
from ui.keyboards_main_auth import MainMenuKeyboards
from utils.validators import InputValidator

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handler for authentication flow."""
    
    def __init__(self, auth_service: AuthService, session_service: SessionService):
        """
        Initialize authentication handler.
        
        Args:
            auth_service: Authentication service
            session_service: Session management service
        """
        self.auth_service = auth_service
        self.session_service = session_service
        logger.info("AuthHandler initialized")
    
    async def handle_password_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle password input from user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting password input
            if not context.user_data.get('awaiting_password', False):
                return  # Not in auth flow, ignore
            
            user = update.effective_user
            chat_id = update.effective_chat.id
            password = update.message.text.strip()
            
            # Delete user's password message for security
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete password message: {e}")
            
            logger.info(f"User {user.id} attempting authentication")
            
            # Validate password format
            validation_result = InputValidator.validate_password(password)
            if not validation_result['valid']:
                await self._handle_auth_failure(
                    update, 
                    context,
                    validation_result['error']
                )
                return
            
            # Verify password
            auth_result = self.auth_service.verify_password_attempt(password)
            
            if not auth_result['valid']:
                await self._handle_auth_failure(update, context, auth_result.get('error'))
                return
            
            # Password correct, create session
            password_id = auth_result['password_id']
            password_type = auth_result['password_type']
            is_master = auth_result['is_master']
            
            session = self.session_service.create_session(
                telegram_user_id=user.id,
                telegram_username=user.username,
                password_id=password_id,
                is_master=is_master
            )
            
            if not session:
                await self._handle_auth_failure(
                    update, 
                    context,
                    "Failed to create session. Please try again."
                )
                return
            
            # Clear auth state
            context.user_data['awaiting_password'] = False
            
            # Authentication successful
            await self._handle_auth_success(update, context, is_master)
            
            logger.info(f"User {user.id} authenticated successfully (master={is_master})")
            
        except Exception as e:
            logger.error(f"Error in handle_password_input: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred during authentication. Please try again."
            )
            context.user_data['awaiting_password'] = False
    
    async def _handle_auth_success(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        is_master: bool
    ) -> None:
        """
        Handle successful authentication.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            is_master: Whether user authenticated with master password
        """
        # Send success message
        success_message = AuthMessages.auth_success(is_master)
        
        # Get main menu keyboard
        keyboard = MainMenuKeyboards.main_menu(is_master)
        
        # Send success message with main menu
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=success_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    async def _handle_auth_failure(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        error_message: str = None
    ) -> None:
        """
        Handle failed authentication attempt.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            error_message: Optional custom error message
        """
        # Send failure message
        if error_message:
            failure_message = f"❌ {error_message}"
        else:
            failure_message = AuthMessages.auth_failed()
        
        # Get retry keyboard
        keyboard = MainMenuKeyboards.auth_retry()
        
        # Send failure message with retry option
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=failure_message,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        # Keep auth state active for retry
        context.user_data['awaiting_password'] = True
    
    async def handle_retry_auth(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle retry authentication button callback.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Set auth state
            context.user_data['awaiting_password'] = True
            
            # Prompt for password
            await query.edit_message_text(
                "🔐 Please enter your password:",
                parse_mode='HTML'
            )
            
            logger.info(f"User {update.effective_user.id} retrying authentication")
            
        except Exception as e:
            logger.error(f"Error in handle_retry_auth: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error. Please try /start again.")
    
    async def handle_cancel_auth(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle cancel authentication button callback.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Clear auth state
            context.user_data['awaiting_password'] = False
            
            # Send cancellation message
            await query.edit_message_text(
                "❌ Authentication cancelled.\n\n"
                "Use /start to begin again.",
                parse_mode='HTML'
            )
            
            logger.info(f"User {update.effective_user.id} cancelled authentication")
            
        except Exception as e:
            logger.error(f"Error in handle_cancel_auth: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def handle_logout(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle logout - terminate active session.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Delete session
            deleted = self.session_service.delete_session(user.id)
            
            # Clear user data
            context.user_data.clear()
            
            if deleted:
                message = (
                    "✅ <b>Logged Out</b>\n\n"
                    "Your session has been terminated.\n\n"
                    "Use /start to log in again."
                )
            else:
                message = (
                    "ℹ️ No active session found.\n\n"
                    "Use /start to begin."
                )
            
            await query.edit_message_text(
                message,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} logged out")
            
        except Exception as e:
            logger.error(f"Error in handle_logout: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error during logout")


def register_handlers(application, auth_service: AuthService, session_service: SessionService):
    """
    Register authentication handlers.
    
    Args:
        application: Telegram application instance
        auth_service: Authentication service
        session_service: Session management service
    """
    handler = AuthHandler(auth_service, session_service)
    
    # Register message handler for password input
    # Use group 1 (lower priority) so other handlers can check first
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler.handle_password_input
        ),
        group=1  # Lower priority - only catches if no other handler processed it
    )
    
    logger.info("AuthHandler registered successfully (group 1)")
    
    return handler
