"""
Content Search Helper untuk AnnounceHandler.
Handle searching movie/series by title and year.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def search_content(tmdb_service, media_type: str, title_year: str) -> Optional[dict]:
    """
    Search movie/series berdasarkan judul dan tahun.
    
    Args:
        tmdb_service: TMDBService instance
        media_type: 'movies' atau 'series'
        title_year: Title dengan tahun (e.g. "Fight Club 1999")
        
    Returns:
        Movie/series info dictionary atau None
    """
    try:
        # Parse title dan year
        # Format: "Judul Film 1999" atau "Judul Series 2020"
        parts = title_year.rsplit(' ', 1)  # Split dari kanan untuk ambil year
        
        if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
            title = parts[0].strip()
            year = int(parts[1])
        else:
            # Jika tidak ada year atau format salah, pakai semua sebagai title
            title = title_year.strip()
            year = None
        
        logger.info(f"Searching {media_type}: title='{title}', year={year}")
        
        # Search berdasarkan media type
        if media_type == 'movies':
            results = await tmdb_service.search_movie(title)
        else:  # series
            results = await tmdb_service.search_tv(title)
        
        if not results:
            logger.warning(f"No results found for {media_type}: {title}")
            return None
        
        # Filter by year jika ada
        if year:
            for result in results:
                # Movie uses 'release_date', TV uses 'first_air_date'
                date_key = 'release_date' if media_type == 'movies' else 'first_air_date'
                release_date = result.get(date_key, '')
                
                if release_date and release_date.startswith(str(year)):
                    logger.info(f"Found matching {media_type}: {result.get('title') or result.get('name')} ({year})")
                    # Get detailed info
                    tmdb_id = result['id']
                    if media_type == 'movies':
                        return await tmdb_service.get_movie_by_id(tmdb_id)
                    else:
                        return await tmdb_service.get_tv_by_id(tmdb_id)
            
            logger.warning(f"No {media_type} found matching year {year}")
            return None
        else:
            # Jika tidak ada year, ambil result pertama
            result = results[0]
            logger.info(f"Using first result: {result.get('title') or result.get('name')}")
            tmdb_id = result['id']
            if media_type == 'movies':
                return await tmdb_service.get_movie_by_id(tmdb_id)
            else:
                return await tmdb_service.get_tv_by_id(tmdb_id)
                
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        return None
