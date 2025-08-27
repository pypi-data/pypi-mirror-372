"""Redis operations for MCP server."""

import logging
import json
from typing import Any, Dict, List, Optional, Union
import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from .config import config

logger = logging.getLogger(__name__)


class RedisConnectionError(Exception):
    """Raised when Redis connection fails."""
    pass


class RedisManager:
    """Manages Redis connections and operations."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._is_available: bool = False
        self._connection_error: Optional[str] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Redis client."""
        try:
            # Check if Redis configuration is provided
            if not hasattr(config, 'redis') or not config.redis.host:
                self._is_available = False
                self._connection_error = "Redis configuration not provided"
                logger.info("Redis configuration not found - Redis features will be unavailable")
                return
            
            # Create Redis client
            self._client = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                db=config.redis.db,
                password=config.redis.password if config.redis.password else None,
                socket_timeout=config.redis.socket_timeout,
                socket_connect_timeout=config.redis.connection_timeout,
                decode_responses=True,  # Automatically decode responses to strings
                max_connections=config.redis.max_connections,
            )
            
            # Test the connection to ensure it's working
            if self.test_connection():
                self._is_available = True
                self._connection_error = None
                logger.info("Redis client initialized and connection test successful")
            else:
                self._is_available = False
                self._connection_error = "Connection test failed"
                logger.warning("Redis client initialized but connection test failed")
            
        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.warning(f"Failed to initialize Redis client: {e} - Redis features will be unavailable")
            # Don't raise exception, just mark as unavailable
    
    def is_available(self) -> bool:
        """Check if Redis is available for operations."""
        return self._is_available
    
    def get_connection_error(self) -> Optional[str]:
        """Get the last connection error message."""
        return self._connection_error
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to Redis."""
        logger.info("Attempting to reconnect to Redis...")
        self._initialize_client()
        return self._is_available
    
    def test_connection(self) -> bool:
        """Test Redis connection."""
        if not self._client:
            return False
            
        try:
            self._client.ping()
            logger.debug("Redis connection test successful")
            return True
        except Exception as e:
            logger.debug(f"Redis connection test failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.get(key)
            logger.debug(f"Redis GET {key}: {'found' if result else 'not found'}")
            return result
        except Exception as e:
            logger.error(f"Redis GET operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis GET failed: {e}")
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set key-value pair with optional expiration."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.set(key, value, ex=ex)
            logger.debug(f"Redis SET {key}: {'success' if result else 'failed'}")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis SET failed: {e}")
    
    def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.delete(*keys)
            logger.debug(f"Redis DELETE {keys}: {result} keys deleted")
            return result
        except Exception as e:
            logger.error(f"Redis DELETE operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis DELETE failed: {e}")
    
    def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.exists(*keys)
            logger.debug(f"Redis EXISTS {keys}: {result} keys exist")
            return result
        except Exception as e:
            logger.error(f"Redis EXISTS operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis EXISTS failed: {e}")
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.keys(pattern)
            logger.debug(f"Redis KEYS {pattern}: {len(result)} keys found")
            return result
        except Exception as e:
            logger.error(f"Redis KEYS operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis KEYS failed: {e}")
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.hget(name, key)
            logger.debug(f"Redis HGET {name} {key}: {'found' if result else 'not found'}")
            return result
        except Exception as e:
            logger.error(f"Redis HGET operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis HGET failed: {e}")
    
    def hset(self, name: str, key: str, value: str) -> int:
        """Set hash field value."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.hset(name, key, value)
            logger.debug(f"Redis HSET {name} {key}: {result}")
            return result
        except Exception as e:
            logger.error(f"Redis HSET operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis HSET failed: {e}")
    
    def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields and values."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.hgetall(name)
            logger.debug(f"Redis HGETALL {name}: {len(result)} fields")
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis HGETALL failed: {e}")
    
    def lpush(self, name: str, *values: str) -> int:
        """Push values to the left of a list."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.lpush(name, *values)
            logger.debug(f"Redis LPUSH {name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Redis LPUSH operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis LPUSH failed: {e}")
    
    def rpop(self, name: str) -> Optional[str]:
        """Pop value from the right of a list."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.rpop(name)
            logger.debug(f"Redis RPOP {name}: {'found' if result else 'empty'}")
            return result
        except Exception as e:
            logger.error(f"Redis RPOP operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis RPOP failed: {e}")
    
    def lrange(self, name: str, start: int = 0, end: int = -1) -> List[str]:
        """Get list elements in range."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.lrange(name, start, end)
            logger.debug(f"Redis LRANGE {name} {start} {end}: {len(result)} items")
            return result
        except Exception as e:
            logger.error(f"Redis LRANGE operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis LRANGE failed: {e}")
    
    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get Redis server information."""
        if not self._is_available:
            raise RedisConnectionError(f"Redis is not available: {self._connection_error}")
        
        try:
            result = self._client.info(section)
            logger.debug(f"Redis INFO {section or 'all'}: retrieved")
            return result
        except Exception as e:
            logger.error(f"Redis INFO operation failed: {e}")
            # Mark as unavailable if connection fails
            self._is_available = False
            self._connection_error = str(e)
            raise RedisConnectionError(f"Redis INFO failed: {e}")
    
    def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
            finally:
                self._client = None


# Global Redis manager instance
redis_manager = RedisManager()
