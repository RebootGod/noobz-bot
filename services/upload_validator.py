"""
Upload validator untuk validate input sebelum send ke API.
Cek format URL, TMDB ID, dan field lainnya.
"""

import re
from typing import Optional, Tuple
from urllib.parse import urlparse


class UploadValidator:
    """
    Validator untuk upload input data.
    Validate sebelum kirim request ke API.
    """
    
    # URL patterns
    HTTPS_PATTERN = re.compile(r'^https://', re.IGNORECASE)
    
    @staticmethod
    def validate_tmdb_id(tmdb_id: any) -> Tuple[bool, Optional[str]]:
        """
        Validate TMDB ID.
        
        Args:
            tmdb_id: TMDB ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            tmdb_id_int = int(tmdb_id)
            if tmdb_id_int <= 0:
                return False, "TMDB ID must be positive integer"
            return True, None
        except (ValueError, TypeError):
            return False, "TMDB ID must be a valid integer"
    
    @staticmethod
    def validate_url(
        url: str,
        field_name: str = "URL",
        require_https: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            field_name: Field name untuk error message
            require_https: Require HTTPS protocol
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url or not isinstance(url, str):
            return False, f"{field_name} is required"
        
        url = url.strip()
        
        if len(url) > 1000:
            return False, f"{field_name} too long (max 1000 characters)"
        
        # Parse URL
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, f"{field_name} must include protocol (https://)"
            
            if require_https and parsed.scheme.lower() != 'https':
                return False, f"{field_name} must use HTTPS protocol"
            
            if not parsed.netloc:
                return False, f"{field_name} must include domain"
            
            return True, None
            
        except Exception as e:
            return False, f"{field_name} format invalid: {str(e)}"
    
    @staticmethod
    def validate_season_number(season_number: any) -> Tuple[bool, Optional[str]]:
        """
        Validate season number.
        
        Args:
            season_number: Season number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            season_int = int(season_number)
            if season_int < 0:
                return False, "Season number cannot be negative"
            if season_int > 100:
                return False, "Season number too large (max 100)"
            return True, None
        except (ValueError, TypeError):
            return False, "Season number must be a valid integer"
    
    @staticmethod
    def validate_episode_number(episode_number: any) -> Tuple[bool, Optional[str]]:
        """
        Validate episode number.
        
        Args:
            episode_number: Episode number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            episode_int = int(episode_number)
            if episode_int <= 0:
                return False, "Episode number must be positive"
            if episode_int > 1000:
                return False, "Episode number too large (max 1000)"
            return True, None
        except (ValueError, TypeError):
            return False, "Episode number must be a valid integer"
    
    @staticmethod
    def validate_movie_upload(
        tmdb_id: any,
        embed_url: str,
        download_url: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate movie upload data.
        
        Args:
            tmdb_id: TMDB ID
            embed_url: Embed URL
            download_url: Download URL (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate TMDB ID
        is_valid, error = UploadValidator.validate_tmdb_id(tmdb_id)
        if not is_valid:
            return False, error
        
        # Validate embed URL
        is_valid, error = UploadValidator.validate_url(embed_url, "Embed URL")
        if not is_valid:
            return False, error
        
        # Validate download URL if provided
        if download_url:
            is_valid, error = UploadValidator.validate_url(download_url, "Download URL")
            if not is_valid:
                return False, error
        
        return True, None
    
    @staticmethod
    def validate_series_upload(tmdb_id: any) -> Tuple[bool, Optional[str]]:
        """
        Validate series upload data.
        
        Args:
            tmdb_id: TMDB ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return UploadValidator.validate_tmdb_id(tmdb_id)
    
    @staticmethod
    def validate_season_upload(
        tmdb_id: any,
        season_number: any
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate season upload data.
        
        Args:
            tmdb_id: TMDB ID
            season_number: Season number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate TMDB ID
        is_valid, error = UploadValidator.validate_tmdb_id(tmdb_id)
        if not is_valid:
            return False, error
        
        # Validate season number
        is_valid, error = UploadValidator.validate_season_number(season_number)
        if not is_valid:
            return False, error
        
        return True, None
    
    @staticmethod
    def validate_episode_upload(
        tmdb_id: any,
        season_number: any,
        episode_number: any,
        embed_url: str,
        download_url: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate episode upload data.
        
        Args:
            tmdb_id: TMDB ID
            season_number: Season number
            episode_number: Episode number
            embed_url: Embed URL
            download_url: Download URL (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate TMDB ID
        is_valid, error = UploadValidator.validate_tmdb_id(tmdb_id)
        if not is_valid:
            return False, error
        
        # Validate season number
        is_valid, error = UploadValidator.validate_season_number(season_number)
        if not is_valid:
            return False, error
        
        # Validate episode number
        is_valid, error = UploadValidator.validate_episode_number(episode_number)
        if not is_valid:
            return False, error
        
        # Validate embed URL
        is_valid, error = UploadValidator.validate_url(embed_url, "Embed URL")
        if not is_valid:
            return False, error
        
        # Validate download URL if provided
        if download_url:
            is_valid, error = UploadValidator.validate_url(download_url, "Download URL")
            if not is_valid:
                return False, error
        
        return True, None
