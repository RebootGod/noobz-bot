"""
Session Management Service
Handle user sessions with 24-hour expiry
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.database import db
from config.settings import settings
from utils.logger import logger, log_auth, log_error


class SessionService:
    """Manage user sessions"""
    
    def __init__(self):
        self.db = db
        self.session_expiry_hours = settings.SESSION_EXPIRY_HOURS
    
    def create_session(
        self,
        telegram_user_id: int,
        telegram_username: Optional[str],
        password_id: int,
        is_master: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new session for a user
        Automatically deletes any existing session for the user
        
        Args:
            telegram_user_id: Telegram user ID
            telegram_username: Telegram username
            password_id: Password ID used for authentication
            is_master: Whether user has master access
            
        Returns:
            Dict with 'success', 'session_token', 'expires_at', 'error'
        """
        try:
            # Delete existing session if any
            self.delete_session(telegram_user_id)
            
            # Generate secure session token
            session_token = secrets.token_urlsafe(32)
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(hours=self.session_expiry_hours)
            
            # Insert new session
            query = """
                INSERT INTO sessions 
                (telegram_user_id, telegram_username, password_id, session_token, is_master, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db.execute_insert(
                query,
                (
                    telegram_user_id,
                    telegram_username,
                    password_id,
                    session_token,
                    1 if is_master else 0,
                    expires_at.isoformat()
                )
            )
            
            log_auth(telegram_user_id, telegram_username or 'unknown', is_master)
            logger.info(
                f"✅ Session created: User {telegram_user_id} "
                f"(Master: {is_master}), Expires: {expires_at}"
            )
            
            return {
                'success': True,
                'session_token': session_token,
                'expires_at': expires_at,
                'error': None
            }
            
        except Exception as e:
            log_error('create_session', e)
            return {
                'success': False,
                'session_token': None,
                'expires_at': None,
                'error': str(e)
            }
    
    def get_active_session(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get active session for a user
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            Session dict or None if not found or expired
        """
        try:
            query = """
                SELECT id, telegram_user_id, telegram_username, password_id, 
                       session_token, is_master, created_at, expires_at, last_activity
                FROM sessions 
                WHERE telegram_user_id = ?
            """
            
            result = self.db.execute_query(query, (telegram_user_id,))
            
            if not result:
                return None
            
            session = dict(result[0])
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session['expires_at'])
            
            if datetime.now() > expires_at:
                logger.warning(f"Session expired for user {telegram_user_id}")
                self.delete_session(telegram_user_id)
                return None
            
            return session
            
        except Exception as e:
            log_error('get_session', e)
            return None
    
    def is_authenticated(self, telegram_user_id: int) -> bool:
        """
        Check if user has valid session
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if user is authenticated
        """
        session = self.get_active_session(telegram_user_id)
        return session is not None
    
    def is_master(self, telegram_user_id: int) -> bool:
        """
        Check if user has master access
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if user has master access
        """
        session = self.get_active_session(telegram_user_id)
        if session:
            return session['is_master'] == 1
        return False
    
    def update_last_activity(self, telegram_user_id: int) -> bool:
        """
        Update session last activity timestamp
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            query = """
                UPDATE sessions 
                SET last_activity = CURRENT_TIMESTAMP 
                WHERE telegram_user_id = ?
            """
            
            self.db.execute_update(query, (telegram_user_id,))
            return True
            
        except Exception as e:
            log_error('update_last_activity', e)
            return False
    
    def delete_session(self, telegram_user_id: int) -> bool:
        """
        Delete user session (logout)
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            query = "DELETE FROM sessions WHERE telegram_user_id = ?"
            
            rows_affected = self.db.execute_update(query, (telegram_user_id,))
            
            if rows_affected > 0:
                logger.info(f"🔓 Session deleted for user {telegram_user_id}")
            
            return True
            
        except Exception as e:
            log_error('delete_session', e)
            return False
    
    def delete_sessions_by_password(self, password_id: int) -> int:
        """
        Delete all sessions using a specific password
        Used when password is revoked
        
        Args:
            password_id: Password ID
            
        Returns:
            Number of sessions deleted
        """
        try:
            query = "DELETE FROM sessions WHERE password_id = ?"
            
            rows_affected = self.db.execute_update(query, (password_id,))
            
            if rows_affected > 0:
                logger.info(f"🔓 {rows_affected} session(s) deleted for password ID {password_id}")
            
            return rows_affected
            
        except Exception as e:
            log_error('delete_sessions_by_password', e)
            return 0
    
    def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions
        Should be called periodically (e.g., daily)
        
        Returns:
            Number of sessions deleted
        """
        try:
            query = "DELETE FROM sessions WHERE expires_at < datetime('now')"
            
            rows_affected = self.db.execute_update(query)
            
            if rows_affected > 0:
                logger.info(f"🧹 Cleaned up {rows_affected} expired session(s)")
            
            return rows_affected
            
        except Exception as e:
            log_error('cleanup_expired_sessions', e)
            return 0
    
    def get_all_sessions(self, active_only: bool = True) -> list:
        """
        Get all sessions
        
        Args:
            active_only: Only return non-expired sessions
            
        Returns:
            List of session dicts
        """
        try:
            if active_only:
                query = """
                    SELECT s.id, s.telegram_user_id, s.telegram_username, 
                           s.password_id, s.is_master, s.created_at, s.expires_at, s.last_activity,
                           p.password_hint, p.password_type
                    FROM sessions s
                    JOIN passwords p ON s.password_id = p.id
                    WHERE s.expires_at > datetime('now')
                    ORDER BY s.created_at DESC
                """
            else:
                query = """
                    SELECT s.id, s.telegram_user_id, s.telegram_username, 
                           s.password_id, s.is_master, s.created_at, s.expires_at, s.last_activity,
                           p.password_hint, p.password_type
                    FROM sessions s
                    JOIN passwords p ON s.password_id = p.id
                    ORDER BY s.created_at DESC
                """
            
            results = self.db.execute_query(query)
            return [dict(row) for row in results]
            
        except Exception as e:
            log_error('get_all_sessions', e)
            return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            Dict with session stats
        """
        try:
            # Total active sessions
            query_active = """
                SELECT COUNT(*) as count 
                FROM sessions 
                WHERE expires_at > datetime('now')
            """
            
            # Total master sessions
            query_master = """
                SELECT COUNT(*) as count 
                FROM sessions 
                WHERE is_master = 1 AND expires_at > datetime('now')
            """
            
            active_result = self.db.execute_query(query_active)
            master_result = self.db.execute_query(query_master)
            
            return {
                'total_active': active_result[0]['count'] if active_result else 0,
                'total_master': master_result[0]['count'] if master_result else 0,
                'total_admin': (active_result[0]['count'] - master_result[0]['count']) if active_result and master_result else 0
            }
            
        except Exception as e:
            log_error('get_session_stats', e)
            return {
                'total_active': 0,
                'total_master': 0,
                'total_admin': 0
            }


# Create global session service instance
session_service = SessionService()


# Convenience functions
def create_session(
    telegram_user_id: int,
    telegram_username: Optional[str],
    password_id: int,
    is_master: bool = False
) -> Dict[str, Any]:
    """Create new session"""
    return session_service.create_session(
        telegram_user_id,
        telegram_username,
        password_id,
        is_master
    )


def get_session(telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """Get user session"""
    return session_service.get_active_session(telegram_user_id)


def is_authenticated(telegram_user_id: int) -> bool:
    """Check if user is authenticated"""
    return session_service.is_authenticated(telegram_user_id)


def is_master(telegram_user_id: int) -> bool:
    """Check if user has master access"""
    return session_service.is_master(telegram_user_id)


def delete_session(telegram_user_id: int) -> bool:
    """Delete user session (logout)"""
    return session_service.delete_session(telegram_user_id)


def update_last_activity(telegram_user_id: int) -> bool:
    """Update session activity"""
    return session_service.update_last_activity(telegram_user_id)


def cleanup_expired_sessions() -> int:
    """Cleanup expired sessions"""
    return session_service.cleanup_expired_sessions()
