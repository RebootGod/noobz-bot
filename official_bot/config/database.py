"""
Database Connection and Initialization
Handles SQLite database setup and connection management
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from config.settings import settings


class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        
    @contextmanager
    def get_connection(self):
        """
        Get database connection with context manager
        Automatically commits and closes connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """
        Execute a query and return results
        
        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
        
        Returns:
            List of Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_insert(self, query, params=None):
        """
        Execute insert query and return last inserted ID
        
        Args:
            query: SQL insert query
            params: Query parameters (tuple or dict)
        
        Returns:
            Last inserted row ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
    
    def execute_update(self, query, params=None):
        """
        Execute update/delete query and return affected rows
        
        Args:
            query: SQL update/delete query
            params: Query parameters (tuple or dict)
        
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount


# Create global database instance
db = Database()


def init_database():
    """
    Initialize database with schema
    Creates tables if they don't exist
    """
    try:
        schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with db.get_connection() as conn:
            conn.executescript(schema_sql)
        
        print("✅ Database initialized successfully")
        print(f"📂 Database location: {settings.DATABASE_PATH}")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def check_database_exists():
    """Check if database file exists"""
    return settings.DATABASE_PATH.exists()


def get_database_info():
    """Get database statistics"""
    try:
        tables = db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        info = {
            'path': str(settings.DATABASE_PATH),
            'exists': check_database_exists(),
            'tables': [row['name'] for row in tables],
        }
        
        # Get row counts
        for table in info['tables']:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            result = db.execute_query(count_query)
            info[f'{table}_count'] = result[0]['count'] if result else 0
        
        return info
        
    except Exception as e:
        return {
            'error': str(e),
            'path': str(settings.DATABASE_PATH),
            'exists': check_database_exists(),
        }
