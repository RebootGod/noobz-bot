"""
Help Handler
Handles all help and information screens.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from ui.keyboards_main_auth import HelpKeyboards

logger = logging.getLogger(__name__)


class HelpHandler:
    """Handler for help screens and documentation"""

    def __init__(self):
        """Initialize help handler"""
        pass

    async def handle_help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Help menu button"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "❓ <b>Help & Information</b>\n\n"
            "Select a topic to learn more:",
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_menu()
        )

    async def handle_help_movie(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Movie Upload Help"""
        query = update.callback_query
        await query.answer()
        
        help_text = (
            "🎬 <b>Movie Upload Help</b>\n\n"
            "<b>Step-by-step guide:</b>\n\n"
            "1️⃣ <b>Set TMDB ID</b>\n"
            "   • Find movie on themoviedb.org\n"
            "   • Copy ID from URL (e.g., 550 for Fight Club)\n"
            "   • Bot will fetch movie info automatically\n\n"
            "2️⃣ <b>Set Embed URL</b>\n"
            "   • Required for streaming\n"
            "   • Format: https://vidsrc.to/embed/movie/{TMDB_ID}\n"
            "   • Example: https://vidsrc.to/embed/movie/550\n\n"
            "3️⃣ <b>Set Download URL</b> (Optional)\n"
            "   • Direct download link\n"
            "   • Use '-' to skip\n\n"
            "4️⃣ <b>Upload</b>\n"
            "   • Review all info\n"
            "   • Click Upload Now\n"
            "   • Wait for confirmation\n\n"
            "⚠️ <b>Important:</b>\n"
            "• TMDB ID must be valid\n"
            "• Movie will be auto-published\n"
            "• Can't edit after upload"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_back()
        )

    async def handle_help_series(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Series Upload Help"""
        query = update.callback_query
        await query.answer()
        
        help_text = (
            "📺 <b>Series Upload Help</b>\n\n"
            "<b>Step-by-step guide:</b>\n\n"
            "1️⃣ <b>Enter Series TMDB ID</b>\n"
            "   • Find series on themoviedb.org\n"
            "   • Copy ID from URL (e.g., 1396 for Breaking Bad)\n"
            "   • Bot creates series automatically\n\n"
            "2️⃣ <b>Select Season</b>\n"
            "   • Choose season to upload\n"
            "   • Bot shows episode status\n\n"
            "3️⃣ <b>Choose Upload Mode</b>\n"
            "   • <b>Bulk Upload:</b> Multiple episodes at once\n"
            "   • <b>Single Episode:</b> One episode at a time\n\n"
            "4️⃣ <b>Upload Episodes</b>\n"
            "   • Follow format instructions\n"
            "   • Bot validates before upload\n"
            "   • Progress shown in real-time\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Series must exist in TMDB\n"
            "• Bot checks duplicate episodes\n"
            "• Episodes auto-published\n\n"
            "💡 <b>Tip:</b> Use bulk upload for faster workflow!"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_back()
        )

    async def handle_help_bulk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Bulk Upload Help"""
        query = update.callback_query
        await query.answer()
        
        help_text = (
            "📦 <b>Bulk Upload Help</b>\n\n"
            "<b>Format per line:</b>\n"
            "<code>EP | EMBED_URL | DOWNLOAD_URL</code>\n\n"
            "<b>Example:</b>\n"
            "<code>1 | https://vidsrc.to/embed/tv/1396/1/1 | -</code>\n"
            "<code>2 | https://vidsrc.to/embed/tv/1396/1/2 | https://dl.../ep02.mp4</code>\n"
            "<code>3 | https://vidsrc.to/embed/tv/1396/1/3 | -</code>\n\n"
            "<b>Rules:</b>\n"
            "• Use <code>|</code> as separator\n"
            "• Episode number = 1-999\n"
            "• Use <code>-</code> for no download URL\n"
            "• Max 20 episodes per upload\n"
            "• One episode per line\n\n"
            "<b>Process:</b>\n"
            "1️⃣ Paste all episodes\n"
            "2️⃣ Bot validates format\n"
            "3️⃣ Review preview\n"
            "4️⃣ Confirm upload\n"
            "5️⃣ Real-time progress shown\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Skip existing complete episodes\n"
            "• Bot will update episodes without URLs\n"
            "• Can't cancel after confirmation"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_back()
        )

    async def handle_help_manual(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Manual Mode Help"""
        query = update.callback_query
        await query.answer()
        
        help_text = (
            "✍️ <b>Manual Mode Help</b>\n\n"
            "<b>When to use:</b>\n"
            "• TMDB data incomplete\n"
            "• Old series without episode info\n"
            "• Custom episode titles needed\n\n"
            "<b>Full Format:</b>\n"
            "<code>EP | TITLE | EMBED_URL | DL_URL</code>\n\n"
            "<b>Quick Format:</b>\n"
            "<code>EP | EMBED_URL | DL_URL</code>\n"
            "(Uses 'Episode X' as title)\n\n"
            "<b>Example (Full):</b>\n"
            "<code>1 | Pilot Episode | https://vidsrc.to/... | -</code>\n"
            "<code>2 | The Beginning | https://vidsrc.to/... | -</code>\n\n"
            "<b>Example (Quick):</b>\n"
            "<code>1 | https://vidsrc.to/... | -</code>\n"
            "<code>2 | https://vidsrc.to/... | https://dl.../ep02.mp4</code>\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Manual mode = No TMDB validation\n"
            "• Episode numbers must be unique\n"
            "• Can mix full and quick format\n"
            "• Same rules as bulk upload"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_back()
        )

    async def handle_help_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle Password Manager Help"""
        query = update.callback_query
        await query.answer()
        
        help_text = (
            "🔐 <b>Password Manager Help</b>\n\n"
            "<b>Master Access Only</b>\n\n"
            "<b>Features:</b>\n\n"
            "1️⃣ <b>Create Password</b>\n"
            "   • Choose type: Master or Admin\n"
            "   • Min 8 characters\n"
            "   • Mix letters & numbers\n"
            "   • Add optional notes\n\n"
            "2️⃣ <b>View Passwords</b>\n"
            "   • See all active passwords\n"
            "   • Check last used time\n"
            "   • View upload count\n\n"
            "3️⃣ <b>Revoke Password</b>\n"
            "   • Select password to revoke\n"
            "   • Confirm action\n"
            "   • Terminates active sessions\n\n"
            "4️⃣ <b>View Stats</b>\n"
            "   • Total uploads per password\n"
            "   • Activity timeline\n"
            "   • Usage breakdown\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Master passwords = Full access\n"
            "• Admin passwords = Upload only\n"
            "• Revoked passwords can't login\n"
            "• Sessions expire after 24 hours"
        )
        
        await query.edit_message_text(
            help_text,
            parse_mode='HTML',
            reply_markup=HelpKeyboards.help_back()
        )


def register_handlers(application):
    """
    Register help handlers.
    
    Args:
        application: Telegram application instance
    """
    handler = HelpHandler()
    
    logger.info("HelpHandler registered successfully")
    
    return handler
