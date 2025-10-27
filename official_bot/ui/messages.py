"""
Module: UI Messages
Purpose: Message templates for bot responses

Provides reusable message templates for:
- Welcome and authentication messages
- Success/error notifications
- Help documentation
- Upload instructions

Author: RebootGod
Date: 2025
"""

from typing import Dict, Any, Optional


class AuthMessages:
    """Authentication-related messages"""
    
    @staticmethod
    def welcome() -> str:
        """Welcome message for /start command"""
        return (
            "┌─────────────────────────────────┐\n"
            "│ 🎬 Noobz Upload Bot             │\n"
            "│                                 │\n"
            "│ Welcome! This bot helps you     │\n"
            "│ upload movies and series.       │\n"
            "│                                 │\n"
            "│ 🔒 Authentication Required      │\n"
            "└─────────────────────────────────┘\n\n"
            "Please enter your password:"
        )
    
    @staticmethod
    def auth_success(is_master: bool = False) -> str:
        """Success message after authentication"""
        if is_master:
            return (
                "✅ Master access granted!\n"
                "Welcome, Master!\n\n"
                "Your session will expire in 24 hours."
            )
        return (
            "✅ Authentication successful!\n"
            "Welcome back!\n\n"
            "Your session will expire in 24 hours."
        )
    
    @staticmethod
    def auth_failed() -> str:
        """Failed authentication message"""
        return "❌ Invalid password. Please try again."
    
    @staticmethod
    def session_expired() -> str:
        """Session expired message"""
        return (
            "⏰ Your session has expired.\n\n"
            "Please use /start to authenticate again."
        )
    
    @staticmethod
    def already_authenticated() -> str:
        """Already authenticated message"""
        return "✅ You are already authenticated!"


class MovieMessages:
    """Movie upload-related messages"""
    
    @staticmethod
    def ask_tmdb_id() -> str:
        """Ask for TMDB ID"""
        return (
            "Please enter TMDB ID:\n\n"
            "Example: 550 (for Fight Club)\n\n"
            "You can find TMDB ID from the URL:\n"
            "https://www.themoviedb.org/movie/550"
        )
    
    @staticmethod
    def ask_embed_url() -> str:
        """Ask for embed URL"""
        return (
            "Please enter Embed URL:\n\n"
            "Example: https://vidsrc.to/embed/movie/550"
        )
    
    @staticmethod
    def ask_download_url() -> str:
        """Ask for download URL (optional)"""
        return (
            "Please enter Download URL (optional):\n\n"
            "Example: https://dl.noobz.space/fight-club.mp4\n\n"
            "Or click Skip to continue without download URL."
        )
    
    @staticmethod
    def tmdb_fetching() -> str:
        """Fetching TMDB data"""
        return "⏳ Fetching movie info from TMDB..."
    
    @staticmethod
    def tmdb_fetch_failed() -> str:
        """TMDB fetch failed"""
        return (
            "❌ Failed to fetch movie data from TMDB.\n\n"
            "Possible reasons:\n"
            "• Invalid TMDB ID\n"
            "• Movie not found\n"
            "• TMDB API error\n\n"
            "Please try again with a valid TMDB ID."
        )
    
    @staticmethod
    def upload_processing() -> str:
        """Upload in progress"""
        return "⏳ Uploading movie to database..."
    
    @staticmethod
    def upload_success(movie_data: Dict[str, Any]) -> str:
        """Upload success message"""
        title = movie_data.get('title', 'Unknown')
        year = movie_data.get('year', 'N/A')
        tmdb_id = movie_data.get('tmdb_id', 'N/A')
        embed_url = movie_data.get('embed_url', '')
        
        # Extract domain from embed URL
        domain = embed_url.split('/')[2] if '/' in embed_url else 'N/A'
        
        return (
            f"✅ Movie uploaded successfully!\n\n"
            f"🎬 {title} ({year})\n"
            f"🆔 TMDB ID: {tmdb_id}\n"
            f"🔗 Embed: {domain}\n"
            f"⏳ Status: Processing...\n\n"
            f"The movie will be published automatically."
        )
    
    @staticmethod
    def upload_error(error_message: str) -> str:
        """Upload error message"""
        return f"❌ Upload failed:\n\n{error_message}"
    
    @staticmethod
    def movie_exists() -> str:
        """Movie already exists"""
        return (
            "⚠️ This movie already exists in the database.\n\n"
            "Please check the website before uploading."
        )


