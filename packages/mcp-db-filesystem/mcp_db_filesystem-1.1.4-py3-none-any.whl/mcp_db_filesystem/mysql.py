"""MySQL database operations for MCP server."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import pymysql
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from .config import config

logger = logging.getLogger(__name__)


class MySQLSecurityError(Exception):
    """Raised when a MySQL query fails security checks."""
    pass


class MySQLConnectionError(Exception):
    """Raised when MySQL connection fails."""
    pass


class MySQLManager:
    """Manages MySQL connections and operations."""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
        self._metadata: Optional[MetaData] = None
        self._is_available: bool = False
        self._connection_error: Optional[str] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            # Check if MySQL configuration is provided
            if not hasattr(config, 'mysql') or not config.mysql.host:
                self._is_available = False
                self._connection_error = "MySQL configuration not provided"
                logger.info("MySQL configuration not found - MySQL features will be unavailable")
                return
            
            # Create MySQL connection URL
            if config.mysql.username and config.mysql.password:
                mysql_url = f"mysql+pymysql://{config.mysql.username}:{config.mysql.password}@{config.mysql.host}:{config.mysql.port}/{config.mysql.database}"
            else:
                mysql_url = f"mysql+pymysql://{config.mysql.host}:{config.mysql.port}/{config.mysql.database}"
            
            self._engine = create_engine(
                mysql_url,
                poolclass=QueuePool,
                pool_size=config.mysql.pool_size,
                max_overflow=config.mysql.max_overflow,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=config.server.debug,  # Log SQL queries in debug mode
                connect_args={
                    'connect_timeout': config.mysql.connection_timeout,
                    'charset': config.mysql.charset,
                }
            )
            
            self._metadata = MetaData()
            
            # Test the connection to ensure it's working
            if self.test_connection():
                self._is_available = True
                self._connection_error = None
                logger.info("MySQL engine initialized and connection test successful")
            else:
                self._is_available = False
                self._connection_error = "Connection test failed"
                logger.warning("MySQL engine initialized but connection test failed")
            
        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.warning(f"Failed to initialize MySQL engine: {e} - MySQL features will be unavailable")
            # Don't raise exception, just mark as unavailable
    
    def is_available(self) -> bool:
        """Check if MySQL is available for operations."""
        return self._is_available
    
    def get_connection_error(self) -> Optional[str]:
        """Get the last connection error message."""
        return self._connection_error
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to MySQL."""
        logger.info("Attempting to reconnect to MySQL...")
        self._initialize_engine()
        return self._is_available
    
    def _validate_sql_query(self, query: str) -> None:
        """Validate SQL query for security issues."""
        # Skip all validation if SQL protection is disabled (full access mode)
        if not config.security.enable_sql_injection_protection:
            logger.debug("SQL security validation skipped - full access mode enabled")
            return

        # Check query length
        if len(query) > config.security.max_query_length:
            raise MySQLSecurityError(f"Query exceeds maximum length of {config.security.max_query_length}")

        # Basic SQL injection patterns
        dangerous_patterns = [
            r';\s*(drop|delete|truncate|alter)\s+',
            r'union\s+select',
            r'exec\s*\(',
            r'xp_cmdshell',
            r'sp_executesql',
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise MySQLSecurityError(f"Query contains potentially dangerous pattern: {pattern}")

    @contextmanager
    def get_connection(self):
        """Get a MySQL connection with automatic cleanup."""
        if not self._is_available:
            raise MySQLConnectionError(f"MySQL is not available: {self._connection_error}")
        
        if not self._engine:
            raise MySQLConnectionError("MySQL engine not initialized")
        
        connection = None
        try:
            connection = self._engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"MySQL connection error: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a SELECT query and return results."""
        if not self._is_available:
            raise MySQLConnectionError(f"MySQL is not available: {self._connection_error}")
            
        self._validate_sql_query(query)
        
        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing MySQL query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing MySQL query: {query}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), parameters or {})
                
                # Convert result to list of dictionaries
                columns = list(result.keys())
                rows = []
                for row in result:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        row_dict[col_name] = row[i]
                    rows.append(row_dict)
                
                logger.info(f"MySQL query executed successfully, returned {len(rows)} rows")
                return {
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows)
                }
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"MySQL query execution failed: [{error_type}] {str(e)}"
            logger.error(error_msg)
            raise e

    def execute_non_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows count."""
        if not self._is_available:
            raise MySQLConnectionError(f"MySQL is not available: {self._connection_error}")
            
        self._validate_sql_query(query)
        
        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing MySQL non-query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing MySQL non-query: {query}")
        
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), parameters or {})
                conn.commit()
                
                affected_rows = result.rowcount
                logger.info(f"MySQL non-query executed successfully, affected {affected_rows} rows")
                return affected_rows
                
        except Exception as e:
            logger.error(f"MySQL non-query execution failed: {e}")
            raise

    def get_table_schema(self, table_name: str, schema_name: str = None) -> Dict[str, Any]:
        """Get table schema information."""
        if not self._is_available:
            raise MySQLConnectionError(f"MySQL is not available: {self._connection_error}")
            
        # MySQL uses database name instead of schema
        database_name = schema_name or config.mysql.database
        
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE,
            CASE WHEN COLUMN_KEY = 'PRI' THEN 1 ELSE 0 END AS IS_PRIMARY_KEY,
            COALESCE(COLUMN_COMMENT, '') AS COLUMN_DESCRIPTION
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = :table_name AND TABLE_SCHEMA = :database_name
        ORDER BY ORDINAL_POSITION
        """
        
        try:
            result = self.execute_query(query, {
                'table_name': table_name,
                'database_name': database_name
            })
            
            return {
                'table_name': table_name,
                'database_name': database_name,
                'columns': result['rows']
            }
            
        except Exception as e:
            logger.error(f"Failed to get MySQL table schema for {database_name}.{table_name}: {e}")
            raise

    def get_database_tables(self, database_name: str = None) -> List[str]:
        """Get list of tables in the database."""
        if not self._is_available:
            raise MySQLConnectionError(f"MySQL is not available: {self._connection_error}")
            
        database_name = database_name or config.mysql.database
        
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = :database_name
        ORDER BY TABLE_NAME
        """
        
        try:
            result = self.execute_query(query, {'database_name': database_name})
            return [row['TABLE_NAME'] for row in result['rows']]
            
        except Exception as e:
            logger.error(f"Failed to get MySQL database tables: {e}")
            raise

    def test_connection(self) -> bool:
        """Test MySQL connection."""
        if not self._engine:
            return False
            
        try:
            # Use direct engine connection for testing to avoid circular dependency
            connection = self._engine.connect()
            try:
                connection.execute(text("SELECT 1"))
                logger.debug("MySQL connection test successful")
                return True
            finally:
                connection.close()
        except Exception as e:
            logger.debug(f"MySQL connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close MySQL engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("MySQL engine closed")


# Global MySQL manager instance
mysql_manager = MySQLManager()
