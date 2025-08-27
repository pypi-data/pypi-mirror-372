"""
Base channel abstract class for notification channels
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from datetime import datetime

from ..formatters.base import BaseFormatter, MessageData
from ..utils import RateLimiter, MessageDeduplicator


class ChannelResult:
    """Result of a channel send operation"""
    
    def __init__(self, success: bool, message: str = "", data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()
    
    def __bool__(self):
        return self.success
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class BaseChannel(ABC):
    """Abstract base class for notification channels"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", True)
        
        # Initialize rate limiter
        rate_config = config.get("rate_limiting", {})
        self.rate_limiter = RateLimiter(
            max_per_minute=rate_config.get("max_messages_per_minute", 20),
            max_per_hour=rate_config.get("max_messages_per_hour", 100)
        )
        
        # Initialize deduplicator
        self.deduplicator = MessageDeduplicator(
            window_minutes=config.get("deduplication_window_minutes", 5)
        )
        
        # Retry configuration
        retry_config = config.get("retry_config", {})
        self.max_retries = retry_config.get("max_retries", 3)
        self.base_delay = retry_config.get("base_delay", 1)
        self.max_delay = retry_config.get("max_delay", 30)
        self.exponential_base = retry_config.get("exponential_base", 2)
        
        # Initialize formatter
        self.formatter = self._create_formatter()
    
    @abstractmethod
    def _create_formatter(self) -> BaseFormatter:
        """Create the appropriate formatter for this channel"""
        pass
    
    @abstractmethod
    def _send_message_impl(self, formatted_message: str, data: MessageData) -> ChannelResult:
        """Implementation-specific message sending logic"""
        pass
    
    @abstractmethod
    def _send_file_impl(self, file_content: str, filename: str, data: MessageData) -> ChannelResult:
        """Implementation-specific file sending logic"""
        pass
    
    @abstractmethod
    def health_check(self) -> ChannelResult:
        """Check if the channel is healthy and can send messages"""
        pass
    
    def send_message(self, data: MessageData, force: bool = False) -> ChannelResult:
        """Send a message through this channel"""
        if not self.enabled:
            return ChannelResult(False, f"Channel {self.name} is disabled")
        
        # Check rate limiting unless forced
        if not force and not self.rate_limiter.can_send_message():
            return ChannelResult(False, f"Rate limited for channel {self.name}")
        
        # Format the message
        try:
            if data.exception:
                formatted_message = self.formatter.format_exception(data)
            else:
                formatted_message = self.formatter.format_message(data)
        except Exception as e:
            return ChannelResult(False, f"Failed to format message: {e}")
        
        # Check for duplicates unless forced
        if not force and not self.deduplicator.should_send_message(formatted_message):
            return ChannelResult(False, f"Duplicate message blocked for channel {self.name}")
        
        # Send with retry
        result = self._send_with_retry(self._send_message_impl, formatted_message, data)
        
        if result.success:
            self.rate_limiter.record_message()
        
        return result
    
    def send_file(self, data: MessageData, force: bool = False) -> ChannelResult:
        """Send a file attachment through this channel"""
        if not self.enabled:
            return ChannelResult(False, f"Channel {self.name} is disabled")
        
        # Check rate limiting unless forced
        if not force and not self.rate_limiter.can_send_message():
            return ChannelResult(False, f"Rate limited for channel {self.name}")
        
        # Generate file content and name
        try:
            if hasattr(self.formatter, 'format_exception_file'):
                file_content = self.formatter.format_exception_file(data)
            else:
                file_content = self.formatter.format_exception(data)
            
            timestamp = data.timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{data.app_name.lower().replace(' ', '_')}_{data.level.lower()}_{timestamp}.txt"
        except Exception as e:
            return ChannelResult(False, f"Failed to generate file content: {e}")
        
        # Check for duplicates unless forced
        if not force and not self.deduplicator.should_send_message(file_content):
            return ChannelResult(False, f"Duplicate file blocked for channel {self.name}")
        
        # Send with retry
        result = self._send_with_retry(self._send_file_impl, file_content, filename, data)
        
        if result.success:
            self.rate_limiter.record_message()
        
        return result
    
    def _send_with_retry(self, send_func, *args, **kwargs) -> ChannelResult:
        """Send with exponential backoff retry"""
        last_result = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = send_func(*args, **kwargs)
                if result.success:
                    return result
                last_result = result
                
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    time.sleep(delay)
                
            except Exception as e:
                last_result = ChannelResult(False, f"Exception during send: {e}")
                
                if attempt < self.max_retries:
                    delay = min(
                        self.base_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    time.sleep(delay)
        
        return last_result or ChannelResult(False, "All retry attempts failed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get channel statistics"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "rate_limiter": self.rate_limiter.get_stats(),
            "deduplicator": self.deduplicator.get_stats(),
            "config": {
                "max_retries": self.max_retries,
                "base_delay": self.base_delay,
                "max_delay": self.max_delay
            }
        }
    
    def reset_limits(self):
        """Reset rate limiting and deduplication"""
        self.rate_limiter.reset()
        self.deduplicator.reset()
    
    def should_send_as_file(self, data: MessageData) -> bool:
        """Determine if message should be sent as file based on configuration"""
        severity_config = self.config.get("severity_config", {})
        level_config = severity_config.get(data.level, {})
        
        # Check if this severity level should always be sent as file
        if level_config.get("send_as_file", False):
            return True
        
        # Check if exceptions should be sent as files
        if data.exception and self.config.get("send_exceptions_as_files", True):
            return True
        
        # Check message length
        max_message_length = self.config.get("max_message_length", 4000)
        formatted_message = self.formatter.format_exception(data) if data.exception else self.formatter.format_message(data)
        
        return len(formatted_message) > max_message_length