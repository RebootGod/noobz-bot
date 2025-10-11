"""
Upload parser untuk parse message input dari user.
Extract TMDB ID, URLs, dan informasi lainnya dari Telegram message.
"""

import re
from typing import Optional, Dict, Any, Tuple


class UploadParser:
    """
    Parser untuk upload commands.
    Extract data dari message text.
    """
    
    # Regex patterns
    TMDB_ID_PATTERN = re.compile(r'tmdb[_\s]*id[:\s]*(\d+)', re.IGNORECASE)
    TMDB_URL_PATTERN = re.compile(
        r'themoviedb\.org/(?:movie|tv)/(\d+)', 
        re.IGNORECASE
    )
    EMBED_URL_PATTERN = re.compile(r'embed[_\s]*url[:\s]*(https?://\S+)', re.IGNORECASE)
    DOWNLOAD_URL_PATTERN = re.compile(
        r'download[_\s]*url[:\s]*(https?://\S+)', 
        re.IGNORECASE
    )
    SEASON_PATTERN = re.compile(r'season[:\s]*(\d+)', re.IGNORECASE)
    EPISODE_PATTERN = re.compile(r'episode[:\s]*(\d+)', re.IGNORECASE)
    
    # Short format: S01E05
    SE_PATTERN = re.compile(r's(\d+)e(\d+)', re.IGNORECASE)
    
    @staticmethod
    def parse_tmdb_id(text: str) -> Optional[int]:
        """
        Parse TMDB ID dari text.
        Support: "tmdb_id: 12345", "tmdb id 12345", 
                 atau TMDB URL "https://www.themoviedb.org/movie/12345"
        
        Args:
            text: Input text
            
        Returns:
            TMDB ID or None
        """
        # Try direct TMDB ID pattern
        match = UploadParser.TMDB_ID_PATTERN.search(text)
        if match:
            return int(match.group(1))
        
        # Try TMDB URL pattern
        match = UploadParser.TMDB_URL_PATTERN.search(text)
        if match:
            return int(match.group(1))
        
        # Try standalone number di awal message
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            if first_line.isdigit():
                return int(first_line)
        
        return None
    
    @staticmethod
    def parse_embed_url(text: str) -> Optional[str]:
        """
        Parse embed URL dari text.
        
        Args:
            text: Input text
            
        Returns:
            Embed URL or None
        """
        match = UploadParser.EMBED_URL_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        
        # Fallback: cari https URL pertama
        urls = re.findall(r'https?://\S+', text, re.IGNORECASE)
        if urls:
            return urls[0].strip()
        
        return None
    
    @staticmethod
    def parse_download_url(text: str) -> Optional[str]:
        """
        Parse download URL dari text.
        
        Args:
            text: Input text
            
        Returns:
            Download URL or None
        """
        match = UploadParser.DOWNLOAD_URL_PATTERN.search(text)
        if match:
            return match.group(1).strip()
        
        # Cari semua URLs, ambil yang kedua jika ada
        urls = re.findall(r'https?://\S+', text, re.IGNORECASE)
        if len(urls) >= 2:
            return urls[1].strip()
        
        return None
    
    @staticmethod
    def parse_season_number(text: str) -> Optional[int]:
        """
        Parse season number dari text.
        Support: "season: 1", "s01", "season 1"
        
        Args:
            text: Input text
            
        Returns:
            Season number or None
        """
        # Try SE pattern first (S01E05)
        match = UploadParser.SE_PATTERN.search(text)
        if match:
            return int(match.group(1))
        
        # Try direct season pattern
        match = UploadParser.SEASON_PATTERN.search(text)
        if match:
            return int(match.group(1))
        
        return None
    
    @staticmethod
    def parse_episode_number(text: str) -> Optional[int]:
        """
        Parse episode number dari text.
        Support: "episode: 5", "e05", "episode 5"
        
        Args:
            text: Input text
            
        Returns:
            Episode number or None
        """
        # Try SE pattern first (S01E05)
        match = UploadParser.SE_PATTERN.search(text)
        if match:
            return int(match.group(2))
        
        # Try direct episode pattern
        match = UploadParser.EPISODE_PATTERN.search(text)
        if match:
            return int(match.group(1))
        
        return None
    
    @staticmethod
    def parse_movie_upload(text: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Parse movie upload command.
        
        Args:
            text: Message text
            
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        tmdb_id = UploadParser.parse_tmdb_id(text)
        if not tmdb_id:
            return False, {}, "TMDB ID tidak ditemukan. Format: /uploadmovie <tmdb_id> <embed_url> [download_url]"
        
        embed_url = UploadParser.parse_embed_url(text)
        if not embed_url:
            return False, {}, "Embed URL tidak ditemukan. Sertakan URL embed untuk movie."
        
        download_url = UploadParser.parse_download_url(text)
        
        return True, {
            'tmdb_id': tmdb_id,
            'embed_url': embed_url,
            'download_url': download_url
        }, None
    
    @staticmethod
    def parse_series_upload(text: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Parse series upload command.
        
        Args:
            text: Message text
            
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        tmdb_id = UploadParser.parse_tmdb_id(text)
        if not tmdb_id:
            return False, {}, "TMDB ID tidak ditemukan. Format: /uploadseries <tmdb_id>"
        
        return True, {'tmdb_id': tmdb_id}, None
    
    @staticmethod
    def parse_season_upload(text: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Parse season upload command.
        
        Args:
            text: Message text
            
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        tmdb_id = UploadParser.parse_tmdb_id(text)
        if not tmdb_id:
            return False, {}, "TMDB ID tidak ditemukan. Format: /uploadseason <tmdb_id> <season_number>"
        
        season_number = UploadParser.parse_season_number(text)
        if season_number is None:
            return False, {}, "Season number tidak ditemukan. Contoh: 'season: 1' atau 'S01'"
        
        return True, {
            'tmdb_id': tmdb_id,
            'season_number': season_number
        }, None
    
    @staticmethod
    def parse_episode_upload(text: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Parse episode upload command.
        
        Args:
            text: Message text
            
        Returns:
            Tuple of (success, parsed_data, error_message)
        """
        tmdb_id = UploadParser.parse_tmdb_id(text)
        if not tmdb_id:
            return False, {}, "TMDB ID tidak ditemukan"
        
        season_number = UploadParser.parse_season_number(text)
        if season_number is None:
            return False, {}, "Season number tidak ditemukan. Contoh: 'S01E05' atau 'season: 1'"
        
        episode_number = UploadParser.parse_episode_number(text)
        if episode_number is None:
            return False, {}, "Episode number tidak ditemukan. Contoh: 'S01E05' atau 'episode: 5'"
        
        embed_url = UploadParser.parse_embed_url(text)
        if not embed_url:
            return False, {}, "Embed URL tidak ditemukan. Sertakan URL embed untuk episode."
        
        download_url = UploadParser.parse_download_url(text)
        
        return True, {
            'tmdb_id': tmdb_id,
            'season_number': season_number,
            'episode_number': episode_number,
            'embed_url': embed_url,
            'download_url': download_url
        }, None
