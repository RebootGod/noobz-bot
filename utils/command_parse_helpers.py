"""
Command Parsing Helpers untuk extract common tags.
Reusable functions untuk parse [movies/series], [judul tahun], [sinopsis].
"""

import re
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Regex patterns
MEDIA_TYPE_PATTERN = r'\[(movies|series)\]'
MEDIA_TYPE_ID_PATTERN = r'\[(moviesid|seriesid)\]\s*\[(\d+)\]'  # Match [moviesid][123] or [seriesid][456]
GEMINI_PATTERN = r'\[gemini\]'  # Match [gemini] tag
# Match [Judul 2024] or [Judul] but NOT [movies], [series], [gemini], [sinopsis], [moviesid], [seriesid]
TITLE_YEAR_PATTERN = r'\[(?!movies\]|series\]|gemini\]|sinopsis\]|moviesid\]|seriesid\])([^\[\]]+)\]'
SYNOPSIS_PATTERN = r'\[sinopsis\]\s*(.+?)(?=\[|$)'


def extract_media_type(prompt: str) -> Tuple[Optional[str], str]:
    """
    Extract media type ([movies] atau [series]) dari prompt.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Tuple of (media_type, cleaned_prompt)
    """
    media_type = None
    media_match = re.search(MEDIA_TYPE_PATTERN, prompt, re.IGNORECASE)
    if media_match:
        media_type = media_match.group(1).lower()
        # Remove [movies/series] dari prompt
        prompt = re.sub(MEDIA_TYPE_PATTERN, '', prompt, flags=re.IGNORECASE).strip()
    
    return media_type, prompt


def extract_media_type_id(prompt: str) -> Tuple[Optional[str], Optional[int], str]:
    """
    Extract media type ID ([moviesid][123] atau [seriesid][456]) dari prompt.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Tuple of (media_type, tmdb_id, cleaned_prompt)
        - media_type: 'movies' atau 'series' (without 'id' suffix)
        - tmdb_id: TMDB ID as integer
        - cleaned_prompt: Prompt with tags removed
    """
    media_type = None
    tmdb_id = None
    media_id_match = re.search(MEDIA_TYPE_ID_PATTERN, prompt, re.IGNORECASE)
    if media_id_match:
        # Extract type (moviesid -> movies, seriesid -> series)
        type_with_id = media_id_match.group(1).lower()
        media_type = type_with_id.replace('id', '')  # moviesid -> movies, seriesid -> series
        tmdb_id = int(media_id_match.group(2))
        # Remove [moviesid/seriesid][123] dari prompt
        prompt = re.sub(MEDIA_TYPE_ID_PATTERN, '', prompt, flags=re.IGNORECASE).strip()
    
    return media_type, tmdb_id, prompt



def extract_gemini_tag(prompt: str) -> Tuple[bool, str]:
    """
    Extract [gemini] tag dari prompt.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Tuple of (use_gemini, cleaned_prompt)
    """
    use_gemini = False
    gemini_match = re.search(GEMINI_PATTERN, prompt, re.IGNORECASE)
    if gemini_match:
        use_gemini = True
        # Remove [gemini] dari prompt
        prompt = re.sub(GEMINI_PATTERN, '', prompt, flags=re.IGNORECASE).strip()
    
    return use_gemini, prompt


def extract_custom_synopsis(prompt: str) -> Tuple[Optional[str], str]:
    """
    Extract custom synopsis dari [sinopsis] tag.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Tuple of (custom_synopsis, cleaned_prompt)
    """
    custom_synopsis = None
    synopsis_match = re.search(SYNOPSIS_PATTERN, prompt, re.IGNORECASE | re.DOTALL)
    if synopsis_match:
        custom_synopsis = synopsis_match.group(1).strip()
        # Remove [sinopsis]...content dari prompt
        prompt = re.sub(SYNOPSIS_PATTERN, '', prompt, flags=re.IGNORECASE | re.DOTALL).strip()
    
    return custom_synopsis, prompt


def extract_title_year(prompt: str) -> Tuple[Optional[str], str]:
    """
    Extract title+year dari [judul tahun] tag.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Tuple of (title_year, custom_prompt)
    """
    title_year = None
    title_match = re.search(TITLE_YEAR_PATTERN, prompt)
    if title_match:
        title_year = title_match.group(1).strip()
        # Remove [judul tahun] dari prompt
        custom_prompt = re.sub(TITLE_YEAR_PATTERN, '', prompt).strip()
    else:
        custom_prompt = prompt
    
    return title_year, custom_prompt


def validate_media_type_requirement(title_year: Optional[str], media_type: Optional[str]) -> Optional[str]:
    """
    Validate bahwa media_type required jika ada title_year.
    
    Args:
        title_year: Title+year string
        media_type: Media type (movies/series)
        
    Returns:
        Error message jika validation failed, None jika OK
    """
    if title_year and not media_type:
        return 'Media type required when using [judul tahun]! Use [movies] or [series] or [moviesid][ID] or [seriesid][ID]'
    return None
