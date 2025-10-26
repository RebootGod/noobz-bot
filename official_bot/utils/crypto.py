"""
Cryptography Utilities
Password hashing and verification using bcrypt
"""

import bcrypt
from config.constants import Limits


class PasswordHasher:
    """Handle password hashing and verification with bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
            
        Raises:
            ValueError: If password is too short
        """
        if len(password) < Limits.PASSWORD_MIN_LENGTH:
            raise ValueError(
                f"Password must be at least {Limits.PASSWORD_MIN_LENGTH} characters"
            )
        
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)  # Cost factor 12 for security
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def get_password_hint(password: str) -> str:
        """
        Generate password hint (last 4 characters)
        For display purposes: ****1234
        
        Args:
            password: Plain text password
            
        Returns:
            Password hint string
        """
        if len(password) < 4:
            return '*' * len(password)
        
        return '****' + password[-4:]


# Create global instance
password_hasher = PasswordHasher()


# Convenience functions
def hash_password(password: str) -> str:
    """Hash a password"""
    return password_hasher.hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password"""
    return password_hasher.verify_password(password, hashed)


def get_password_hint(password: str) -> str:
    """Get password hint"""
    return password_hasher.get_password_hint(password)
