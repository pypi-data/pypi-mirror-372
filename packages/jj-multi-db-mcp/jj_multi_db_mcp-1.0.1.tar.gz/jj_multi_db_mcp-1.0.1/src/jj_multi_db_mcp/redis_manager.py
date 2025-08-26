"""Redis database manager."""

import os
import logging
from typing import List, Any, Optional, Union

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RedisManager:
    """Redis database manager."""
    
    def __init__(self):
        """Initialize Redis manager."""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis dependencies not installed. Install with: pip install jj-multi-db-mcp[redis]")
        
        self._client = None
        self._is_available = False
        self._connection_error = None
        
        # Get configuration from environment variables
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.decode_responses = os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true"
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Redis connection."""
        try:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self._client.ping()
            
            self._is_available = True
            self._connection_error = None
            logger.info(f"Redis connected successfully: {self.host}:{self.port}/{self.db}")
            
        except Exception as e:
            self._is_available = False
            self._connection_error = str(e)
            logger.error(f"Redis connection failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        return self._is_available
    
    def get_connection_error(self) -> Optional[str]:
        """Get connection error message."""
        return self._connection_error
    
    def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            raise
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            raise
    
    def delete(self, key: str) -> int:
        """Delete key from Redis."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            raise
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            raise
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return bool(self._client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            raise
    
    def ttl(self, key: str) -> int:
        """Get time to live for key."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error: {e}")
            raise
    
    def info(self) -> dict:
        """Get Redis server information."""
        if not self._is_available:
            raise Exception(f"Redis is not available: {self._connection_error}")
        
        try:
            return self._client.info()
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            raise
