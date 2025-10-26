"""
Message Parsers
Parse user messages for bulk upload and other complex inputs
"""

import re
from typing import List, Dict, Any, Optional
from config.constants import ValidationPatterns
from utils.validators import (
    validate_episode_number,
    validate_url,
    validate_embed_url,
    sanitize_input
)


class BulkEpisodeParser:
    """Parse bulk episode upload format"""
    
    @staticmethod
    def parse_line(line: str) -> Dict[str, Any]:
        """
        Parse single line of bulk episode format
        Format: EP | EMBED_URL | DOWNLOAD_URL
        
        Args:
            line: Input line
            
        Returns:
            Dict with 'valid', 'episode', 'embed_url', 'download_url', 'error'
        """
        # Sanitize input
        line = sanitize_input(line, max_length=2000)
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return {
                'valid': False,
                'episode': None,
                'embed_url': None,
                'download_url': None,
                'error': 'Empty line'
            }
        
        # Split by pipe
        parts = [part.strip() for part in line.split('|')]
        
        if len(parts) != 3:
            return {
                'valid': False,
                'episode': None,
                'embed_url': None,
                'download_url': None,
                'error': f'Invalid format. Expected 3 parts, got {len(parts)}. Format: EP | EMBED_URL | DOWNLOAD_URL'
            }
        
        episode_str, embed_url, download_url = parts
        
        # Validate episode number
        episode_check = validate_episode_number(episode_str)
        if not episode_check['valid']:
            return {
                'valid': False,
                'episode': None,
                'embed_url': None,
                'download_url': None,
                'error': f"Episode number error: {episode_check['error']}"
            }
        
        # Validate embed URL
        embed_check = validate_embed_url(embed_url)
        if not embed_check['valid']:
            return {
                'valid': False,
                'episode': episode_check['value'],
                'embed_url': None,
                'download_url': None,
                'error': f"Embed URL error: {embed_check['error']}"
            }
        
        # Validate download URL (optional, "-" means no download URL)
        download_url_final = None
        if download_url and download_url != '-':
            download_check = validate_url(download_url, check_https=True)
            if not download_check['valid']:
                return {
                    'valid': False,
                    'episode': episode_check['value'],
                    'embed_url': embed_check['value'],
                    'download_url': None,
                    'error': f"Download URL error: {download_check['error']}"
                }
            download_url_final = download_check['value']
        
        return {
            'valid': True,
            'episode': episode_check['value'],
            'embed_url': embed_check['value'],
            'download_url': download_url_final,
            'error': None
        }
    
    @staticmethod
    def parse_bulk(text: str, max_episodes: int = 20) -> Dict[str, Any]:
        """
        Parse bulk episode upload text
        
        Args:
            text: Multi-line input text
            max_episodes: Maximum allowed episodes
            
        Returns:
            Dict with 'valid', 'episodes' (list), 'errors' (list), 'summary'
        """
        lines = text.strip().split('\n')
        
        episodes = []
        errors = []
        
        for line_num, line in enumerate(lines, start=1):
            # Skip empty lines
            if not line.strip():
                continue
            
            result = BulkEpisodeParser.parse_line(line)
            
            if result['valid']:
                # Check for duplicates
                if any(ep['episode'] == result['episode'] for ep in episodes):
                    errors.append({
                        'line': line_num,
                        'error': f"Duplicate episode number: {result['episode']}"
                    })
                else:
                    episodes.append({
                        'episode': result['episode'],
                        'embed_url': result['embed_url'],
                        'download_url': result['download_url'],
                        'line': line_num
                    })
            else:
                # Skip "Empty line" errors
                if result['error'] != 'Empty line':
                    errors.append({
                        'line': line_num,
                        'error': result['error']
                    })
        
        # Check episode count
        if len(episodes) > max_episodes:
            return {
                'valid': False,
                'episodes': [],
                'errors': [{
                    'line': 0,
                    'error': f'Too many episodes. Maximum is {max_episodes}, got {len(episodes)}'
                }],
                'summary': {
                    'total_lines': len(lines),
                    'valid_episodes': 0,
                    'errors': 1
                }
            }
        
        # Sort episodes by episode number
        episodes.sort(key=lambda x: x['episode'])
        
        return {
            'valid': len(errors) == 0 and len(episodes) > 0,
            'episodes': episodes,
            'errors': errors,
            'summary': {
                'total_lines': len(lines),
                'valid_episodes': len(episodes),
                'errors': len(errors)
            }
        }


