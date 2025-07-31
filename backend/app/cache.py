import redis
import json
import pickle
from flask import current_app
from typing import Any, Optional, Union



class RedisCache:
    
    def __init__(self, app=None):
        self.redis_client = None
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/1')
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            raise Exception(f"Redis connection failed: {e}")
    
    def _serialize(self, value: Any) -> bytes:
        try:
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            return pickle.dumps(value)
    
    def _deserialize(self, value: bytes) -> Any:
        try:
            # Try JSON first
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(value)
    
    def _make_key(self, key: str) -> str:
        prefix = current_app.config.get('CACHE_KEY_PREFIX', 'quizzo:')
        return f"{prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._make_key(key)
            value = self.redis_client.get(cache_key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception as e:
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            serialized_value = self._serialize(value)
            
            if timeout is None:
                timeout = current_app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            
            return self.redis_client.setex(cache_key, timeout, serialized_value)
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            return bool(self.redis_client.delete(cache_key))
        except Exception as e:
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        if not self.redis_client:
            return 0
        
        try:
            cache_pattern = self._make_key(pattern)
            keys = self.redis_client.keys(cache_pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            return 0
    
    def clear_user_cache(self, user_id: int) -> int:
        return self.delete_pattern(f"user_{user_id}_*")
    
    def clear_quiz_cache(self, quiz_id: int) -> int:
        return self.delete_pattern(f"quiz_{quiz_id}_*")
    
    def clear_admin_cache(self) -> int:
        deleted = 0
        deleted += self.delete_pattern("admin_*")
        deleted += self.delete_pattern("course_*")
        deleted += self.delete_pattern("chapter_*")
        return deleted
    
    def get_cache_stats(self) -> dict:
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get('used_memory_human', 'Unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "uptime_in_seconds": info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


def cache_result(key_func=None, timeout=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = current_app.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            current_app.cache.set(cache_key, result, timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_user_cache(user_id: int):
    if hasattr(current_app, 'cache'):
        current_app.cache.clear_user_cache(user_id)


def invalidate_quiz_cache(quiz_id: int, chapter_id: int = None):
    if hasattr(current_app, 'cache'):
        current_app.cache.clear_quiz_cache(quiz_id)
        if chapter_id:
            current_app.cache.delete(f'chapter_{chapter_id}_quizzes')
        # Clear related caches
        current_app.cache.delete('upcoming_quizzes')
        current_app.cache.delete('open_quizzes')
