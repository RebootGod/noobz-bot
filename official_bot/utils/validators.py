"""
Input Validators
Validate user inputs for security and correctness
"""

import re
from typing import Optional, Dict, Any
from config.constants import ValidationPatterns, Limits
import validators as external_validators


class InputValidator:
    """Validate user inputs"""
    
    @staticmethod
    def validate_tmdb_id(tmdb_id: str) -> Dict[str, Any]:
        """
        Validate TMDB ID
        
        Args:
            tmdb_id: TMDB ID string
            
        Returns:
            Dict with 'valid' (bool), 'value' (int), 'error' (str)
        """
        # Check pattern
        if not re.match(ValidationPatterns.TMDB_ID_PATTERN, tmdb_id):
            return {
                'valid': False,
                'value': None,
                'error': 'Invalid TMDB ID format. Must be a number (e.g., 550)'
            }
        
        # Convert to int
        try:
            tmdb_id_int = int(tmdb_id)
            
            if tmdb_id_int <= 0:
                return {
                    'valid': False,
                    'value': None,
                    'error': 'TMDB ID must be greater than 0'
                }
            
            return {
                'valid': True,
                'value': tmdb_id_int,
                'error': None
            }
        except ValueError:
            return {
                'valid': False,
                'value': None,
                'error': 'Invalid TMDB ID format'
            }
    
    @staticmethod
    def validate_url(url: str, check_https: bool = True) -> Dict[str, Any]:
        """
        Validate URL
        
        Args:
            url: URL string
            check_https: Whether to enforce HTTPS
            
        Returns:
            Dict with 'valid' (bool), 'value' (str), 'error' (str)
        """
        # Check basic URL format
        if not external_validators.url(url):
            return {
                'valid': False,
                'value': None,
                'error': 'Invalid URL format'
            }
        
        # Check HTTPS if required
        if check_https and not url.startswith('https://'):
            return {
                'valid': False,
                'value': None,
                'error': 'URL must use HTTPS protocol'
            }
        
        # Check URL length
        if len(url) > 500:
            return {
                'valid': False,
                'value': None,
                'error': 'URL too long (max 500 characters)'
            }
        
        return {
            'valid': True,
            'value': url,
            'error': None
        }
    
    @staticmethod
    def validate_embed_url(url: str) -> Dict[str, Any]:
        """
        Validate embed URL (must be from allowed domains)
        
        Args:
            url: Embed URL string
            
        Returns:
            Dict with 'valid' (bool), 'value' (str), 'error' (str)
        """
        # First validate as URL
        url_check = InputValidator.validate_url(url)
        if not url_check['valid']:
            return url_check
        
        # Check allowed domains
        allowed_domains = [
            'vidsrc.to',
            'vidsrc.me',
            'vidsrc.xyz',
            'embed.su',
            'embedsu.com',
        ]
        
        url_lower = url.lower()
        if not any(domain in url_lower for domain in allowed_domains):
            return {
                'valid': False,
                'value': None,
                'error': f'Embed URL must be from allowed domains: {", ".join(allowed_domains)}'
            }
        
        return {
            'valid': True,
            'value': url,
            'error': None
        }
    
    @staticmethod
    def validate_episode_number(episode_str: str) -> Dict[str, Any]:
        """
        Validate episode number
        
        Args:
            episode_str: Episode number string
            
        Returns:
            Dict with 'valid' (bool), 'value' (int), 'error' (str)
        """
        try:
            episode_num = int(episode_str)
            
            if episode_num < 1 or episode_num > Limits.MAX_EPISODE_NUMBER:
                return {
                    'valid': False,
                    'value': None,
                    'error': f'Episode number must be between 1 and {Limits.MAX_EPISODE_NUMBER}'
                }
            
            return {
                'valid': True,
                'value': episode_num,
                'error': None
            }
        except ValueError:
            return {
                'valid': False,
                'value': None,
                'error': 'Invalid episode number format'
            }
    
    @staticmethod
    def validate_season_number(season_str: str) -> Dict[str, Any]:
        """
        Validate season number
        
        Args:
            season_str: Season number string
            
        Returns:
            Dict with 'valid' (bool), 'value' (int), 'error' (str)
        """
        try:
            season_num = int(season_str)
            
            if season_num < 1 or season_num > Limits.MAX_SEASON_NUMBER:
                return {
                    'valid': False,
                    'value': None,
                    'error': f'Season number must be between 1 and {Limits.MAX_SEASON_NUMBER}'
                }
            
            return {
                'valid': True,
                'value': season_num,
                'error': None
            }
        except ValueError:
            return {
                'valid': False,
                'value': None,
                'error': 'Invalid season number format'
            }
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength
        
        Args:
            password: Password string
            
        Returns:
            Dict with 'valid' (bool), 'error' (str)
        """
        # Check minimum length
        if len(password) < Limits.PASSWORD_MIN_LENGTH:
            return {
                'valid': False,
                'error': f'Password must be at least {Limits.PASSWORD_MIN_LENGTH} characters'
            }
        
        # Check pattern (letters and numbers)
        if not re.match(ValidationPatterns.PASSWORD_PATTERN, password):
            return {
                'valid': False,
                'error': 'Password must contain both letters and numbers'
            }
        
        return {
            'valid': True,
            'error': None
        }
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input by removing potentially harmful characters
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        # Trim whitespace
        text = text.strip()
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes (SQL injection prevention)
        text = text.replace('\x00', '')
        
        return text


# Create global validator instance
input_validator = InputValidator()


# Convenience functions
def validate_tmdb_id(tmdb_id: str) -> Dict[str, Any]:
    """Validate TMDB ID"""
    return input_validator.validate_tmdb_id(tmdb_id)


def validate_url(url: str, check_https: bool = True) -> Dict[str, Any]:
    """Validate URL"""
    return input_validator.validate_url(url, check_https)


def validate_embed_url(url: str) -> Dict[str, Any]:
    """Validate embed URL"""
    return input_validator.validate_embed_url(url)


def validate_episode_number(episode_str: str) -> Dict[str, Any]:
    """Validate episode number"""
    return input_validator.validate_episode_number(episode_str)


def validate_season_number(season_str: str) -> Dict[str, Any]:
    """Validate season number"""
    return input_validator.validate_season_number(season_str)


def validate_password(password: str) -> Dict[str, Any]:
    """Validate password"""
    return input_validator.validate_password(password)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize input"""
    return input_validator.sanitize_input(text, max_length)
