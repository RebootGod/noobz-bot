"""
Context Service
Manage upload context state for series → season → episodes flow
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from config.database import db
from config.constants import ContextType, UploadStep
from utils.logger import logger, log_error


class ContextService:
    """Manage upload context state"""
    
    def __init__(self):
        self.db = db
    
    def create_context(
        self,
        telegram_user_id: int,
        context_type: str,
        series_tmdb_id: Optional[int] = None,
        series_title: Optional[str] = None,
        season_number: Optional[int] = None,
        step: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new upload context
        Automatically deletes any existing context for the user
        
        Args:
            telegram_user_id: Telegram user ID
            context_type: Type of context ('movie', 'series', 'season', 'episode')
            series_tmdb_id: TMDB ID of series
            series_title: Title of series
            season_number: Season number
            step: Current step in the flow
            data: Additional data as dict (will be stored as JSON)
            
        Returns:
            Dict with 'success', 'context_id', 'error'
        """
        try:
            # Delete existing context
            self.delete_context(telegram_user_id)
            
            # Convert data dict to JSON string
            data_json = json.dumps(data) if data else None
            
            # Insert new context
            query = """
                INSERT INTO upload_contexts 
                (telegram_user_id, context_type, series_tmdb_id, series_title, 
                 season_number, step, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            context_id = self.db.execute_insert(
                query,
                (
                    telegram_user_id,
                    context_type,
                    series_tmdb_id,
                    series_title,
                    season_number,
                    step,
                    data_json
                )
            )
            
            logger.info(
                f"✅ Context created: User {telegram_user_id}, "
                f"Type: {context_type}, Series: {series_tmdb_id}, "
                f"Season: {season_number}, Step: {step}"
            )
            
            return {
                'success': True,
                'context_id': context_id,
                'error': None
            }
            
        except Exception as e:
            log_error('create_context', e)
            return {
                'success': False,
                'context_id': None,
                'error': str(e)
            }
    
    def get_context(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current upload context for a user
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            Context dict or None if not found
        """
        try:
            query = """
                SELECT id, telegram_user_id, context_type, series_tmdb_id, 
                       series_title, season_number, step, data, created_at, updated_at
                FROM upload_contexts 
                WHERE telegram_user_id = ?
            """
            
            result = self.db.execute_query(query, (telegram_user_id,))
            
            if not result:
                return None
            
            context = dict(result[0])
            
            # Parse JSON data
            if context['data']:
                try:
                    context['data'] = json.loads(context['data'])
                except json.JSONDecodeError:
                    context['data'] = None
            
            return context
            
        except Exception as e:
            log_error('get_context', e)
            return None
    
    def update_context(
        self,
        telegram_user_id: int,
        series_tmdb_id: Optional[int] = None,
        series_title: Optional[str] = None,
        season_number: Optional[int] = None,
        step: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        merge_data: bool = False
    ) -> Dict[str, Any]:
        """
        Update existing upload context
        
        Args:
            telegram_user_id: Telegram user ID
            series_tmdb_id: New TMDB ID (optional)
            series_title: New series title (optional)
            season_number: New season number (optional)
            step: New step (optional)
            data: New data dict (optional)
            merge_data: If True, merge with existing data instead of replacing
            
        Returns:
            Dict with 'success', 'error'
        """
        try:
            # Get existing context
            existing = self.get_context(telegram_user_id)
            
            if not existing:
                return {
                    'success': False,
                    'error': 'No context found for user'
                }
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            if series_tmdb_id is not None:
                update_fields.append('series_tmdb_id = ?')
                params.append(series_tmdb_id)
            
            if series_title is not None:
                update_fields.append('series_title = ?')
                params.append(series_title)
            
            if season_number is not None:
                update_fields.append('season_number = ?')
                params.append(season_number)
            
            if step is not None:
                update_fields.append('step = ?')
                params.append(step)
            
            if data is not None:
                if merge_data and existing['data']:
                    # Merge with existing data
                    merged_data = {**existing['data'], **data}
                    data_json = json.dumps(merged_data)
                else:
                    # Replace data
                    data_json = json.dumps(data)
                
                update_fields.append('data = ?')
                params.append(data_json)
            
            if not update_fields:
                return {
                    'success': False,
                    'error': 'No fields to update'
                }
            
            # Always update updated_at
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            
            # Add telegram_user_id to params for WHERE clause
            params.append(telegram_user_id)
            
            # Execute update
            query = f"""
                UPDATE upload_contexts 
                SET {', '.join(update_fields)}
                WHERE telegram_user_id = ?
            """
            
            self.db.execute_update(query, tuple(params))
            
            logger.info(f"✅ Context updated for user {telegram_user_id}")
            
            return {
                'success': True,
                'error': None
            }
            
        except Exception as e:
            log_error('update_context', e)
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_context(self, telegram_user_id: int) -> bool:
        """
        Delete upload context for a user
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if successful
        """
        try:
            query = "DELETE FROM upload_contexts WHERE telegram_user_id = ?"
            
            rows_affected = self.db.execute_update(query, (telegram_user_id,))
            
            if rows_affected > 0:
                logger.info(f"🗑️ Context deleted for user {telegram_user_id}")
            
            return True
            
        except Exception as e:
            log_error('delete_context', e)
            return False
    
    def has_context(self, telegram_user_id: int) -> bool:
        """
        Check if user has an active context
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            True if context exists
        """
        context = self.get_context(telegram_user_id)
        return context is not None
    
    def get_series_context(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get series context specifically
        
        Args:
            telegram_user_id: Telegram user ID
            
        Returns:
            Series context dict or None
        """
        context = self.get_context(telegram_user_id)
        
        if context and context.get('series_tmdb_id'):
            return {
                'tmdb_id': context['series_tmdb_id'],
                'title': context['series_title'],
                'season_number': context['season_number'],
                'step': context['step'],
                'data': context['data']
            }
        
        return None
    
    def cleanup_old_contexts(self, days: int = 7) -> int:
        """
        Delete contexts older than specified days
        
        Args:
            days: Number of days to keep contexts
            
        Returns:
            Number of contexts deleted
        """
        try:
            query = """
                DELETE FROM upload_contexts 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            """
            
            rows_affected = self.db.execute_update(query, (days,))
            
            if rows_affected > 0:
                logger.info(f"🧹 Cleaned up {rows_affected} old context(s)")
            
            return rows_affected
            
        except Exception as e:
            log_error('cleanup_old_contexts', e)
            return 0


# Create global context service instance
context_service = ContextService()


# Convenience functions
def create_series_context(
    telegram_user_id: int,
    series_tmdb_id: int,
    series_title: str,
    season_number: Optional[int] = None,
    step: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create series upload context"""
    return context_service.create_context(
        telegram_user_id=telegram_user_id,
        context_type='series',
        series_tmdb_id=series_tmdb_id,
        series_title=series_title,
        season_number=season_number,
        step=step,
        data=data
    )


def get_context(telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """Get user's upload context"""
    return context_service.get_context(telegram_user_id)


def update_context(
    telegram_user_id: int,
    **kwargs
) -> Dict[str, Any]:
    """Update user's upload context"""
    return context_service.update_context(telegram_user_id, **kwargs)


def delete_context(telegram_user_id: int) -> bool:
    """Delete user's upload context"""
    return context_service.delete_context(telegram_user_id)


def has_context(telegram_user_id: int) -> bool:
    """Check if user has active context"""
    return context_service.has_context(telegram_user_id)


def get_series_context(telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """Get series context"""
    return context_service.get_series_context(telegram_user_id)