class ManualEpisodeParser:
    """Parse manual episode upload format (with titles)"""
    
    @staticmethod
    def parse_line_full(line: str) -> Dict[str, Any]:
        """
        Parse full format line
        Format: EP | TITLE | EMBED_URL | DOWNLOAD_URL
        
        Args:
            line: Input line
            
        Returns:
            Dict with episode data and validation result
        """
        # Sanitize input
        line = sanitize_input(line, max_length=2000)
        line = line.strip()
        
        # Skip empty lines
        if not line:
            return {
                'valid': False,
                'episode': None,
                'title': None,
                'embed_url': None,
                'download_url': None,
                'error': 'Empty line'
            }
        
        # Split by pipe
        parts = [part.strip() for part in line.split('|')]
        
        if len(parts) != 4:
            return {
                'valid': False,
                'episode': None,
                'title': None,
                'embed_url': None,
                'download_url': None,
                'error': f'Invalid format. Expected 4 parts, got {len(parts)}. Format: EP | TITLE | EMBED_URL | DOWNLOAD_URL'
            }
        
        episode_str, title, embed_url, download_url = parts
        
        # Validate episode number
        episode_check = validate_episode_number(episode_str)
        if not episode_check['valid']:
            return {
                'valid': False,
                'episode': None,
                'title': None,
                'embed_url': None,
                'download_url': None,
                'error': f"Episode number error: {episode_check['error']}"
            }
        
        # Validate title
        if not title or len(title) < 1:
            return {
                'valid': False,
                'episode': episode_check['value'],
                'title': None,
                'embed_url': None,
                'download_url': None,
                'error': 'Title cannot be empty'
            }
        
        title = sanitize_input(title, max_length=200)
        
        # Validate embed URL
        embed_check = validate_embed_url(embed_url)
        if not embed_check['valid']:
            return {
                'valid': False,
                'episode': episode_check['value'],
                'title': title,
                'embed_url': None,
                'download_url': None,
                'error': f"Embed URL error: {embed_check['error']}"
            }
        
        # Validate download URL (optional)
        download_url_final = None
        if download_url and download_url != '-':
            download_check = validate_url(download_url, check_https=True)
            if not download_check['valid']:
                return {
                    'valid': False,
                    'episode': episode_check['value'],
                    'title': title,
                    'embed_url': embed_check['value'],
                    'download_url': None,
                    'error': f"Download URL error: {download_check['error']}"
                }
            download_url_final = download_check['value']
        
        return {
            'valid': True,
            'episode': episode_check['value'],
            'title': title,
            'embed_url': embed_check['value'],
            'download_url': download_url_final,
            'error': None
        }


# Create global parser instances
bulk_episode_parser = BulkEpisodeParser()
manual_episode_parser = ManualEpisodeParser()


# Convenience functions
def parse_bulk_episodes(text: str, max_episodes: int = 20) -> Dict[str, Any]:
    """
    Parse bulk episode upload text
    
    Args:
        text: Multi-line input
        max_episodes: Maximum episodes allowed
        
    Returns:
        Parsing result dict
    """
    return bulk_episode_parser.parse_bulk(text, max_episodes)


def parse_manual_episode(line: str) -> Dict[str, Any]:
    """
    Parse manual episode line (with title)
    
    Args:
        line: Input line
        
    Returns:
        Parsing result dict
    """
    return manual_episode_parser.parse_line_full(line)


def generate_bulk_template(start_episode: int, end_episode: int) -> str:
    """
    Generate bulk upload template
    
    Args:
        start_episode: Starting episode number
        end_episode: Ending episode number
        
    Returns:
        Template string
    """
    lines = []
    for ep in range(start_episode, end_episode + 1):
        lines.append(f"{ep} | https://vidsrc.to/embed/... | -")
    
    return '\n'.join(lines)
