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
TITLE_YEAR_PATTERN = r'\[([^\[\]]+\s+\d{4})\]'
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
        return 'Media type required when using [judul tahun]! Use [movies] or [series]'
    return None
