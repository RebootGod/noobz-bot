"""
Start Command Handler
Handles /start command, checks existing session, and shows appropriate welcome/main menu.
"""

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler
from datetime import datetime

from services.session_service import SessionService
from ui.messages import AuthMessages
from ui.keyboards_main_auth import MainMenuKeyboards
from ui.formatters import TimeFormatters

logger = logging.getLogger(__name__)


class StartHandler:
    """Handler for /start command and initial user interaction."""
    
    def __init__(self, session_service: SessionService):
        """
        Initialize start handler.
        
        Args:
            session_service: Session management service
        """
        self.session_service = session_service
        logger.info("StartHandler initialized")
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.
        Checks if user has active session, shows welcome or main menu.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            logger.info(f"User {user.id} ({user.username or 'no_username'}) started bot")
            
            # Check for active session
            session = self.session_service.get_active_session(user.id)
            
            if session:
                # User has active session, show main menu
                await self._show_main_menu(update, context, session)
            else:
                # No active session, show welcome and request authentication
                await self._show_welcome(update, context)
                
        except Exception as e:
            logger.error(f"Error in handle_start: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
    
    async def _show_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Show welcome message for new/unauthenticated user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user = update.effective_user
        
        # Send welcome message
        welcome_text = AuthMessages.welcome()
        await update.message.reply_text(
            welcome_text,
            parse_mode='HTML'
        )
        
        # Prompt for password
        auth_prompt = "🔐 Please enter your password to continue:"
        await update.message.reply_text(auth_prompt)
        
        # Set conversation state for auth handler
        context.user_data['awaiting_password'] = True
        
        logger.info(f"Showed welcome message to user {user.id}")
    
    async def _show_main_menu(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        session: dict
    ) -> None:
        """
        Show main menu for authenticated user.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            session: Active session data
        """
        user = update.effective_user
        is_master = session['is_master']
        
        # Calculate session expiry time
        expires_at = session['expires_at']
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        time_remaining = TimeFormatters.format_time_remaining(expires_at.isoformat())
        
        # Build greeting message
        greeting = f"👋 Welcome back"
        if is_master:
            greeting += ", <b>Master</b>!"
        else:
            greeting += "!"
        
        greeting += f"\n\n📱 Your session is active.\n⏰ Expires in: {time_remaining}"
        
        # Get main menu keyboard
        keyboard = MainMenuKeyboards.main_menu(is_master)
        
        # Send greeting with main menu
        await update.message.reply_text(
            greeting,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        
        logger.info(f"Showed main menu to user {user.id} (master={is_master})")
    
    async def handle_home(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle "Home" button callback - return to main menu.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            query = update.callback_query
            await query.answer()
            
            user = update.effective_user
            
            # Check active session
            session = self.session_service.get_active_session(user.id)
            
            if not session:
                # Session expired
                expired_message = AuthMessages.session_expired()
                await query.edit_message_text(
                    expired_message,
                    parse_mode='HTML'
                )
                
                # Prompt for re-authentication
                await query.message.reply_text(
                    "🔐 Please enter your password to continue:"
                )
                context.user_data['awaiting_password'] = True
                
                logger.warning(f"User {user.id} session expired on home callback")
                return
            
            # Show main menu
            is_master = session['is_master']
            
            # Calculate time remaining
            expires_at = session['expires_at']
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)
            
            time_remaining = TimeFormatters.format_time_remaining(expires_at.isoformat())
            
            greeting = f"🏠 <b>Main Menu</b>\n\n⏰ Session expires in: {time_remaining}"
            
            keyboard = MainMenuKeyboards.main_menu(is_master)
            
            await query.edit_message_text(
                greeting,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"User {user.id} returned to home")
            
        except Exception as e:
            logger.error(f"Error in handle_home: {e}", exc_info=True)
            await update.callback_query.answer("❌ Error returning to home")
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle My Stats button"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Check session
        session = self.session_service.get_active_session(user.id)
        if not session:
            await query.edit_message_text(
                "⏰ Your session has expired.\n\nPlease use /start to authenticate again."
            )
            return
        
        # TODO: Implement stats display
        await query.edit_message_text(
            "📊 <b>My Stats</b>\n\n"
            "🚧 This feature is coming soon!\n\n"
            "You'll be able to see:\n"
            "• Total uploads\n"
            "• Movies uploaded\n"
            "• Series created\n"
            "• Episodes uploaded\n"
            "• Recent activity",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="home")
            ]])
        )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Help button - redirect to HelpHandler"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        # Check session
        session = self.session_service.get_active_session(user.id)
        if not session:
            await query.edit_message_text(
                "⏰ Your session has expired.\n\nPlease use /start to authenticate again."
            )
            return
        
        # Import and use HelpHandler
        from handlers.help_handler import HelpHandler
        help_handler = HelpHandler()
        await help_handler.handle_help_menu(update, context)


def register_handlers(application, session_service: SessionService):
    """
    Register start command and home callback handlers.
    
    Args:
        application: Telegram application instance
        session_service: Session management service
    """
    handler = StartHandler(session_service)
    
    # Register /start command
    application.add_handler(CommandHandler("start", handler.handle_start))
    
    logger.info("StartHandler registered successfully")
    
    return handler
