"""
Constants and Enumerations
Central place for all constants used throughout the bot
"""

from enum import Enum


# Password Types
class PasswordType(Enum):
    """Password types"""
    MASTER = 'master'
    ADMIN = 'admin'


# Upload Types
class UploadType(Enum):
    """Content upload types"""
    MOVIE = 'movie'
    SERIES = 'series'
    SEASON = 'season'
    EPISODE = 'episode'


# Context Types
class ContextType(Enum):
    """Upload context types"""
    MOVIE = 'movie'
    SERIES = 'series'
    SEASON = 'season'
    EPISODE = 'episode'


# Upload Steps
class UploadStep(Enum):
    """Steps in upload process"""
    # Movie steps
    MOVIE_SET_TMDB_ID = 'movie_set_tmdb_id'
    MOVIE_SET_EMBED_URL = 'movie_set_embed_url'
    MOVIE_SET_DOWNLOAD_URL = 'movie_set_download_url'
    MOVIE_CONFIRM = 'movie_confirm'
    
    # Series steps
    SERIES_SET_TMDB_ID = 'series_set_tmdb_id'
    SERIES_SELECT_SEASON = 'series_select_season'
    SERIES_UPLOAD_MODE = 'series_upload_mode'
    
    # Episode steps
    EPISODE_BULK_INPUT = 'episode_bulk_input'
    EPISODE_SINGLE_INPUT = 'episode_single_input'
    EPISODE_MANUAL_INPUT = 'episode_manual_input'


# Callback Data Prefixes
class CallbackPrefix:
    """Prefixes for callback data"""
    # Main menu
    MAIN_MENU = 'main_menu'
    UPLOAD_MOVIE = 'upload_movie'
    UPLOAD_SERIES = 'upload_series'
    VIEW_STATS = 'view_stats'
    PASSWORD_MANAGER = 'password_manager'
    HELP = 'help'
    
    # Movie upload
    MOVIE_SET_TMDB = 'movie_set_tmdb'
    MOVIE_SET_EMBED = 'movie_set_embed'
    MOVIE_SET_DOWNLOAD = 'movie_set_download'
    MOVIE_UPLOAD_NOW = 'movie_upload_now'
    MOVIE_CANCEL = 'movie_cancel'
    
    # Series upload
    SERIES_SET_TMDB = 'series_set_tmdb'
    SERIES_SEASON = 'series_season'
    SERIES_BULK = 'series_bulk'
    SERIES_SINGLE = 'series_single'
    SERIES_MANUAL = 'series_manual'
    SERIES_REFRESH = 'series_refresh'
    SERIES_CHANGE_SEASON = 'series_change_season'
    SERIES_CANCEL = 'series_cancel'
    
    # Episode upload
    EPISODE_CONFIRM = 'episode_confirm'
    EPISODE_CANCEL = 'episode_cancel'
    EPISODE_UPLOAD_MORE = 'episode_upload_more'
    
    # Password manager
    PM_ADD_PASSWORD = 'pm_add_password'
    PM_REVOKE_PASSWORD = 'pm_revoke_password'
    PM_VIEW_STATS = 'pm_view_stats'
    PM_BACK = 'pm_back'
    PM_CREATE_MASTER = 'pm_create_master'
    PM_CREATE_ADMIN = 'pm_create_admin'
    PM_CONFIRM_REVOKE = 'pm_confirm_revoke'
    
    # Common
    CANCEL = 'cancel'
    BACK = 'back'
    CONFIRM = 'confirm'


# Messages
class Messages:
    """Bot message templates"""
    
    # Welcome
    WELCOME = """🎬 **Noobz Upload Bot**

Welcome! This bot helps you upload movies and series.

🔒 **Authentication Required**

Please enter your password:"""
    
    WELCOME_AUTHENTICATED = """✅ **Authentication Successful!**
Welcome back!

Your session will expire in 24 hours.

What would you like to do?"""
    
    WELCOME_MASTER = """✅ **Master Access Granted!**
Welcome, Master!

You have full access including password management.

What would you like to do?"""
    
    # Authentication
    AUTH_INVALID = "❌ Invalid password. Please try again."
    AUTH_SESSION_EXPIRED = "⏰ Your session has expired. Please authenticate again."
    
    # Errors
    ERROR_GENERIC = "❌ An error occurred. Please try again."
    ERROR_NETWORK = "❌ Network error. Please check your connection."
    ERROR_TMDB = "❌ TMDB API error. Please try again later."
    ERROR_API = "❌ API error. Please contact administrator."
    
    # Success
    SUCCESS_MOVIE_UPLOADED = "✅ Movie uploaded successfully!"
    SUCCESS_SERIES_CREATED = "✅ Series created successfully!"
    SUCCESS_EPISODE_UPLOADED = "✅ Episode uploaded successfully!"
    SUCCESS_PASSWORD_CREATED = "✅ Password created successfully!"
    SUCCESS_PASSWORD_REVOKED = "✅ Password revoked successfully!"


# Emoji
class Emoji:
    """Emoji constants"""
    # Media types
    MOVIE = '🎥'
    SERIES = '📺'
    SEASON = '📹'
    EPISODE = '🎬'
    
    # Actions
    UPLOAD = '📤'
    DOWNLOAD = '📥'
    STATS = '📊'
    SETTINGS = '⚙️'
    HELP = '❓'
    
    # Status
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    LOADING = '⏳'
    
    # Navigation
    BACK = '🔙'
    HOME = '🏠'
    NEXT = '➡️'
    PREV = '⬅️'
    
    # Security
    LOCK = '🔒'
    KEY = '🔑'
    MASTER = '👑'
    ADMIN = '👤'
    
    # Numbers (for seasons)
    NUMBERS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    # Other
    STAR = '⭐'
    CALENDAR = '📅'
    TEXT = '📝'
    LINK = '🔗'
    TRASH = '🗑️'
    PLUS = '➕'
    CHECK = '✓'
    CROSS = '✗'


# Validation Patterns
class ValidationPatterns:
    """Regex patterns for validation"""
    # URLs
    URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'
    VIDSRC_PATTERN = r'^https://vidsrc\.to/(embed|embed/)'
    
    # TMDB ID
    TMDB_ID_PATTERN = r'^\d{1,10}$'
    
    # Episode format for bulk upload
    EPISODE_BULK_PATTERN = r'^(\d{1,3})\s*\|\s*(.+?)\s*\|\s*(.+)$'
    
    # Password
    PASSWORD_PATTERN = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$'


# API Endpoints
class NoobzEndpoints:
    """Noobz API endpoints"""
    MOVIES = '/api/bot/movies'
    SERIES = '/api/bot/series'
    SEASONS = '/api/bot/series/{tmdb_id}/seasons'
    EPISODES = '/api/bot/series/{tmdb_id}/episodes'
    EPISODE_STATUS = '/api/bot/series/{tmdb_id}/episodes-status'
    EPISODE_UPDATE = '/api/bot/episodes/{episode_id}'


class TMDBEndpoints:
    """TMDB API endpoints"""
    MOVIE_DETAILS = '/movie/{movie_id}'
    SERIES_DETAILS = '/tv/{series_id}'
    SEASON_DETAILS = '/tv/{series_id}/season/{season_number}'


# Limits
class Limits:
    """Various limits"""
    MAX_BULK_EPISODES = 20
    MAX_SEASON_NUMBER = 99
    MAX_EPISODE_NUMBER = 999
    SESSION_EXPIRY_HOURS = 24
    PASSWORD_MIN_LENGTH = 8
    MAX_PASSWORD_ATTEMPTS = 3
    RATE_LIMIT_PER_MINUTE = 100
