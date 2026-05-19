from typing import Dict, Optional
import time
from src.core.database import Database

class RateLimiter:
    """Rate limiter per user using token bucket algorithm."""
    
    def __init__(self, database: Database, max_tokens: int = 10, refill_rate: float = 1.0):
        """
        Initialize rate limiter.
        
        Args:
            database: Database instance for persistence
            max_tokens: Maximum tokens per user
            refill_rate: Tokens per second refill rate
        """
        self.database = database
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self._buckets: Dict[str, Dict[str, float]] = {}
    
    def _get_bucket(self, user_id: str) -> Dict[str, float]:
        """Get or create token bucket for user."""
        if user_id not in self._buckets:
            self._buckets[user_id] = {
                'tokens': float(self.max_tokens),
                'last_refill': time.time()
            }
        return self._buckets[user_id]
    
    def _refill_tokens(self, bucket: Dict[str, float]) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - bucket['last_refill']
        tokens_to_add = elapsed * self.refill_rate
        bucket['tokens'] = min(self.max_tokens, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
    
    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user is rate limited.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            True if request is allowed, False if rate limited
        """
        try:
            bucket = self._get_bucket(user_id)
            self._refill_tokens(bucket)
            
            if bucket['tokens'] >= 1.0:
                bucket['tokens'] -= 1.0
                return True
            return False
            
        except Exception as e:
            raise RuntimeError(f"Rate limit check failed: {e}") from e
    
    def get_remaining_tokens(self, user_id: str) -> float:
        """
        Get remaining tokens for user.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Number of remaining tokens
        """
        try:
            bucket = self._get_bucket(user_id)
            self._refill_tokens(bucket)
            return bucket['tokens']
            
        except Exception as e:
            raise RuntimeError(f"Failed to get remaining tokens: {e}") from e
    
    def get_wait_time(self, user_id: str) -> float:
        """
        Get estimated wait time until next token is available.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Wait time in seconds
        """
        try:
            bucket = self._get_bucket(user_id)
            self._refill_tokens(bucket)
            
            if bucket['tokens'] >= 1.0:
                return 0.0
            
            tokens_needed = 1.0 - bucket['tokens']
            return tokens_needed / self.refill_rate
            
        except Exception as e:
            raise RuntimeError(f"Failed to calculate wait time: {e}") from e
    
    def reset_user(self, user_id: str) -> None:
        """
        Reset rate limit for a specific user.
        
        Args:
            user_id: Unique user identifier
        """
        try:
            if user_id in self._buckets:
                del self._buckets[user_id]
        except Exception as e:
            raise RuntimeError(f"Failed to reset user rate limit: {e}") from e
    
    def reset_all(self) -> None:
        """Reset rate limits for all users."""
        try:
            self._buckets.clear()
        except Exception as e:
            raise RuntimeError(f"Failed to reset all rate limits: {e}") from e