class SeriesMessages:
    """Series upload-related messages"""
    
    @staticmethod
    def ask_tmdb_id() -> str:
        """Ask for series TMDB ID"""
        return (
            "Please enter Series TMDB ID:\n\n"
            "Example: 1396 (for Breaking Bad)\n\n"
            "You can find TMDB ID from the URL:\n"
            "https://www.themoviedb.org/tv/1396"
        )
    
    @staticmethod
    def tmdb_fetching() -> str:
        """Fetching series data"""
        return "⏳ Fetching series info from TMDB..."
    
    @staticmethod
    def tmdb_fetch_error(tmdb_id: int) -> str:
        """TMDB fetch failed for series"""
        return (
            f"❌ Failed to fetch series data from TMDB.\n\n"
            f"TMDB ID: {tmdb_id}\n\n"
            f"Possible reasons:\n"
            f"• Invalid TMDB ID\n"
            f"• Series not found\n"
            f"• TMDB API error\n\n"
            f"Please try again with a valid TMDB ID."
        )
    
    @staticmethod
    def series_creating() -> str:
        """Creating series in database"""
        return "⏳ Creating series in database..."
    
    @staticmethod
    def series_created(title: str) -> str:
        """Series created successfully"""
        return (
            f"✅ Series created!\n\n"
            f"📺 {title}\n\n"
            f"Select season to upload:"
        )
    
    @staticmethod
    def series_create_error(error_message: str) -> str:
        """Series creation failed"""
        return (
            f"❌ Failed to create series!\n\n"
            f"Error: {error_message}\n\n"
            f"Please try again or contact support."
        )
    
    @staticmethod
    def series_exists(title: str) -> str:
        """Series already exists"""
        return (
            f"⚠️ Series already exists!\n\n"
            f"📺 {title}\n\n"
            f"This series already exists in the database.\n"
            f"You can still add episodes to existing seasons."
        )
    
    @staticmethod
    def checking_episode_status(series_title: str, season_number: int) -> str:
        """Checking episode status"""
        return (
            f"⏳ Checking episode status...\n\n"
            f"📺 {series_title}\n"
            f"🔢 Season {season_number}"
        )
    
    @staticmethod
    def tmdb_data_unavailable() -> str:
        """TMDB data not available"""
        return (
            "⚠️ TMDB Data Incomplete\n\n"
            "This season has no episode data on TMDB.\n"
            "You can use Manual Mode to upload episodes."
        )


class EpisodeMessages:
    """Episode upload-related messages"""
    
    @staticmethod
    def bulk_upload_instructions(series_title: str, season_number: int, episode_count: int) -> str:
        """Bulk upload instructions"""
        return (
            f"┌─────────────────────────────────┐\n"
            f"│ 📦 Bulk Episode Upload          │\n"
            f"│                                 │\n"
            f"│ Series: {series_title[:20]}{'...' if len(series_title) > 20 else ''}│\n"
            f"│ Season: {season_number}                       │\n"
            f"│ Episodes to upload: {episode_count}           │\n"
            f"│                                 │\n"
            f"│ Format (one per line):          │\n"
            f"│ EP | EMBED_URL | DL_URL         │\n"
            f"│                                 │\n"
            f"│ Use \"-\" for no download URL     │\n"
            f"└─────────────────────────────────┘\n\n"
            f"Example:\n"
            f"2 | https://vidsrc.to/embed/tv/1396/1/2 | -\n"
            f"3 | https://vidsrc.to/embed/tv/1396/1/3 | https://dl.../s01e03.mp4"
        )
    
    @staticmethod
    def manual_mode_instructions(mode: str = "quick") -> str:
        """Manual mode upload instructions"""
        if mode == "full":
            return (
                "📝 Full Mode\n\n"
                "Format per line:\n"
                "EP | TITLE | EMBED_URL | DOWNLOAD_URL\n\n"
                "Example:\n"
                "1 | Pilot | https://vidsrc.to/... | -\n"
                "2 | Episode 2 | https://vidsrc.to/... | https://dl.../ep02.mp4"
            )
        else:
            return (
                "⚡ Quick Mode\n\n"
                "Format per line:\n"
                "EP | EMBED_URL | DOWNLOAD_URL\n\n"
                "Quick mode uses \"Episode X\" as default title.\n\n"
                "Example:\n"
                "1 | https://vidsrc.to/... | -\n"
                "2 | https://vidsrc.to/... | https://dl.../ep02.mp4"
            )
    
    @staticmethod
    def validating() -> str:
        """Validating episode data"""
        return "📊 Validating episodes..."
    
    @staticmethod
    def validation_result(valid_count: int, error_count: int, errors: list = None) -> str:
        """Validation result"""
        msg = f"✅ {valid_count} episodes valid\n"
        
        if error_count > 0:
            msg += f"⚠️ {error_count} errors\n\n"
            if errors:
                msg += "Errors:\n"
                for error in errors[:5]:  # Show first 5 errors
                    msg += f"• Line {error.get('line', '?')}: {error.get('message', 'Unknown error')}\n"
        
        return msg
    
    @staticmethod
    def upload_progress(current: int, total: int, episode_number: int) -> str:
        """Upload progress message"""
        percentage = int((current / total) * 100)
        bar_length = 6
        filled = int((current / total) * bar_length)
        bar = "▓" * filled + "░" * (bar_length - filled)
        
        return (
            f"⏳ Uploading episodes...\n"
            f"{bar} {percentage}% ({current}/{total})\n\n"
            f"Current: Episode {episode_number}"
        )
    
    @staticmethod
    def upload_summary(succeeded: int, failed: int, total: int) -> str:
        """Upload summary"""
        return (
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 Upload Summary:\n"
            f"✅ Success: {succeeded} episodes\n"
            f"❌ Failed: {failed} episodes\n"
            f"⏳ Processing in background...\n\n"
            f"Episodes will be published automatically."
        )


