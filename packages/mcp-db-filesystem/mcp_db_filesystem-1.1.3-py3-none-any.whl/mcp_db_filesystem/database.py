"""SQL Server database operations for MCP server."""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import pyodbc
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

from .config import config

logger = logging.getLogger(__name__)


class SQLSecurityError(Exception):
    """Raised when a SQL query fails security checks."""
    pass


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class SQLServerManager:
    """Manages SQL Server connections and operations."""

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._metadata: Optional[MetaData] = None
        self._is_available: bool = False
        self._connection_error: Optional[str] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize SQLAlchemy engine with connection pooling."""
        try:
            # Convert pyodbc connection string to SQLAlchemy format
            connection_string = config.database.connection_string
            sqlalchemy_url = f"mssql+pyodbc:///?odbc_connect={connection_string}"

            self._engine = create_engine(
                sqlalchemy_url,
                poolclass=QueuePool,
                pool_size=config.database.pool_size,
                max_overflow=config.database.max_overflow,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=config.server.debug,  # Log SQL queries in debug mode
            )

            self._metadata = MetaData()

            # Test the connection to ensure it's working
            if self.test_connection():
                self._is_available = True
                self._connection_error = None
                logger.info("Database engine initialized and connection test successful")
            else:
                self._is_available = False
                self._connection_error = "Connection test failed"
                logger.warning("Database engine initialized but connection test failed")

        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.warning(f"Failed to initialize database engine: {e} - Database features will be unavailable")
            # Don't raise exception, just mark as unavailable

    def is_available(self) -> bool:
        """Check if database is available for operations."""
        return self._is_available

    def get_connection_error(self) -> Optional[str]:
        """Get the last connection error message."""
        return self._connection_error

    def reconnect(self) -> bool:
        """Attempt to reconnect to the database."""
        logger.info("Attempting to reconnect to database...")
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
            raise SQLSecurityError(f"Query exceeds maximum length of {config.security.max_query_length}")

        # Convert to uppercase for keyword checking
        query_upper = query.upper()

        # Check for blocked keywords (only if any are configured)
        if config.security.blocked_sql_keywords:
            for keyword in config.security.blocked_sql_keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_upper):
                    raise SQLSecurityError(f"Blocked SQL keyword detected: {keyword}")
        else:
            logger.debug("No blocked SQL keywords configured - allowing all SQL commands")

        # Skip injection pattern checks if no keywords are blocked (full access mode)
        if not config.security.blocked_sql_keywords:
            logger.debug("SQL injection pattern checks skipped - full access mode")
            return

        # Check for common SQL injection patterns (only when security is enabled)
        injection_patterns = [
            r";\s*(DROP|DELETE|UPDATE|INSERT|CREATE|ALTER|EXEC|EXECUTE)",
            r"UNION\s+SELECT",
            r"--\s*$",
            r"/\*.*\*/",
            r"'\s*(OR|AND)\s*'",
            r"'\s*=\s*'",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, query_upper, re.MULTILINE):
                raise SQLSecurityError(f"Potential SQL injection detected: {pattern}")

        logger.debug("SQL query passed security validation")
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup."""
        if not self._is_available:
            raise DatabaseConnectionError(f"Database is not available: {self._connection_error}")

        if not self._engine:
            raise DatabaseConnectionError("Database engine not initialized")

        connection = None
        try:
            connection = self._engine.connect()
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
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
            raise DatabaseConnectionError(f"Database is not available: {self._connection_error}")

        self._validate_sql_query(query)

        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing query: {query}")

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
                
                logger.info(f"Query executed successfully, returned {len(rows)} rows")
                return {
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows)
                }
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = f"Query execution failed: [{error_type}] {str(e)}"
            logger.error(error_msg)

            # 提供更具体的错误信息
            if hasattr(e, 'args') and e.args:
                logger.error(f"Error details: {e.args}")

            raise e
    
    def execute_non_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> int:
        """Execute an INSERT, UPDATE, or DELETE query and return affected rows count."""
        if not self._is_available:
            raise DatabaseConnectionError(f"Database is not available: {self._connection_error}")

        self._validate_sql_query(query)

        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing non-query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing non-query: {query}")

        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), parameters or {})
                conn.commit()
                
                affected_rows = result.rowcount
                logger.info(f"Non-query executed successfully, affected {affected_rows} rows")
                return affected_rows
                
        except Exception as e:
            logger.error(f"Non-query execution failed: {e}")
            raise
    
    def get_table_schema(self, table_name: str, schema_name: str = "dbo") -> Dict[str, Any]:
        """Get table schema information."""
        if not self._is_available:
            raise DatabaseConnectionError(f"Database is not available: {self._connection_error}")
        query = """
        SELECT
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END AS IS_PRIMARY_KEY,
            ISNULL(ep.value, '') AS COLUMN_DESCRIPTION
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN (
            SELECT ku.TABLE_CATALOG, ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
            INNER JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS ku
                ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
        ) pk ON c.TABLE_CATALOG = pk.TABLE_CATALOG
            AND c.TABLE_SCHEMA = pk.TABLE_SCHEMA
            AND c.TABLE_NAME = pk.TABLE_NAME
            AND c.COLUMN_NAME = pk.COLUMN_NAME
        LEFT JOIN sys.extended_properties ep ON ep.major_id = OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME)
            AND ep.minor_id = c.ORDINAL_POSITION
            AND ep.name = 'MS_Description'
        WHERE c.TABLE_NAME = :table_name AND c.TABLE_SCHEMA = :schema_name
        ORDER BY c.ORDINAL_POSITION
        """
        
        try:
            result = self.execute_query(query, {
                'table_name': table_name,
                'schema_name': schema_name
            })
            
            return {
                'table_name': table_name,
                'schema_name': schema_name,
                'columns': result['rows']
            }
            
        except Exception as e:
            logger.error(f"Failed to get table schema for {schema_name}.{table_name}: {e}")
            raise
    
    def get_database_tables(self, schema_name: str = "dbo") -> List[str]:
        """Get list of tables in the database."""
        if not self._is_available:
            raise DatabaseConnectionError(f"Database is not available: {self._connection_error}")

        query = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = :schema_name
        ORDER BY TABLE_NAME
        """

        try:
            result = self.execute_query(query, {'schema_name': schema_name})
            return [row['TABLE_NAME'] for row in result['rows']]

        except Exception as e:
            logger.error(f"Failed to get database tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection."""
        if not self._engine:
            return False

        try:
            # Use direct engine connection for testing to avoid circular dependency
            connection = self._engine.connect()
            try:
                connection.execute(text("SELECT 1"))
                logger.debug("Database connection test successful")
                return True
            finally:
                connection.close()
        except Exception as e:
            logger.debug(f"Database connection test failed: {e}")
            return False
    
    def list_tables(self, schema_name: str = "dbo") -> List[str]:
        """Get list of tables in the database (alias for get_database_tables)."""
        return self.get_database_tables(schema_name)
    
    def execute_with_details(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute query and return detailed results including affected records for INSERT/UPDATE/DELETE."""
        if not self._is_available:
            return {
                'type': 'error',
                'success': False,
                'error': f'Database is not available: {self._connection_error}',
                'message': f'数据库连接不可用: {self._connection_error}'
            }

        self._validate_sql_query(query)
        
        query_upper = query.strip().upper()
        is_select = query_upper.startswith('SELECT')
        is_insert = query_upper.startswith('INSERT')
        is_update = query_upper.startswith('UPDATE')
        is_delete = query_upper.startswith('DELETE')
        
        if config.security.enable_query_logging:
            if config.security.log_sensitive_data:
                logger.info(f"Executing detailed query: {query} with parameters: {parameters}")
            else:
                logger.info(f"Executing detailed query: {query}")
        
        try:
            with self.get_connection() as conn:
                if is_select:
                    # For SELECT queries, return rows and columns
                    result = conn.execute(text(query), parameters or {})
                    columns = list(result.keys())
                    rows = []
                    for row in result:
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            row_dict[col_name] = row[i]
                        rows.append(row_dict)
                    
                    return {
                        'type': 'select',
                        'success': True,
                        'columns': columns,
                        'rows': rows,
                        'row_count': len(rows),
                        'message': f'查询成功，返回 {len(rows)} 行数据'
                    }
                
                elif is_insert or is_update or is_delete:
                    # For DML queries, get affected records details
                    affected_records = []
                    
                    # Try to get detailed information about affected records
                    if is_update or is_delete:
                        # For UPDATE/DELETE, try to get the records before operation
                        try:
                            # Extract table name from query (basic parsing)
                            table_name = self._extract_table_name(query, is_update, is_delete)
                            if table_name:
                                # Get records that would be affected
                                where_clause = self._extract_where_clause(query)
                                if where_clause:
                                    preview_query = f"SELECT * FROM {table_name} WHERE {where_clause}"
                                    preview_result = conn.execute(text(preview_query), parameters or {})
                                    preview_columns = list(preview_result.keys())
                                    for row in preview_result:
                                        row_dict = {}
                                        for i, col_name in enumerate(preview_columns):
                                            row_dict[col_name] = row[i]
                                        affected_records.append(row_dict)
                        except Exception as preview_error:
                            logger.debug(f"Could not preview affected records: {preview_error}")
                    
                    # Execute the actual query
                    result = conn.execute(text(query), parameters or {})
                    conn.commit()
                    
                    affected_rows = result.rowcount
                    
                    operation_type = 'insert' if is_insert else ('update' if is_update else 'delete')
                    operation_name = {'insert': '插入', 'update': '更新', 'delete': '删除'}[operation_type]
                    
                    response = {
                        'type': operation_type,
                        'success': True,
                        'affected_rows': affected_rows,
                        'message': f'{operation_name}操作成功，影响了 {affected_rows} 行记录'
                    }
                    
                    if affected_records and (is_update or is_delete):
                        response['affected_records'] = affected_records
                        response['message'] += f'，详细记录如下'
                    
                    return response
                
                else:
                    # For other queries (DDL, etc.)
                    result = conn.execute(text(query), parameters or {})
                    conn.commit()
                    
                    return {
                        'type': 'other',
                        'success': True,
                        'message': 'SQL命令执行成功'
                    }
                    
        except Exception as e:
            logger.error(f"Detailed query execution failed: {e}")
            return {
                'type': 'error',
                'success': False,
                'error': str(e),
                'message': f'SQL执行失败: {e}'
            }
    
    def _extract_table_name(self, query: str, is_update: bool, is_delete: bool) -> Optional[str]:
        """Extract table name from UPDATE or DELETE query."""
        try:
            import re
            query_upper = query.upper()
            
            if is_update:
                # UPDATE table_name SET ...
                match = re.search(r'UPDATE\s+(\[?\w+\]?\.?\[?\w+\]?)\s+SET', query_upper)
            elif is_delete:
                # DELETE FROM table_name WHERE ...
                match = re.search(r'DELETE\s+FROM\s+(\[?\w+\]?\.?\[?\w+\]?)', query_upper)
            else:
                return None
            
            if match:
                return match.group(1).strip()
            return None
        except Exception:
            return None
    
    def _extract_where_clause(self, query: str) -> Optional[str]:
        """Extract WHERE clause from query."""
        try:
            import re
            query_upper = query.upper()
            
            # Find WHERE clause
            match = re.search(r'WHERE\s+(.+?)(?:ORDER\s+BY|GROUP\s+BY|$)', query_upper, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None
        except Exception:
            return None
    
    def close(self) -> None:
        """Close database engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            logger.info("Database engine closed")


# Global database manager instance
db_manager = SQLServerManager()
