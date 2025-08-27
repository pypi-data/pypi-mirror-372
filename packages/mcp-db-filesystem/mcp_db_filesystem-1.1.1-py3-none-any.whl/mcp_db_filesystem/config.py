"""Configuration management for MCP SQL Server Filesystem server."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from . import __version__

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseModel):
    """SQL Server database configuration."""

    server: str = Field(..., description="SQL Server hostname or IP address")
    database: str = Field(..., description="Database name")
    username: Optional[str] = Field(None, description="Username for SQL Server authentication")
    password: Optional[str] = Field(None, description="Password for SQL Server authentication")
    use_windows_auth: bool = Field(True, description="Use Windows Authentication")
    port: int = Field(1433, description="SQL Server port")
    driver: str = Field("ODBC Driver 17 for SQL Server", description="ODBC driver name")
    connection_timeout: int = Field(30, description="Connection timeout in seconds")
    command_timeout: int = Field(30, description="Command timeout in seconds")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum overflow connections")

    # 新增的连接参数
    trust_server_certificate: bool = Field(True, description="Trust server certificate (TrustServerCertificate)")
    encrypt: bool = Field(False, description="Enable encryption (Encrypt)")
    multiple_active_result_sets: bool = Field(True, description="Enable multiple active result sets (MultipleActiveResultSets)")
    application_name: str = Field("MCP-Db-Filesystem", description="Application name for connection tracking")
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    @property
    def connection_string(self) -> str:
        """Generate SQL Server connection string with enhanced parameters."""
        # 基础连接参数
        base_params = [
            f"DRIVER={{{self.driver}}}",
            f"SERVER={self.server},{self.port}",
            f"DATABASE={self.database}",
            f"Connection Timeout={self.connection_timeout}",
        ]

        # 认证参数
        if self.use_windows_auth:
            base_params.append("Trusted_Connection=yes")
        else:
            base_params.extend([
                f"UID={self.username}",
                f"PWD={self.password}",
            ])

        # 增强的连接参数
        enhanced_params = [
            f"TrustServerCertificate={'yes' if self.trust_server_certificate else 'no'}",
            f"Encrypt={'yes' if self.encrypt else 'no'}",
            f"MultipleActiveResultSets={'yes' if self.multiple_active_result_sets else 'no'}",
            f"Application Name={self.application_name}",
        ]

        # 合并所有参数
        all_params = base_params + enhanced_params
        return ";".join(all_params) + ";"


class MySQLConfig(BaseModel):
    """MySQL database configuration."""

    host: str = Field("", description="MySQL server hostname or IP address")
    port: int = Field(3306, description="MySQL server port")
    database: str = Field("", description="Database name")
    username: Optional[str] = Field(None, description="Username for MySQL authentication")
    password: Optional[str] = Field(None, description="Password for MySQL authentication")
    charset: str = Field("utf8mb4", description="Character set")
    connection_timeout: int = Field(30, description="Connection timeout in seconds")
    pool_size: int = Field(5, description="Connection pool size")
    max_overflow: int = Field(10, description="Maximum overflow connections")

    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v


class RedisConfig(BaseModel):
    """Redis configuration."""

    host: str = Field("", description="Redis server hostname or IP address")
    port: int = Field(6379, description="Redis server port")
    db: int = Field(0, description="Redis database number")
    password: Optional[str] = Field(None, description="Redis password")
    socket_timeout: int = Field(30, description="Socket timeout in seconds")
    connection_timeout: int = Field(30, description="Connection timeout in seconds")
    max_connections: int = Field(10, description="Maximum connections in pool")

    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

    @validator('db')
    def validate_db(cls, v):
        if not 0 <= v <= 15:
            raise ValueError('Redis database number must be between 0 and 15')
        return v


class FilesystemConfig(BaseModel):
    """Filesystem access configuration."""

    allowed_paths: List[str] = Field(default_factory=list, description="List of allowed base paths (empty or ['*'] = allow all)")
    max_file_size: int = Field(1024 * 1024 * 1024, description="Maximum file size in bytes (1GB)")
    allowed_extensions: Set[str] = Field(default_factory=set, description="Allowed file extensions (empty or '*.*' = allow all)")
    enable_write: bool = Field(True, description="Enable write operations")
    enable_delete: bool = Field(True, description="Enable delete operations")
    ignore_file_locks: bool = Field(True, description="Ignore file locks when reading/writing files")
    
    @property
    def is_full_access_mode(self) -> bool:
        """Check if filesystem is in full access mode (no path restrictions)."""
        return not self.allowed_paths or '*' in self.allowed_paths or 'all' in [p.lower() for p in self.allowed_paths]
    
    @validator('allowed_paths')
    def validate_paths(cls, v):
        """Validate and normalize paths."""
        if not v:
            return v
            
        normalized_paths = []
        for path in v:
            path = path.strip()
            if not path:
                continue
                
            # Handle wildcards
            if path in ['*', 'all', 'ALL']:
                normalized_paths.append('*')
                continue
                
            try:
                # Only resolve real paths, not wildcards
                normalized_path = str(Path(path).resolve())
                normalized_paths.append(normalized_path)
            except Exception as e:
                raise ValueError(f"Invalid path '{path}': {e}")
        return normalized_paths
    
    @validator('max_file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('Max file size must be positive')
        return v


class SecurityConfig(BaseModel):
    """Security configuration."""

    enable_sql_injection_protection: bool = Field(False, description="Enable SQL injection protection (disabled for full access)")
    allowed_sql_keywords: Set[str] = Field(
        default_factory=set,
        description="Allowed SQL keywords (empty = allow all)"
    )
    blocked_sql_keywords: Set[str] = Field(
        default_factory=set,
        description="Blocked SQL keywords (empty = allow all)"
    )
    max_query_length: int = Field(100000, description="Maximum SQL query length (increased for complex queries)")
    enable_query_logging: bool = Field(True, description="Enable query logging")
    log_sensitive_data: bool = Field(True, description="Log sensitive data for debugging (enabled for full access)")


class ServerConfig(BaseModel):
    """MCP server configuration."""
    
    name: str = Field("mcp-db-filesystem", description="Server name")
    version: str = Field(__version__, description="Server version")
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.upper()


class Config(BaseModel):
    """Main configuration class."""

    database: DatabaseConfig
    mysql: MySQLConfig = Field(default_factory=MySQLConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    filesystem: FilesystemConfig = Field(default_factory=FilesystemConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables."""
        # SQL Server configuration
        db_config = DatabaseConfig(
            server=os.getenv('MSSQL_SERVER', 'localhost'),
            database=os.getenv('MSSQL_DATABASE', 'master'),
            username=os.getenv('MSSQL_USERNAME'),
            password=os.getenv('MSSQL_PASSWORD'),
            use_windows_auth=os.getenv('MSSQL_USE_WINDOWS_AUTH', 'true').lower() == 'true',
            port=int(os.getenv('MSSQL_PORT', '1433')),
            driver=os.getenv('MSSQL_DRIVER', 'ODBC Driver 17 for SQL Server'),
            connection_timeout=int(os.getenv('MSSQL_CONNECTION_TIMEOUT', '30')),
            command_timeout=int(os.getenv('MSSQL_COMMAND_TIMEOUT', '30')),
            pool_size=int(os.getenv('MSSQL_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('MSSQL_MAX_OVERFLOW', '10')),

            # 新增的连接参数
            trust_server_certificate=os.getenv('MSSQL_TRUST_SERVER_CERTIFICATE', 'true').lower() == 'true',
            encrypt=os.getenv('MSSQL_ENCRYPT', 'false').lower() == 'true',
            multiple_active_result_sets=os.getenv('MSSQL_MULTIPLE_ACTIVE_RESULT_SETS', 'true').lower() == 'true',
            application_name=os.getenv('MSSQL_APPLICATION_NAME', 'MCP-Db-Filesystem'),
        )

        # MySQL configuration
        mysql_config = MySQLConfig(
            host=os.getenv('MYSQL_HOST', ''),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            database=os.getenv('MYSQL_DATABASE', ''),
            username=os.getenv('MYSQL_USERNAME'),
            password=os.getenv('MYSQL_PASSWORD'),
            charset=os.getenv('MYSQL_CHARSET', 'utf8mb4'),
            connection_timeout=int(os.getenv('MYSQL_CONNECTION_TIMEOUT', '30')),
            pool_size=int(os.getenv('MYSQL_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('MYSQL_MAX_OVERFLOW', '10')),
        )

        # Redis configuration
        redis_config = RedisConfig(
            host=os.getenv('REDIS_HOST', ''),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            password=os.getenv('REDIS_PASSWORD'),
            socket_timeout=int(os.getenv('REDIS_SOCKET_TIMEOUT', '30')),
            connection_timeout=int(os.getenv('REDIS_CONNECTION_TIMEOUT', '30')),
            max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', '10')),
        )

        # Filesystem configuration
        allowed_paths = os.getenv('FS_ALLOWED_PATHS', '').split(',') if os.getenv('FS_ALLOWED_PATHS') else []
        allowed_extensions = set(os.getenv('FS_ALLOWED_EXTENSIONS', '').split(',')) if os.getenv('FS_ALLOWED_EXTENSIONS') else set()
        
        fs_config = FilesystemConfig(
            allowed_paths=[p.strip() for p in allowed_paths if p.strip()],
            max_file_size=int(os.getenv('FS_MAX_FILE_SIZE', str(1024 * 1024 * 1024))),  # 1GB default
            allowed_extensions=allowed_extensions,
            enable_write=os.getenv('FS_ENABLE_WRITE', 'true').lower() == 'true',
            enable_delete=os.getenv('FS_ENABLE_DELETE', 'true').lower() == 'true',
            ignore_file_locks=os.getenv('FS_IGNORE_FILE_LOCKS', 'true').lower() == 'true',
        )
        
        # Security configuration - defaults to full access
        security_config = SecurityConfig(
            enable_sql_injection_protection=os.getenv('SEC_ENABLE_SQL_PROTECTION', 'false').lower() == 'true',
            max_query_length=int(os.getenv('SEC_MAX_QUERY_LENGTH', '100000')),
            enable_query_logging=os.getenv('SEC_ENABLE_QUERY_LOGGING', 'true').lower() == 'true',
            log_sensitive_data=os.getenv('SEC_LOG_SENSITIVE_DATA', 'true').lower() == 'true',
        )
        
        # Server configuration
        server_config = ServerConfig(
            debug=os.getenv('SERVER_DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('SERVER_LOG_LEVEL', 'INFO'),
            log_file=os.getenv('SERVER_LOG_FILE'),
        )
        
        return cls(
            database=db_config,
            mysql=mysql_config,
            redis=redis_config,
            filesystem=fs_config,
            security=security_config,
            server=server_config,
        )


# Global configuration instance - can be reloaded
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the current configuration instance, creating if necessary."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.from_env()
    return _config_instance


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global _config_instance
    _config_instance = Config.from_env()
    return _config_instance


# For backward compatibility
config = get_config()
