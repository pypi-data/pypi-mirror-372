"""
Base formatter classes for message formatting across different channels
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime


class MessageData:
    """Standard message data structure passed to formatters"""
    
    def __init__(self, 
                 level: str,
                 message: str, 
                 timestamp: datetime,
                 app_name: str,
                 app_version: str,
                 environment: str,
                 exception: Optional[Exception] = None,
                 context: Optional[Dict[str, Any]] = None,
                 source_location: Optional[Dict[str, str]] = None):
        self.level = level
        self.message = message
        self.timestamp = timestamp
        self.app_name = app_name
        self.app_version = app_version
        self.environment = environment
        self.exception = exception
        self.context = context or {}
        self.source_location = source_location or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message data to dictionary"""
        return {
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "exception": str(self.exception) if self.exception else None,
            "context": self.context,
            "source_location": self.source_location
        }


class BaseFormatter(ABC):
    """Abstract base class for message formatters"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    @abstractmethod
    def format_message(self, data: MessageData) -> str:
        """Format a message for the target channel"""
        pass
    
    @abstractmethod
    def format_exception(self, data: MessageData) -> str:
        """Format an exception message for the target channel"""
        pass
    
    def get_severity_emoji(self, level: str) -> str:
        """Get emoji for severity level"""
        severity_emojis = self.config.get("severity_emoji", {
            "CRITICAL": "🚨",
            "ERROR": "❌", 
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "DEBUG": "🔍"
        })
        return severity_emojis.get(level, "📝")
    
    def get_environment_emoji(self, environment: str) -> str:
        """Get emoji for environment"""
        env_emojis = self.config.get("environment_emoji", {
            "production": "🏭",
            "staging": "🧪",
            "development": "🛠️", 
            "local": "💻"
        })
        return env_emojis.get(environment.lower(), "🔧")
    
    def should_include_context(self, data: MessageData) -> bool:
        """Determine if context should be included in message"""
        max_context_size = self.config.get("max_context_size", 5000)
        if not data.context:
            return False
        
        context_str = str(data.context)
        return len(context_str) <= max_context_size
    
    def truncate_if_needed(self, text: str, max_length: int) -> str:
        """Truncate text if it exceeds max length"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length - 3] + "..."
        return truncated