"""
Handlers package initialization.
Exports all bot command and callback handlers.
"""

from .start_handler import StartHandler, register_handlers as register_start_handlers
from .auth_handler import AuthHandler, register_handlers as register_auth_handlers
from .movie_upload_handler import MovieUploadHandler
from .movie_upload_handler_2 import MovieUploadHandlerPart2, register_handlers as register_movie_handlers
from .series_upload_handler_1 import SeriesUploadHandler
from .series_upload_handler_2 import SeriesUploadHandlerPart2
from .password_manager_handler import PasswordManagerHandler, register_handlers as register_password_handlers

__all__ = [
    'StartHandler',
    'AuthHandler',
    'MovieUploadHandler',
    'MovieUploadHandlerPart2',
    'SeriesUploadHandler',
    'SeriesUploadHandlerPart2',
    'PasswordManagerHandler',
    'register_start_handlers',
    'register_auth_handlers',
    'register_movie_handlers',
    'register_password_handlers',
]
