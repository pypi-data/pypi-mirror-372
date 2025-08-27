"""
Message deduplication utility for preventing duplicate notifications
"""

import hashlib
import time
from typing import Dict


class MessageDeduplicator:
    """Prevent sending duplicate messages across notification channels"""
    
    def __init__(self, window_minutes: int = 5):
        self.window_minutes = window_minutes
        self.recent_messages: Dict[str, float] = {}
    
    def should_send_message(self, message_content: str) -> bool:
        """Check if this message should be sent (not a recent duplicate)"""
        message_hash = hashlib.md5(message_content.encode()).hexdigest()
        now = time.time()
        
        # Clean old entries
        cutoff = now - (self.window_minutes * 60)
        self.recent_messages = {k: v for k, v in self.recent_messages.items() if v > cutoff}
        
        # Check if this message was sent recently
        if message_hash in self.recent_messages:
            return False
        
        # Record this message
        self.recent_messages[message_hash] = now
        return True
    
    def force_allow_message(self, message_content: str):
        """Force allow a message even if it would be considered duplicate"""
        message_hash = hashlib.md5(message_content.encode()).hexdigest()
        now = time.time()
        self.recent_messages[message_hash] = now
    
    def get_stats(self) -> dict:
        """Get deduplication statistics"""
        now = time.time()
        cutoff = now - (self.window_minutes * 60)
        
        # Clean old entries
        self.recent_messages = {k: v for k, v in self.recent_messages.items() if v > cutoff}
        
        return {
            "recent_messages_count": len(self.recent_messages),
            "window_minutes": self.window_minutes,
            "oldest_message_age_seconds": min([now - v for v in self.recent_messages.values()]) if self.recent_messages else 0
        }
    
    def reset(self):
        """Reset deduplication cache"""
        self.recent_messages.clear()