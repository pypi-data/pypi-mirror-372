"""
JSON formatter for webhook and API-based channels
"""

import json
import traceback
from typing import Dict, Any, Optional
from .base import BaseFormatter, MessageData


class JsonFormatter(BaseFormatter):
    """JSON formatter for webhook and API channels"""
    
    def format_message(self, data: MessageData) -> str:
        """Format a message as JSON"""
        payload = {
            "timestamp": data.timestamp.isoformat(),
            "level": data.level,
            "app": {
                "name": data.app_name,
                "version": data.app_version,
                "environment": data.environment
            },
            "message": data.message,
            "type": "log"
        }
        
        # Add source location if available
        if data.source_location:
            payload["source"] = data.source_location
        
        # Add context if available
        if data.context:
            payload["context"] = data.context
        
        return json.dumps(payload, indent=2 if self.config.get("pretty_print", False) else None)
    
    def format_exception(self, data: MessageData) -> str:
        """Format an exception as JSON"""
        payload = {
            "timestamp": data.timestamp.isoformat(),
            "level": data.level,
            "app": {
                "name": data.app_name,
                "version": data.app_version,
                "environment": data.environment
            },
            "message": data.message,
            "type": "exception"
        }
        
        # Add exception details
        if data.exception:
            payload["exception"] = {
                "type": type(data.exception).__name__,
                "message": str(data.exception),
                "traceback": self._get_traceback(data.exception) if hasattr(data.exception, '__traceback__') else None
            }
        
        # Add source location if available
        if data.source_location:
            payload["source"] = data.source_location
        
        # Add context if available
        if data.context:
            payload["context"] = data.context
        
        return json.dumps(payload, indent=2 if self.config.get("pretty_print", False) else None)
    
    def _get_traceback(self, exception: Exception) -> Optional[list]:
        """Extract traceback as list of strings"""
        if not hasattr(exception, '__traceback__') or not exception.__traceback__:
            return None
        
        try:
            tb_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
            return [line.rstrip() for line in tb_lines]
        except Exception:
            return None
    
    def format_structured(self, data: MessageData, additional_fields: Optional[Dict[str, Any]] = None) -> str:
        """Format with additional structured fields for advanced webhooks"""
        base_payload = json.loads(self.format_exception(data) if data.exception else self.format_message(data))
        
        if additional_fields:
            base_payload.update(additional_fields)
        
        # Add severity indicators
        base_payload["severity"] = {
            "level": data.level,
            "numeric": self._get_numeric_severity(data.level),
            "color": self._get_severity_color(data.level)
        }
        
        return json.dumps(base_payload, indent=2 if self.config.get("pretty_print", False) else None)
    
    def _get_numeric_severity(self, level: str) -> int:
        """Convert log level to numeric severity"""
        severity_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        return severity_map.get(level, 0)
    
    def _get_severity_color(self, level: str) -> str:
        """Get color code for severity level"""
        color_map = self.config.get("severity_colors", {
            "CRITICAL": "#FF0000",
            "ERROR": "#FF6B6B",
            "WARNING": "#FFB74D",
            "INFO": "#4FC3F7",
            "DEBUG": "#9E9E9E"
        })
        return color_map.get(level, "#000000")