"""
PostgreSQL RDS Database Connection Manager
Handles connection pooling and database sessions
"""
import logging
from contextlib import contextmanager
from typing import Optional

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extensions import connection

from src.config import Config


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    PostgreSQL RDS connection manager with connection pooling
    """
    
    def __init__(self):
        self._connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self._config = Config()
    
    def initialize(self):
        """Initialize the connection pool to PostgreSQL RDS"""
        try:
            logger.info(f"Initializing connection pool to PostgreSQL RDS at {self._config.DB_HOST}")
            
            # Create connection parameters
            conn_params = {
                'host': self._config.DB_HOST,
                'port': self._config.DB_PORT,
                'database': self._config.DB_NAME,
                'user': self._config.DB_USER,
                'password': self._config.DB_PASSWORD,
                'sslmode': self._config.DB_SSL_MODE,
                'connect_timeout': 10,
                'application_name': 'rbac_service'
            }
            
            # Create connection pool
            self._connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self._config.DB_POOL_SIZE,
                **conn_params
            )
            
            # Test the connection
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                logger.info(f"Connected to PostgreSQL: {version[0]}")
                cursor.close()
                self.release_connection(conn)
            
            logger.info("Database connection pool initialized successfully")
            
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self) -> connection:
        """
        Get a connection from the pool
        
        Returns:
            psycopg2 connection object
        """
        try:
            if self._connection_pool is None:
                raise RuntimeError("Connection pool not initialized")
            
            conn = self._connection_pool.getconn()
            if conn is None:
                raise RuntimeError("Failed to get connection from pool")
            
            return conn
            
        except pool.PoolError as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise
    
    def release_connection(self, conn: connection):
        """
        Return a connection back to the pool
        
        Args:
            conn: psycopg2 connection object to release
        """
        try:
            if self._connection_pool and conn:
                self._connection_pool.putconn(conn)
        except pool.PoolError as e:
            logger.error(f"Failed to release connection: {e}")
    
    @contextmanager
    def get_cursor(self, commit: bool = False):
        """
        Context manager for database operations
        
        Args:
            commit: Whether to commit the transaction
            
        Yields:
            psycopg2 cursor object
        """
        conn = None
        cursor = None
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            yield cursor
            
            if commit:
                conn.commit()
                
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.release_connection(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch_one: bool = False):
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single row if True, all rows if False
            
        Returns:
            Query results
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an UPDATE/INSERT/DELETE query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def close(self):
        """Close all connections in the pool"""
        if self._connection_pool:
            self._connection_pool.closeall()
            logger.info("Database connection pool closed")


# Singleton instance
_db_instance: Optional[DatabaseConnection] = None


def get_database() -> DatabaseConnection:
    """Get the singleton database connection instance"""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.initialize()
    
    return _db_instance

