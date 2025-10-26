"""
Authentication Service
Handle password authentication, creation, and management
"""

from datetime import datetime
from typing import Optional, Dict, Any
from config.database import db
from config.constants import PasswordType
from utils.crypto import hash_password, verify_password, get_password_hint
from utils.logger import logger, log_auth, log_error


class AuthService:
    """Manage password authentication"""
    
    def __init__(self):
        self.db = db
    
    def create_password(
        self,
        password: str,
        password_type: str = 'admin',
        created_by_telegram_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new password
        
        Args:
            password: Plain text password
            password_type: 'master' or 'admin'
            created_by_telegram_id: Telegram user ID who created it
            notes: Optional notes about the password
            
        Returns:
            Dict with 'success', 'password_id', 'password_hint', 'error'
        """
        try:
            # Validate password type
            if password_type not in ['master', 'admin']:
                return {
                    'success': False,
                    'password_id': None,
                    'password_hint': None,
                    'error': 'Invalid password type. Must be "master" or "admin"'
                }
            
            # Hash password
            password_hash = hash_password(password)
            password_hint = get_password_hint(password)
            
            # Insert into database
            query = """
                INSERT INTO passwords 
                (password_hash, password_type, password_hint, created_by_telegram_id, notes, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """
            
            password_id = self.db.execute_insert(
                query,
                (password_hash, password_type, password_hint, created_by_telegram_id, notes)
            )
            
            logger.info(f"✅ Password created: ID={password_id}, Type={password_type}, Hint={password_hint}")
            
            return {
                'success': True,
                'password_id': password_id,
                'password_hint': password_hint,
                'error': None
            }
            
        except Exception as e:
            log_error('create_password', e)
            return {
                'success': False,
                'password_id': None,
                'password_hint': None,
                'error': str(e)
            }
    
    def verify_password_attempt(self, password: str) -> Dict[str, Any]:
        """
        Verify password and return password info
        
        Args:
            password: Plain text password to verify
            
        Returns:
            Dict with 'valid', 'password_id', 'password_type', 'is_master', 'error'
        """
        try:
            # Get all active passwords
            query = """
                SELECT id, password_hash, password_type 
                FROM passwords 
                WHERE is_active = 1
            """
            
            passwords = self.db.execute_query(query)
            
            if not passwords:
                logger.warning("No active passwords found in database")
                return {
                    'valid': False,
                    'password_id': None,
                    'password_type': None,
                    'is_master': False,
                    'error': 'No active passwords found'
                }
            
            # Try to verify against each password
            for pwd in passwords:
                if verify_password(password, pwd['password_hash']):
                    # Password matched!
                    password_id = pwd['id']
                    password_type = pwd['password_type']
                    is_master = password_type == 'master'
                    
                    # Update last_used_at
                    self._update_password_last_used(password_id)
                    
                    logger.info(f"✅ Password verified: ID={password_id}, Type={password_type}")
                    
                    return {
                        'valid': True,
                        'password_id': password_id,
                        'password_type': password_type,
                        'is_master': is_master,
                        'error': None
                    }
            
            # No password matched
            logger.warning("Invalid password attempt")
            return {
                'valid': False,
                'password_id': None,
                'password_type': None,
                'is_master': False,
                'error': 'Invalid password'
            }
            
        except Exception as e:
            log_error('verify_password_attempt', e)
            return {
                'valid': False,
                'password_id': None,
                'password_type': None,
                'is_master': False,
                'error': str(e)
            }
    
    def _update_password_last_used(self, password_id: int):
        """Update password last_used_at timestamp"""
        try:
            query = """
                UPDATE passwords 
                SET last_used_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """
            self.db.execute_update(query, (password_id,))
        except Exception as e:
            log_error('update_password_last_used', e)
    
    def get_password_by_id(self, password_id: int) -> Optional[Dict[str, Any]]:
        """
        Get password information by ID
        
        Args:
            password_id: Password ID
            
        Returns:
            Password dict or None
        """
        try:
            query = """
                SELECT id, password_type, password_hint, created_at, 
                       last_used_at, total_uploads, notes, is_active
                FROM passwords 
                WHERE id = ?
            """
            
            result = self.db.execute_query(query, (password_id,))
            
            if result:
                return dict(result[0])
            return None
            
        except Exception as e:
            log_error('get_password_by_id', e)
            return None
    
    def get_all_passwords(self, include_inactive: bool = False) -> list:
        """
        Get all passwords
        
        Args:
            include_inactive: Whether to include inactive passwords
            
        Returns:
            List of password dicts
        """
        try:
            if include_inactive:
                query = """
                    SELECT id, password_type, password_hint, created_at, 
                           last_used_at, total_uploads, notes, is_active
                    FROM passwords 
                    ORDER BY created_at DESC
                """
            else:
                query = """
                    SELECT id, password_type, password_hint, created_at, 
                           last_used_at, total_uploads, notes, is_active
                    FROM passwords 
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                """
            
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
            
        except Exception as e:
            log_error('get_all_passwords', e)
            return []
    
    def revoke_password(self, password_id: int) -> Dict[str, Any]:
        """
        Revoke a password (set inactive)
        
        Args:
            password_id: Password ID to revoke
            
        Returns:
            Dict with 'success', 'error'
        """
        try:
            query = """
                UPDATE passwords 
                SET is_active = 0 
                WHERE id = ?
            """
            
            rows_affected = self.db.execute_update(query, (password_id,))
            
            if rows_affected > 0:
                logger.info(f"✅ Password revoked: ID={password_id}")
                return {
                    'success': True,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'error': 'Password not found'
                }
                
        except Exception as e:
            log_error('revoke_password', e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def increment_upload_count(self, password_id: int) -> bool:
        """
        Increment total_uploads counter for a password
        
        Args:
            password_id: Password ID
            
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE passwords 
                SET total_uploads = total_uploads + 1 
                WHERE id = ?
            """
            
            self.db.execute_update(query, (password_id,))
            return True
            
        except Exception as e:
            log_error('increment_upload_count', e)
            return False
    
    def create_initial_master_password(self, password: str) -> Dict[str, Any]:
        """
        Create the initial master password (first setup)
        Only works if no master password exists
        
        Args:
            password: Plain text master password
            
        Returns:
            Dict with 'success', 'password_hint', 'error'
        """
        try:
            # Check if master password already exists
            query = """
                SELECT COUNT(*) as count 
                FROM passwords 
                WHERE password_type = 'master' AND is_active = 1
            """
            
            result = self.db.execute_query(query)
            
            if result and result[0]['count'] > 0:
                return {
                    'success': False,
                    'password_hint': None,
                    'error': 'Master password already exists'
                }
            
            # Create master password
            result = self.create_password(
                password=password,
                password_type='master',
                notes='Initial master password'
            )
            
            if result['success']:
                logger.info("🎉 Initial master password created successfully!")
                return {
                    'success': True,
                    'password_hint': result['password_hint'],
                    'error': None
                }
            else:
                return result
                
        except Exception as e:
            log_error('create_initial_master_password', e)
            return {
                'success': False,
                'password_hint': None,
                'error': str(e)
            }


# Create global auth service instance
auth_service = AuthService()


# Convenience functions
def verify_password_attempt(password: str) -> Dict[str, Any]:
    """Verify password attempt"""
    return auth_service.verify_password_attempt(password)


def create_password(
    password: str,
    password_type: str = 'admin',
    created_by_telegram_id: Optional[int] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Create new password"""
    return auth_service.create_password(password, password_type, created_by_telegram_id, notes)


def create_initial_master_password(password: str) -> Dict[str, Any]:
    """Create initial master password"""
    return auth_service.create_initial_master_password(password)


def revoke_password(password_id: int) -> Dict[str, Any]:
    """Revoke password"""
    return auth_service.revoke_password(password_id)


def get_all_passwords(include_inactive: bool = False) -> list:
    """Get all passwords"""
    return auth_service.get_all_passwords(include_inactive)
