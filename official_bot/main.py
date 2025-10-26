"""
Official Noobz Telegram Bot - Main Entry Point
Upload-focused bot with SQLite authentication.
"""

import logging
import sys
from telegram import Update
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
from handlers.series_upload_handler_2 import register_handlers as register_series
from handlers.password_manager_handler import register_handlers as register_password_manager
from handlers.help_handler import register_handlers as register_help
from handlers.unified_input_handler import UnifiedInputHandler

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
            logger.info(f"Password hint: {result['password_hint']}")
        else:
            logger.critical(f"Failed to create master password: {result.get('error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Error setting up master password: {e}", exc_info=True)
        sys.exit(1)


def register_callback_handlers(application: Application, services: dict, help_handler, movie_handler, movie_handler_2, series_handler, series_handler_2):
    """
    Register all callback query handlers.
    
    Args:
        application: Telegram application instance
        services: Dictionary of service instances
        help_handler: HelpHandler instance
        movie_handler: MovieUploadHandler instance
        movie_handler_2: MovieUploadHandlerPart2 instance
        series_handler: SeriesUploadHandler instance
        series_handler_2: SeriesUploadHandlerPart2 instance (for series)
    """
    # Import handler classes
    from handlers.start_handler import StartHandler
    from handlers.auth_handler import AuthHandler
    from handlers.password_manager_handler import PasswordManagerHandler
    
    # Initialize handlers (except movie and series handlers - already passed in)
    start_handler = StartHandler(services['session'])
    auth_handler = AuthHandler(services['auth'], services['session'])
    password_handler = PasswordManagerHandler(services['session'], services['auth'])
    
    # Register callback handlers
    
    # Home button
    application.add_handler(
        CallbackQueryHandler(start_handler.handle_home, pattern='^home$')
    )
    
    # Stats and Help buttons
    application.add_handler(
        CallbackQueryHandler(start_handler.handle_stats, pattern='^menu_stats$')
    )
    application.add_handler(
        CallbackQueryHandler(start_handler.handle_help, pattern='^menu_help$')
    )
    
    # Help topic handlers
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_menu, pattern='^menu_help$')
    )
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_movie, pattern='^help_movie$')
    )
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_series, pattern='^help_series$')
    )
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_bulk, pattern='^help_bulk$')
    )
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_manual, pattern='^help_manual$')
    )
    application.add_handler(
        CallbackQueryHandler(help_handler.handle_help_password, pattern='^help_password$')
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
    
    # Movie upload handlers (main menu button uses menu_movie)
    application.add_handler(
        CallbackQueryHandler(movie_handler.start_movie_upload, pattern='^menu_movie$')
    )
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
    
    # Series upload handlers (main menu button uses menu_series)
    application.add_handler(
        CallbackQueryHandler(series_handler.start_series_upload, pattern='^menu_series$')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler.start_series_upload, pattern='^upload_series$')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler.handle_season_selection, pattern='^series_season_')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler.cancel_series_upload, pattern='^series_cancel$')
    )
    
    # Episode handlers (part 2) - use passed-in handler
    application.add_handler(
        CallbackQueryHandler(series_handler_2.prompt_bulk_upload, pattern='^bulk_upload_')
    )
    application.add_handler(
        CallbackQueryHandler(series_handler_2.execute_bulk_upload, pattern='^confirm_bulk_upload_')
    )
    
    # Password manager handlers (main menu button uses menu_password_manager)
    application.add_handler(
        CallbackQueryHandler(password_handler.show_password_manager, pattern='^menu_password_manager$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.show_password_manager, pattern='^password_manager$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.handle_password_add, pattern='^password_add$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.prompt_password_type, pattern='^add_password$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.start_password_creation, pattern='^password_type_')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.handle_password_stats, pattern='^password_stats$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.handle_password_revoke, pattern='^password_revoke$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.handle_password_cancel, pattern='^password_cancel$')
    )
    application.add_handler(
        CallbackQueryHandler(password_handler.handle_main_menu, pattern='^main_menu$')
    )
    
    logger.info("All callback handlers registered successfully")


def main():
    """Main entry point for the bot."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Starting Noobz Official Bot")
        logger.info("🔧 VERSION: 2025-10-26-21-00-DEBUG-LOGGING")  # Unique version marker
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

        # Create application with PicklePersistence (absolute path, next to main.py)
        logger.info("Creating Telegram application with PicklePersistence...")
        from pathlib import Path
        from telegram.ext import PicklePersistence
        persistence_path = Path(__file__).resolve().with_name("bot_persistence.pkl")
        logger.info(f"PicklePersistence file: {persistence_path}")
        persistence = PicklePersistence(filepath=str(persistence_path))
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).persistence(persistence).build()

        # Register handlers
        logger.info("Registering handlers...")
        
        # Register command and message handlers
        try:
            logger.info("Step 1: Registering start handler...")
            register_start(application, services['session'])
            logger.info("✅ Start handler registered")
            
            logger.info("Step 2: Registering auth handler...")
            register_auth(application, services['auth'], services['session'])
            logger.info("✅ Auth handler registered")
            
            logger.info("Step 3: Registering movie handler...")
            movie_handler, movie_handler_2 = register_movie(application, services['session'], services['tmdb'], services['noobz_api'])
            logger.info(f"✅ Movie handlers initialized: {movie_handler is not None}, {movie_handler_2 is not None}")
            
            logger.info("Step 4: Registering series handler...")
            series_handler, series_handler_2 = register_series(application, services['session'], services['tmdb'], services['noobz_api'], services['context'])
            logger.info(f"✅ Series handlers initialized: {series_handler is not None}, {series_handler_2 is not None}")
            
            logger.info("Step 5: Registering password manager...")
            register_password_manager(application, services['session'], services['auth'])
            logger.info("✅ Password manager registered")
            
            logger.info("Step 6: Registering help handler...")
            help_handler = register_help(application)
            logger.info("✅ Help handler registered")
            
            logger.info("Step 7: Registering unified input handler...")
            # Create unified input handler that handles ALL text input
            unified_handler = UnifiedInputHandler(movie_handler, movie_handler_2, series_handler)
            application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    unified_handler.handle_text_input
                ),
                group=0
            )
            logger.info("✅ Unified input handler registered (group 0)")
            
            logger.info("Step 8: Registering callback handlers...")
            register_callback_handlers(application, services, help_handler, movie_handler, movie_handler_2, series_handler, series_handler_2)
            logger.info("✅ Callback handlers registered")
            
        except Exception as e:
            logger.critical(f"HANDLER REGISTRATION FAILED AT SOME STEP: {e}", exc_info=True)
            raise
        
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
