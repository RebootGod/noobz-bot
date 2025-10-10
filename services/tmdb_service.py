"""
TMDB Service - Main service combining movie and TV operations.
Handle API calls ke The Movie Database (TMDB).
"""

import logging
from typing import Optional

from services.tmdb_movie import TMDBMovie
from services.tmdb_tv import TMDBTV

logger = logging.getLogger(__name__)


class TMDBService(TMDBMovie, TMDBTV):
    """
    Main TMDB service combining movie and TV operations.
    Inherits from TMDBMovie and TMDBTV for full functionality.
    """
    
    def __init__(self):
        """Initialize TMDB service."""
        super().__init__()
        logger.info("TMDB Service initialized")


# Global instance
_tmdb_service: Optional[TMDBService] = None


def get_tmdb_service() -> TMDBService:
    """
    Get global TMDBService instance.
    
    Returns:
        TMDBService instance
    """
    global _tmdb_service
    if _tmdb_service is None:
        _tmdb_service = TMDBService()
    return _tmdb_service

