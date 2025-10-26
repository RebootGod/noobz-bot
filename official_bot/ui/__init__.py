"""
UI Module
Inline keyboards and formatting utilities for Telegram bot
"""

from .keyboards_main_auth import (
    MainMenuKeyboards,
    HelpKeyboards,
    StatsKeyboards,
    build_pagination_keyboard,
    build_confirmation_keyboard
)

from .keyboards_movie import (
    MovieUploadKeyboards,
    MoviePreviewKeyboards,
    get_movie_status_emoji,
    format_movie_state_summary
)

from .keyboards_series import (
    SeriesUploadKeyboards,
    ManualModeKeyboards,
    EpisodeProgressKeyboards,
    build_episode_list_keyboard,
    format_episode_status_summary
)

from .keyboards_password import (
    PasswordManagerKeyboards,
    PasswordStatsKeyboards,
    format_password_list,
    format_password_stats,
    format_revoke_confirmation
)

from .messages import (
    AuthMessages,
    MovieMessages,
    SeriesMessages,
    EpisodeMessages,
    PasswordMessages,
    HelpMessages,
    ErrorMessages
)

from .formatters import (
    MovieFormatters,
    SeriesFormatters,
    EpisodeFormatters,
    StatsFormatters,
    PasswordFormatters,
    TimeFormatters,
    URLFormatters,
    format_progress_bar
)

__all__ = [
    # Main/Auth keyboards
    'MainMenuKeyboards',
    'HelpKeyboards',
    'StatsKeyboards',
    'build_pagination_keyboard',
    'build_confirmation_keyboard',
    
    # Movie keyboards
    'MovieUploadKeyboards',
    'MoviePreviewKeyboards',
    'get_movie_status_emoji',
    'format_movie_state_summary',
    
    # Series keyboards
    'SeriesUploadKeyboards',
    'ManualModeKeyboards',
    'EpisodeProgressKeyboards',
    'build_episode_list_keyboard',
    'format_episode_status_summary',
    
    # Password keyboards
    'PasswordManagerKeyboards',
    'PasswordStatsKeyboards',
    'format_password_list',
    'format_password_stats',
    'format_revoke_confirmation',
    
    # Messages
    'AuthMessages',
    'MovieMessages',
    'SeriesMessages',
    'EpisodeMessages',
    'PasswordMessages',
    'HelpMessages',
    'ErrorMessages',
    
    # Formatters
    'MovieFormatters',
    'SeriesFormatters',
    'EpisodeFormatters',
    'StatsFormatters',
    'PasswordFormatters',
    'TimeFormatters',
    'URLFormatters',
    'format_progress_bar'
]