class PasswordMessages:
    """Password management messages"""
    
    @staticmethod
    def ask_new_password() -> str:
        """Ask for new password"""
        return (
            "Please enter new password:\n\n"
            "Requirements:\n"
            "• Minimum 8 characters\n"
            "• Mix of letters and numbers\n"
            "• No special characters required"
        )
    
    @staticmethod
    def ask_confirm_password() -> str:
        """Ask to confirm password"""
        return "Please confirm password:"
    
    @staticmethod
    def ask_password_notes() -> str:
        """Ask for password notes (optional)"""
        return (
            "Optional: Add notes\n\n"
            "Example: \"Password for John\"\n\n"
            "Or click Skip to continue without notes."
        )
    
    @staticmethod
    def password_mismatch() -> str:
        """Password confirmation mismatch"""
        return "❌ Passwords do not match. Please try again."
    
    @staticmethod
    def password_weak() -> str:
        """Weak password warning"""
        return (
            "❌ Password too weak.\n\n"
            "Requirements:\n"
            "• Minimum 8 characters\n"
            "• Mix of letters and numbers"
        )
    
    @staticmethod
    def password_created(hint: str, password_type: str, notes: Optional[str] = None) -> str:
        """Password created successfully"""
        msg = (
            f"✅ Password Created!\n\n"
            f"Password: {hint}\n"
            f"Type: {password_type.title()}\n"
            f"Created: Oct 26, 2025\n"
        )
        
        if notes:
            msg += f"Notes: {notes}\n"
        
        msg += "\n⚠️ Save this password securely!\nIt will not be shown again."
        
        return msg
    
    @staticmethod
    def password_revoked(hint: str) -> str:
        """Password revoked successfully"""
        return (
            f"✅ Password Revoked\n\n"
            f"Password {hint} has been revoked.\n"
            f"Active sessions terminated."
        )
    
    @staticmethod
    def master_warning() -> str:
        """Warning for master password creation"""
        return (
            "⚠️ Warning: Master passwords have full access\n"
            "including password management!"
        )


class HelpMessages:
    """Help documentation messages"""
    
    @staticmethod
    def main_help() -> str:
        """Main help message"""
        return (
            "📚 Noobz Upload Bot Help\n\n"
            "This bot allows you to upload movies and series\n"
            "to the Noobz platform.\n\n"
            "Available Commands:\n"
            "• /start - Start the bot and authenticate\n"
            "• /help - Show this help message\n\n"
            "Features:\n"
            "• 🎥 Upload movies with TMDB integration\n"
            "• 📺 Upload series with season/episode management\n"
            "• 📦 Bulk upload multiple episodes at once\n"
            "• 🔐 Secure password-based authentication\n"
            "• 📊 Track your upload statistics\n\n"
            "Select a topic to learn more:"
        )
    
    @staticmethod
    def movie_help() -> str:
        """Movie upload help"""
        return (
            "🎬 Movie Upload Help\n\n"
            "Steps:\n"
            "1. Click \"Upload Movie\" from main menu\n"
            "2. Enter TMDB ID of the movie\n"
            "3. Enter embed URL\n"
            "4. (Optional) Enter download URL\n"
            "5. Confirm and upload\n\n"
            "Tips:\n"
            "• Find TMDB ID from themoviedb.org URL\n"
            "• Movie will be published automatically"
        )
    
    @staticmethod
    def series_help() -> str:
        """Series upload help"""
        return (
            "📺 Series Upload Help\n\n"
            "Steps:\n"
            "1. Click \"Upload Series\" from main menu\n"
            "2. Enter TMDB ID of the series\n"
            "3. Select season to upload\n"
            "4. Choose bulk or single episode mode\n"
            "5. Follow the upload instructions\n\n"
            "Tips:\n"
            "• Series data is fetched from TMDB\n"
            "• You can upload multiple episodes at once\n"
            "• Check episode status before uploading"
        )
    
    @staticmethod
    def bulk_help() -> str:
        """Bulk upload help"""
        return (
            "📦 Bulk Upload Help\n\n"
            "Format:\n"
            "EP | EMBED_URL | DOWNLOAD_URL\n\n"
            "Rules:\n"
            "• One episode per line\n"
            "• Use pipe (|) as separator\n"
            "• Use \"-\" for no download URL\n"
            "• Maximum 20 episodes per batch\n\n"
            "Example:\n"
            "1 | https://vidsrc.to/... | -\n"
            "2 | https://vidsrc.to/... | https://dl.../ep02.mp4"
        )


class ErrorMessages:
    """Error messages"""
    
    @staticmethod
    def generic_error() -> str:
        """Generic error message"""
        return "❌ An error occurred. Please try again."
    
    @staticmethod
    def invalid_input() -> str:
        """Invalid input error"""
        return "❌ Invalid input. Please check your input and try again."
    
    @staticmethod
    def api_error() -> str:
        """API error"""
        return "❌ API error. Please try again later."
    
    @staticmethod
    def permission_denied() -> str:
        """Permission denied"""
        return "❌ You don't have permission to perform this action."
