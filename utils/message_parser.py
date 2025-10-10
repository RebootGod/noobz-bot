"""
Message Parser utility untuk parse commands dari user.
Extract command, parameters, dan arguments.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

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
    custom_prompt: Optional[str] = None
    raw_text: str = ""
    is_valid: bool = False
    error_message: Optional[str] = None


class MessageParser:
    """
    Parser untuk command messages.
    """
    
    # Regex patterns
    ANNOUNCE_PATTERN = r'^/announce\s+(.+?)\s+(.+)$'
    INFOFILM_PATTERN = r'^/infofilm\s+@(\w+)\s+(movie|tv|series)\s+(.+?)(?:\s+(\d{4}))?$'
    TMDB_ID_PATTERN = r'\[(\d+)\]'
    
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
        else:
            return ParsedCommand(
                command='unknown',
                raw_text=message_text,
                is_valid=False,
                error_message='Unknown command. Use /announce, /infofilm, or /help'
            )
    
    def _parse_announce(self, message_text: str) -> ParsedCommand:
        """
        Parse /announce command.
        
        Format: /announce <channel/group name> <prompt with [tmdbid]>
        
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
                    error_message='Invalid format. Use: /announce <channel/group name> <prompt>'
                )
            
            target = match.group(1).strip()
            prompt = match.group(2).strip()
            
            # Extract TMDB ID jika ada
            tmdb_id = None
            tmdb_match = re.search(self.TMDB_ID_PATTERN, prompt)
            if tmdb_match:
                tmdb_id = int(tmdb_match.group(1))
                # Remove TMDB ID dari prompt untuk custom prompt
                custom_prompt = re.sub(self.TMDB_ID_PATTERN, '', prompt).strip()
            else:
                custom_prompt = prompt
            
            return ParsedCommand(
                command='announce',
                target=target,
                tmdb_id=tmdb_id,
                custom_prompt=custom_prompt,
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
        
        Format: /infofilm @username <movie|tv|series> <keyword> [year]
        
        Args:
            message_text: Raw message text
            
        Returns:
            ParsedCommand object
        """
        try:
            match = re.match(self.INFOFILM_PATTERN, message_text, re.IGNORECASE)
            
            if not match:
                return ParsedCommand(
                    command='infofilm',
                    raw_text=message_text,
                    is_valid=False,
                    error_message='Invalid format. Use: /infofilm @username <movie|tv> <keyword> [year]'
                )
            
            username = match.group(1).strip()
            content_type = match.group(2).strip().lower()
            keyword = match.group(3).strip()
            year_str = match.group(4)
            
            # Normalize content type
            if content_type in ['series', 'tv']:
                content_type = 'tv'
            else:
                content_type = 'movie'
            
            # Parse year
            year = None
            if year_str:
                try:
                    year = int(year_str)
                except ValueError:
                    pass
            
            return ParsedCommand(
                command='infofilm',
                target=username,
                content_type=content_type,
                keyword=keyword,
                year=year,
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
