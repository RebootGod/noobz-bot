"""
Message Parser utility untuk parse commands dari user.
Extract command, parameters, dan arguments.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from utils.command_parse_helpers import (
    extract_media_type,
    extract_gemini_tag,
    extract_custom_synopsis,
    extract_title_year,
    validate_media_type_requirement
)

logger = logging.getLogger(__name__)


@dataclass
class ParsedCommand:
    """
    Dataclass untuk store parsed command.
    """
    command: str
    target: Optional[str] = None
    content_type: Optional[str] = None
    keyword: Optional[str] = None
    year: Optional[int] = None
    tmdb_id: Optional[int] = None
    media_type: Optional[str] = None  # 'movies' atau 'series'
    title_year: Optional[str] = None  # Format: "Judul Tahun" atau "Judul" saja
    use_gemini: bool = False  # True jika ada [gemini] tag
    custom_prompt: Optional[str] = None
    custom_synopsis: Optional[str] = None  # For [sinopsis] tag
    raw_text: str = ""
    is_valid: bool = False
    error_message: Optional[str] = None



class MessageParser:
    """
    Parser untuk command messages.
    """
    
    # Regex patterns
    # Pattern untuk handle target (quoted atau unquoted), lalu prompt
    # Format: /announce Target Context [optional: movies/series, judul tahun, sinopsis]
    ANNOUNCE_PATTERN = r'^/announce\s+(?:"([^"]+)"|(\S+))\s+(.+)$'
    # Format: /infofilm @username Context [optional: movies/series, judul tahun, sinopsis]
    INFOFILM_PATTERN = r'^/infofilm\s+@(\w+)\s+(.+)$'
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def parse(self, message_text: str) -> ParsedCommand:
        """
        Parse message text menjadi command object.
        
        Args:
            message_text: Raw message text
            
        Returns:
            ParsedCommand object
        """
        message_text = message_text.strip()
        
        # Check command type
        if message_text.startswith('/announce'):
            return self._parse_announce(message_text)
        elif message_text.startswith('/infofilm'):
            return self._parse_infofilm(message_text)
        elif message_text.startswith('/help'):
            return self._parse_help(message_text)
        elif message_text.startswith('/uploadmovie'):
            return self._parse_upload_command(message_text, 'uploadmovie')
        elif message_text.startswith('/uploadseries'):
            return self._parse_upload_command(message_text, 'uploadseries')
        elif message_text.startswith('/uploadseason'):
            return self._parse_upload_command(message_text, 'uploadseason')
        elif message_text.startswith('/uploadepisode'):
            return self._parse_upload_command(message_text, 'uploadepisode')
        elif message_text.startswith('/uploadhelp'):
            return self._parse_upload_command(message_text, 'uploadhelp')
        else:
            return ParsedCommand(
                command='unknown',
                raw_text=message_text,
                is_valid=False,
                error_message='Unknown command. Use /help or /uploadhelp for available commands'
            )
    
    def _parse_announce(self, message_text: str) -> ParsedCommand:
        """
        Parse /announce command.
        
        Format: 
        - /announce <channel> <context>
        - /announce <channel> [movies/series] <context> [judul tahun]
        - /announce <channel> [movies/series] <context> [sinopsis] <text> [judul tahun]
        
        Args:
            message_text: Raw message text
            
        Returns:
            ParsedCommand object
        """
        try:
            match = re.match(self.ANNOUNCE_PATTERN, message_text, re.IGNORECASE | re.DOTALL)
            
            if not match:
                return ParsedCommand(
                    command='announce',
                    raw_text=message_text,
                    is_valid=False,
                    error_message='Invalid format. Use: /announce <channel> <context> or /announce <channel> [movies/series] <context> [judul tahun]'
                )
            
            # Group 1 = quoted target, Group 2 = unquoted target, Group 3 = prompt
            target = match.group(1) if match.group(1) else match.group(2)
            prompt = match.group(3).strip()
            
            # Remove quotes from target if present
            target = target.strip().strip('"')
            
            # Extract tags using helpers (order matters!)
            media_type, prompt = extract_media_type(prompt)
            use_gemini, prompt = extract_gemini_tag(prompt)
            custom_synopsis, prompt = extract_custom_synopsis(prompt)
            title_year, custom_prompt = extract_title_year(prompt)
            
            # Validation
            error_msg = validate_media_type_requirement(title_year, media_type)
            if error_msg:
                return ParsedCommand(
                    command='announce',
                    raw_text=message_text,
                    is_valid=False,
                    error_message=error_msg
                )
            
            return ParsedCommand(
                command='announce',
                target=target,
                media_type=media_type,
                use_gemini=use_gemini,
                title_year=title_year,
                custom_prompt=custom_prompt,
                custom_synopsis=custom_synopsis,
                raw_text=message_text,
                is_valid=True
            )
            
        except Exception as e:
            logger.error(f"Failed to parse announce command: {e}")
            return ParsedCommand(
                command='announce',
                raw_text=message_text,
                is_valid=False,
                error_message=f'Error parsing command: {str(e)}'
            )
    
    def _parse_infofilm(self, message_text: str) -> ParsedCommand:
        """
        Parse /infofilm command.
        
        Format:
        - /infofilm @username <context>
        - /infofilm @username [movies/series] <context> [judul tahun]
        - /infofilm @username [movies/series] <context> [sinopsis] <text> [judul tahun]
        
        Args:
            message_text: Raw message text
            
        Returns:
            ParsedCommand object
        """
        try:
            match = re.match(self.INFOFILM_PATTERN, message_text, re.IGNORECASE | re.DOTALL)
            
            if not match:
                return ParsedCommand(
                    command='infofilm',
                    raw_text=message_text,
                    is_valid=False,
                    error_message='Invalid format. Use: /infofilm @username <context> or /infofilm @username [movies/series] <context> [judul tahun]'
                )
            
            # Group 1 = username, Group 2 = prompt
            username = match.group(1).strip()
            prompt = match.group(2).strip()
            
            # Extract tags using helpers (order matters!)
            media_type, prompt = extract_media_type(prompt)
            use_gemini, prompt = extract_gemini_tag(prompt)
            custom_synopsis, prompt = extract_custom_synopsis(prompt)
            title_year, custom_prompt = extract_title_year(prompt)
            
            # Validation
            error_msg = validate_media_type_requirement(title_year, media_type)
            if error_msg:
                return ParsedCommand(
                    command='infofilm',
                    raw_text=message_text,
                    is_valid=False,
                    error_message=error_msg
                )
            
            return ParsedCommand(
                command='infofilm',
                target=username,
                media_type=media_type,
                use_gemini=use_gemini,
                title_year=title_year,
                custom_prompt=custom_prompt,
                custom_synopsis=custom_synopsis,
                raw_text=message_text,
                is_valid=True
            )
            
        except Exception as e:
            logger.error(f"Failed to parse infofilm command: {e}")
            return ParsedCommand(
                command='infofilm',
                raw_text=message_text,
                is_valid=False,
                error_message=f'Error parsing command: {str(e)}'
            )
    
    def _parse_help(self, message_text: str) -> ParsedCommand:
        """
        Parse /help command.
        
        Format: /help
        
        Args:
            message_text: Raw message text
            
        Returns:
            ParsedCommand object
        """
        return ParsedCommand(
            command='help',
            raw_text=message_text,
            is_valid=True
        )
    
    def _parse_upload_command(self, message_text: str, command_type: str) -> ParsedCommand:
        """
        Parse upload commands (uploadmovie, uploadseries, uploadseason, uploadepisode, uploadhelp).
        Upload handlers will parse the full message content themselves.
        
        Args:
            message_text: Raw message text
            command_type: Type of upload command
            
        Returns:
            ParsedCommand object
        """
        return ParsedCommand(
            command=command_type,
            raw_text=message_text,
            is_valid=True
        )
    
    def extract_tmdb_ids(self, text: str) -> List[int]:
        """
        Extract semua TMDB IDs dari text.
        
        Args:
            text: Text yang mungkin contain TMDB IDs
            
        Returns:
            List of TMDB IDs
        """
        matches = re.findall(self.TMDB_ID_PATTERN, text)
        return [int(match) for match in matches]
    
    def is_command(self, message_text: str) -> bool:
        """
        Check apakah message adalah command.
        
        Args:
            message_text: Message text
            
        Returns:
            True jika message adalah command
        """
        return message_text.strip().startswith('/')


# Global instance
_message_parser: Optional[MessageParser] = None


def get_message_parser() -> MessageParser:
    """
    Get global MessageParser instance.
    
    Returns:
        MessageParser instance
    """
    global _message_parser
    if _message_parser is None:
        _message_parser = MessageParser()
    return _message_parser
