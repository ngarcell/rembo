"""
Redis client configuration for caching and OTP storage
"""

import redis
import json
import logging
from typing import Optional, Any
from .config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper for sync operations"""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._client: Optional[redis.Redis] = None

    def connect(self):
        """Connect to Redis"""
        if not self._client:
            self._client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
        return self._client

    def close(self):
        """Close Redis connection"""
        if self._client:
            try:
                self._client.close()
            except Exception as e:
                # Log the exception but don't raise it during cleanup
                print(f"Warning: Error closing Redis connection: {e}")
            self._client = None

    def ping(self) -> bool:
        """Test Redis connection"""
        client = self.connect()
        try:
            client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        client = self.connect()
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)

            result = client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        client = self.connect()
        try:
            value = client.get(key)
            if value:
                try:
                    # Try to parse as JSON
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Return as string if not JSON
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key"""
        client = self.connect()
        try:
            result = client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        client = self.connect()
        try:
            result = client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a key"""
        client = self.connect()
        try:
            result = client.incr(key, amount)
            return result
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return None

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        client = self.connect()
        try:
            result = client.expire(key, seconds)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False


# Create global Redis client instance
redis_client = RedisClient()
