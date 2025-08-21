"""
Redis client utilities for service communication
"""
import redis
import json
import logging
from typing import Any, Dict, Optional
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from .retry_utils import retry_with_backoff, REDIS_RETRY_CONFIG, circuit_breaker

logger = logging.getLogger(__name__)

class RedisClient:
    """Shared Redis client for all services"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
            retry_on_timeout=True
        )
        
    @retry_with_backoff(REDIS_RETRY_CONFIG)
    def publish(self, channel: str, message: Any) -> bool:
        """Publish message to a channel with retry logic"""
        try:
            # Handle both string and dict/object messages
            if isinstance(message, str):
                # Already a string, publish as-is
                self.client.publish(channel, message)
            else:
                # Serialize dict/object to JSON
                serialized = json.dumps(message)
                self.client.publish(channel, serialized)
            logger.debug(f"Published to {channel}: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            raise  # Re-raise for retry decorator
    
    def pubsub(self) -> redis.client.PubSub:
        """Get a pubsub instance"""
        return self.client.pubsub()
            
    def subscribe(self, channels: list) -> redis.client.PubSub:
        """Subscribe to channels"""
        pubsub = self.client.pubsub()
        pubsub.subscribe(channels)
        return pubsub
    
    @retry_with_backoff(REDIS_RETRY_CONFIG)
    def set(self, key: str, value: Any, ex: int = None) -> bool:
        """Set a key-value pair with optional expiry"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.client.set(key, value, ex=ex)
            return True
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            raise  # Re-raise for retry decorator
    
    @retry_with_backoff(REDIS_RETRY_CONFIG)
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            raise  # Re-raise for retry decorator
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False
        
    def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached value with TTL"""
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")
            return False
            
    def get_cache(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to get cache {key}: {e}")
            return None
            
    @retry_with_backoff(REDIS_RETRY_CONFIG)
    def health_check(self) -> bool:
        """Check Redis connection with retry logic"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            raise  # Re-raise for retry decorator

# Global instance
redis_client = RedisClient()