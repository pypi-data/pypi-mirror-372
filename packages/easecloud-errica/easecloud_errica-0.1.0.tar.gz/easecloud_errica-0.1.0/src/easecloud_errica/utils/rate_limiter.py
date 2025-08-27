"""
Rate limiting utility for preventing message spam across notification channels
"""

import time
from typing import List


class RateLimiter:
    """Rate limiter to prevent API spam across different notification channels"""
    
    def __init__(self, max_per_minute: int = 20, max_per_hour: int = 100):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.minute_messages: List[float] = []
        self.hour_messages: List[float] = []
    
    def can_send_message(self) -> bool:
        """Check if we can send a message based on rate limits"""
        now = time.time()
        
        # Clean old entries
        self.minute_messages = [t for t in self.minute_messages if now - t < 60]
        self.hour_messages = [t for t in self.hour_messages if now - t < 3600]
        
        # Check limits
        if len(self.minute_messages) >= self.max_per_minute:
            return False
        if len(self.hour_messages) >= self.max_per_hour:
            return False
        
        return True
    
    def record_message(self):
        """Record that a message was sent"""
        now = time.time()
        self.minute_messages.append(now)
        self.hour_messages.append(now)
    
    def get_stats(self) -> dict:
        """Get current rate limiting statistics"""
        now = time.time()
        
        # Clean old entries
        self.minute_messages = [t for t in self.minute_messages if now - t < 60]
        self.hour_messages = [t for t in self.hour_messages if now - t < 3600]
        
        return {
            "messages_last_minute": len(self.minute_messages),
            "messages_last_hour": len(self.hour_messages),
            "max_per_minute": self.max_per_minute,
            "max_per_hour": self.max_per_hour,
            "can_send": self.can_send_message()
        }
    
    def reset(self):
        """Reset rate limiting counters"""
        self.minute_messages.clear()
        self.hour_messages.clear()