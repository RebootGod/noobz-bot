"""
Password Manager Handler
Master-only features for password management (create, revoke, view stats).
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from services.session_service import SessionService
from services.auth_service import AuthService
from ui.messages import PasswordMessages, ErrorMessages
from ui.keyboards_password import PasswordManagerKeyboards, PasswordStatsKeyboards
from ui.formatters import PasswordFormatters, TimeFormatters
from utils.validators import InputValidator

logger = logging.getLogger(__name__)


class PasswordManagerHandler:
    """Handler for password management operations (Master only)."""
    
    def __init__(self, session_service: SessionService, auth_service: AuthService):
        """
        Initialize password manager handler.
        
        Args:
            session_service: Session management service
            auth_service: Authentication service
        """
        self.session_service = session_service
        self.auth_service = auth_service
        logger.info("PasswordManagerHandler initialized")
    
    async def show_password_manager(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Show password management main menu (Master only).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Check session and master access
            session = self.session_service.get_active_session(user.id)
            if not session:
                await query.edit_message_text(
                    "❌ Session expired. Use /start to login again."
                )
                return
            
            if not session['is_master']:
                await query.answer("❌ Access denied. Master only.", show_alert=True)
                return
            
            # Get all passwords
            passwords = self.auth_service.get_all_passwords()
            
            # Format password list
            password_list = PasswordFormatters.format_password_list(passwords)
            
            # Get keyboard
            keyboard = PasswordManagerKeyboards.main_menu()
            
            await query.edit_message_text(
                password_list,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"Master {user.id} opened password manager")
            
        except Exception as e:
            logger.error(f"Error in show_password_manager: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error opening password manager")
    
    async def prompt_password_type(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Prompt master to select password type (Master/Admin).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Check master access
            session = self.session_service.get_active_session(update.effective_user.id)
            if not session or not session['is_master']:
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Show password type selection
            keyboard = PasswordManagerKeyboards.password_type_selection()
            
            await query.edit_message_text(
                "➕ <b>Create New Password</b>\n\n"
                "Select password type:",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"Master {update.effective_user.id} selecting password type")
            
        except Exception as e:
            logger.error(f"Error in prompt_password_type: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def start_password_creation(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Start password creation flow.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            # Parse callback data: create_password_master or create_password_admin
            password_type = query.data.split('_')[2]  # 'master' or 'admin'
            
            # Check master access
            session = self.session_service.get_active_session(update.effective_user.id)
            if not session or not session['is_master']:
                await query.answer("❌ Access denied", show_alert=True)
                return
            
            # Set state
            context.user_data['creating_password_type'] = password_type
            context.user_data['awaiting_new_password'] = True
            
            # Show warning for master passwords
            prompt = PasswordMessages.ask_new_password(password_type)
            if password_type == 'master':
                prompt += "\n\n" + PasswordMessages.master_warning()
            
            await query.edit_message_text(
                prompt,
                parse_mode='HTML'
            )
            
            logger.info(
                f"Master {update.effective_user.id} creating {password_type} password"
            )
            
        except Exception as e:
            logger.error(f"Error in start_password_creation: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error")
    
    async def handle_new_password_input(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle new password input.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting new password
            if not context.user_data.get('awaiting_new_password', False):
                return
            
            user = update.effective_user
            password = update.message.text.strip()
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Validate password
            validation_result = InputValidator.validate_password(password)
            if not validation_result['valid']:
                error_msg = f"❌ {validation_result['error']}"
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                return
            
            # Save password for confirmation
            context.user_data['new_password_pending'] = password
            context.user_data['awaiting_new_password'] = False
            context.user_data['awaiting_password_confirmation'] = True
            
            # Ask for confirmation
            confirm_msg = PasswordMessages.ask_confirm_password()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=confirm_msg,
                parse_mode='HTML'
            )
            
            logger.info(f"Master {user.id} entered new password, awaiting confirmation")
            
        except Exception as e:
            logger.error(f"Error in handle_new_password_input: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_new_password'] = False
    
    async def handle_password_confirmation(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle password confirmation input.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting confirmation
            if not context.user_data.get('awaiting_password_confirmation', False):
                return
            
            user = update.effective_user
            confirmation = update.message.text.strip()
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            pending_password = context.user_data.get('new_password_pending')
            
            # Check if passwords match
            if confirmation != pending_password:
                error_msg = PasswordMessages.password_mismatch()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                # Reset to password input
                context.user_data['awaiting_password_confirmation'] = False
                context.user_data['awaiting_new_password'] = True
                return
            
            # Passwords match - ask for notes
            context.user_data['awaiting_password_confirmation'] = False
            context.user_data['awaiting_password_notes'] = True
            
            notes_msg = PasswordMessages.ask_password_notes()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=notes_msg,
                parse_mode='HTML'
            )
            
            logger.info(f"Master {user.id} confirmed password, awaiting notes")
            
        except Exception as e:
            logger.error(f"Error in handle_password_confirmation: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_password_confirmation'] = False
    
    async def handle_password_notes(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle password notes input and create password.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Check if we're expecting notes
            if not context.user_data.get('awaiting_password_notes', False):
                return
            
            user = update.effective_user
            notes = update.message.text.strip()
            
            # Allow skipping notes with "-"
            if notes == '-':
                notes = None
            
            # Delete user's message
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
            
            # Get password data
            password = context.user_data.get('new_password_pending')
            password_type = context.user_data.get('creating_password_type')
            
            # Create password
            result = self.auth_service.create_password(
                password=password,
                password_type=password_type,
                created_by_telegram_id=user.id,
                notes=notes
            )
            
            if not result['success']:
                error_msg = ErrorMessages.api_error(result.get('message'))
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=error_msg,
                    parse_mode='HTML'
                )
                # Clear state
                context.user_data.pop('new_password_pending', None)
                context.user_data.pop('creating_password_type', None)
                context.user_data['awaiting_password_notes'] = False
                return
            
            # Success
            password_data = result['password']
            success_msg = PasswordMessages.password_created(
                password_data['password_hint'],
                password_type
            )
            
            keyboard = PasswordManagerKeyboards.password_creation_success()
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=success_msg,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            # Clear state
            context.user_data.pop('new_password_pending', None)
            context.user_data.pop('creating_password_type', None)
            context.user_data['awaiting_password_notes'] = False
            
            logger.info(
                f"Master {user.id} created {password_type} password "
                f"(hint: {password_data['password_hint']})"
            )
            
        except Exception as e:
            logger.error(f"Error in handle_password_notes: {e}", exc_info=True)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ErrorMessages.generic_error()
            )
            context.user_data['awaiting_password_notes'] = False


def register_handlers(application, session_service: SessionService, auth_service: AuthService):
    """
    Register password manager handlers.
    
    Args:
        application: Telegram application instance
        session_service: Session management service
        auth_service: Authentication service
    """
    handler = PasswordManagerHandler(session_service, auth_service)
    
    # Register message handlers for password input
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler.handle_new_password_input
        )
    )
    
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler.handle_password_confirmation
        )
    )
    
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handler.handle_password_notes
        )
    )
    
    logger.info("PasswordManagerHandler registered successfully")
    
    return handler
