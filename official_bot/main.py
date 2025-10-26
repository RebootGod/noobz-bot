"""
Official Noobz Telegram Bot - Main Entry Point
Upload-focused bot with SQLite authentication.
"""

import logging
import sys
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters

# Import config
from config.settings import Settings
from config.database import Database, init_database

# Import services
from services.auth_service import AuthService
from services.session_service import SessionService
from services.context_service import ContextService
from services.tmdb_service import TmdbService
from services.noobz_api_service import NoobzApiService

# Import handlers
from handlers.start_handler import register_handlers as register_start
from handlers.auth_handler import register_handlers as register_auth
from handlers.movie_upload_handler_2 import register_handlers as register_movie
from handlers.password_manager_handler import register_handlers as register_password_manager

# Import utilities
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()


def initialize_database() -> Database:
    """
    Initialize database and create tables.
    
    Returns:
        Database instance
    """
    try:
        # Initialize database schema
        if not init_database():
            raise Exception("Database initialization failed")
        
        # Return database instance
        db = Database()
        logger.info("Database initialized successfully")
        return db
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}", exc_info=True)
        sys.exit(1)


def initialize_services(db: Database) -> dict:
    """
    Initialize all bot services.
    
    Args:
        db: Database instance (not used, services use global db instance)
        
    Returns:
        Dictionary of service instances
    """
    try:
        auth_service = AuthService()
        session_service = SessionService()
        context_service = ContextService()
        tmdb_service = TmdbService(Settings)
        noobz_api_service = NoobzApiService(Settings)
        
        logger.info("All services initialized successfully")
        
        return {
            'auth': auth_service,
            'session': session_service,
            'context': context_service,
            'tmdb': tmdb_service,
            'noobz_api': noobz_api_service
        }
    except Exception as e:
        logger.critical(f"Failed to initialize services: {e}", exc_info=True)
        sys.exit(1)


def setup_master_password(auth_service: AuthService):
    """
    Setup initial master password if not exists.
    
    Args:
        auth_service: Authentication service instance
    """
    try:
        # Check if master password exists
        if auth_service.has_master_password():
            logger.info("Master password already exists")
            return
        
        # Create initial master password
        logger.warning("No master password found. Creating initial master password...")
        
        # For production, you should set this via environment variable
        initial_password = Settings.INITIAL_MASTER_PASSWORD
        
        if not initial_password:
            logger.critical(
                "INITIAL_MASTER_PASSWORD not set in environment. "
                "Cannot create master password."
            )
            sys.exit(1)
        
        result = auth_service.create_password(
            password=initial_password,
            password_type='master',
            notes='Initial master password'
        )
        
        if result['success']:
            logger.info("✅ Master password created successfully")
            logger.info(f"Password hint: {result['password']['password_hint']}")
        else:
            logger.critical(f"Failed to create master password: {result.get('message')}")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Error setting up master password: {e}", exc_info=True)
        sys.exit(1)


def register_callback_handlers(application: Application, services: dict):
    """
    Register all callback query handlers.
    
    Args:
        application: Telegram application instance
        services: Dictionary of service instances
    """
    # Import handler classes
    from handlers.start_handler import StartHandler
    from handlers.auth_handler import AuthHandler
    from handlers.movie_upload_handler import MovieUploadHandler
    from handlers.movie_upload_handler_2 import MovieUploadHandlerPart2
    from handlers.series_upload_handler_1 import SeriesUploadHandler
    from handlers.series_upload_handler_2 import SeriesUploadHandlerPart2
    from handlers.password_manager_handler import PasswordManagerHandler
    
    # Initialize handlers
    start_handler = StartHandler(services['session'])
    auth_handler = AuthHandler(services['auth'], services['session'])
    movie_handler = MovieUploadHandler(
        services['session'],
        services['tmdb'],
        services['noobz_api']
    )
    movie_handler_2 = MovieUploadHandlerPart2(movie_handler)
    series_handler = SeriesUploadHandler(
        services['session'],
        services['tmdb'],
        services['noobz_api'],
        services['context']
    )
    password_handler = PasswordManagerHandler(services['session'], services['auth'])
    
    # Register callback handlers
    
    # Home button
    application.add_handler(
        CallbackQueryHandler(start_handler.handle_home, pattern='^home$')
    )
    
    # Auth handlers
    application.add_handler(
        CallbackQueryHandler(auth_handler.handle_retry_auth, pattern='^retry_auth$')
    )
    application.add_handler(
        CallbackQueryHandler(auth_handler.handle_cancel_auth, pattern='^cancel_auth$')
    )
    application.add_handler(
        CallbackQueryHandler(auth_handler.handle_logout, pattern='^logout$')
    )
    
    # Movie upload handlers
    application.add_handler(
        CallbackQueryHandler(movie_handler.start_movie_upload, pattern='^upload_movie$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler.prompt_tmdb_id, pattern='^movie_set_tmdb$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler.prompt_embed_url, pattern='^movie_set_embed$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler_2.prompt_download_url, pattern='^movie_set_download$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler_2.confirm_upload, pattern='^movie_upload_now$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler_2.execute_upload, pattern='^movie_upload_confirm$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler_2.cancel_upload, pattern='^movie_cancel$')
    )
    application.add_handler(
        CallbackQueryHandler(movie_handler.start_movie_upload, pattern='^movie_upload_another$')
    )
    
    # Series upload handlers
    application.add_handler(
        CallbackQueryHandler(series_handler.start_series_upload, pattern='^upload_series$')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler.handle_season_selection, pattern='^series_season_')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler.cancel_series_upload, pattern='^series_cancel$')
    )
    
    # Episode handlers (part 2)
    series_handler_2 = SeriesUploadHandlerPart2(series_handler)
    application.add_handler(
        CallbackQueryHandler(series_handler_2.prompt_bulk_upload, pattern='^bulk_upload_')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler_2.execute_bulk_upload, pattern='^confirm_bulk_upload_')
    )
    
    # Password manager handlers
    application.add_handler(
        CallbackQueryHandler(password_handler.show_password_manager, pattern='^password_manager$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.prompt_password_type, pattern='^add_password$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.start_password_creation, pattern='^create_password_')
    )
    
    logger.info("All callback handlers registered successfully")


def main():
    """Main entry point for the bot."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Starting Noobz Official Bot")
        logger.info("=" * 60)
        
        # Load settings
        settings = Settings.load()
        logger.info(f"Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
        logger.info(f"API URL: {settings.NOOBZ_API_URL}")
        logger.info(f"Database: {settings.DATABASE_PATH}")
        
        # Initialize database
        logger.info("Initializing database...")
        db = initialize_database()
        
        # Initialize services
        logger.info("Initializing services...")
        services = initialize_services(db)
        
        # Setup master password
        logger.info("Checking master password...")
        setup_master_password(services['auth'])
        
        # Create application
        logger.info("Creating Telegram application...")
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Register handlers
        logger.info("Registering handlers...")
        
        # Register command and message handlers
        register_start(application, services['session'])
        register_auth(application, services['auth'], services['session'])
        register_movie(application, services['session'], services['tmdb'], services['noobz_api'])
        register_password_manager(application, services['session'], services['auth'])
        
        # Register callback handlers
        register_callback_handlers(application, services)
        
        logger.info("✅ All handlers registered")
        
        # Start bot
        logger.info("=" * 60)
        logger.info("✅ Bot started successfully!")
        logger.info("Polling for updates...")
        logger.info("=" * 60)
        
        # Run bot until Ctrl+C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
