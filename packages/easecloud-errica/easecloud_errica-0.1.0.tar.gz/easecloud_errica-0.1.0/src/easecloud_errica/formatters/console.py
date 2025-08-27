"""
Console formatter for terminal output with colors and styling
"""

import json
import traceback
from typing import Dict, Any, Optional
from .base import BaseFormatter, MessageData


class ConsoleFormatter(BaseFormatter):
    """Console formatter with color support and structured output"""
    
    # ANSI color codes
    COLORS = {
        "red": "\033[91m",
        "yellow": "\033[93m", 
        "blue": "\033[94m",
        "green": "\033[92m",
        "gray": "\033[90m",
        "white": "\033[97m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.use_colors = config.get("use_colors", True)
        self.include_timestamp = config.get("include_timestamp", True)
        self.include_level = config.get("include_level", True)
        self.include_source = config.get("include_source", True)
        self.format_template = config.get("format", "{timestamp} [{level}] {app_name}: {message}")
        
        # Color scheme
        self.color_scheme = config.get("color_scheme", {
            "CRITICAL": "red",
            "ERROR": "red",
            "WARNING": "yellow",
            "INFO": "blue",
            "DEBUG": "gray"
        })
    
    def format_message(self, data: MessageData) -> str:
        """Format a regular message for console output"""
        # Build the main message line
        main_line = self._format_main_line(data)
        lines = [main_line]
        
        # Add source location if enabled and available
        if self.include_source and data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            location_line = self._colorize(f"  📍 Source: {location}", "gray")
            lines.append(location_line)
        
        # Add context if available
        if self.should_include_context(data):
            context_line = self._colorize(f"  🔍 Context: {json.dumps(data.context)}", "gray")
            lines.append(context_line)
        
        return "\n".join(lines)
    
    def format_exception(self, data: MessageData) -> str:
        """Format an exception message for console output"""
        # Build the main message line
        main_line = self._format_main_line(data)
        lines = [main_line]
        
        # Add exception details if available
        if data.exception:
            exc_type = type(data.exception).__name__
            exc_message = str(data.exception)
            exc_line = self._colorize(f"  ⚡ Exception: {exc_type}: {exc_message}", "red")
            lines.append(exc_line)
        
        # Add source location if enabled and available
        if self.include_source and data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            location_line = self._colorize(f"  📍 Source: {location}", "gray")
            lines.append(location_line)
        
        # Add context if available
        if self.should_include_context(data):
            context_line = self._colorize(f"  🔍 Context: {json.dumps(data.context)}", "gray")
            lines.append(context_line)
        
        return "\n".join(lines)
    
    def format_detailed_exception(self, data: MessageData) -> str:
        """Format detailed exception with full traceback for console"""
        lines = []
        
        # Header
        header = "=" * 80
        lines.append(self._colorize(header, "red"))
        lines.append(self._colorize(f"EXCEPTION REPORT - {data.app_name} v{data.app_version}", "red"))
        lines.append(self._colorize(header, "red"))
        
        # Basic info
        lines.append(f"Environment: {self._colorize(data.environment.upper(), 'yellow')}")
        lines.append(f"Timestamp: {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Level: {self._colorize(data.level, self.color_scheme.get(data.level, 'white'))}")
        lines.append("")
        
        # Application details
        lines.append(self._colorize("APPLICATION DETAILS:", "bold"))
        lines.append("-" * 40)
        lines.append(f"App Name: {data.app_name}")
        lines.append(f"App Version: {data.app_version}")
        lines.append(f"Environment: {data.environment}")
        
        if data.source_location:
            lines.append(f"Module: {data.source_location.get('module', 'unknown')}")
            lines.append(f"Function: {data.source_location.get('function', 'unknown')}")
            lines.append(f"Line: {data.source_location.get('line', 'unknown')}")
        
        lines.append("")
        
        # Log message
        lines.append(self._colorize("LOG MESSAGE:", "bold"))
        lines.append("-" * 40)
        lines.append(data.message)
        lines.append("")
        
        # Exception details
        if data.exception:
            lines.append(self._colorize("EXCEPTION DETAILS:", "bold"))
            lines.append("-" * 40)
            lines.append("")
            lines.append(f"Type: {self._colorize(type(data.exception).__name__, 'red')}")
            lines.append(f"Message: {str(data.exception)}")
            lines.append("")
            
            # Full traceback
            if hasattr(data.exception, '__traceback__') and data.exception.__traceback__:
                lines.append(self._colorize("FULL TRACEBACK:", "bold"))
                lines.append("-" * 20)
                tb_lines = traceback.format_exception(type(data.exception), data.exception, data.exception.__traceback__)
                for line in tb_lines:
                    lines.append(line.rstrip())
                lines.append("")
        
        # Context information
        if data.context:
            lines.append(self._colorize("CONTEXT INFORMATION:", "bold"))
            lines.append("-" * 40)
            lines.append(json.dumps(data.context, indent=2))
            lines.append("")
        
        # Footer
        lines.append(self._colorize("=" * 80, "red"))
        lines.append(self._colorize(f"End of Exception Report - {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", "red"))
        lines.append(self._colorize("=" * 80, "red"))
        
        return "\n".join(lines)
    
    def _format_main_line(self, data: MessageData) -> str:
        """Format the main message line"""
        # Prepare template variables
        template_vars = {
            "timestamp": data.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.include_timestamp else "",
            "level": data.level if self.include_level else "",
            "app_name": data.app_name,
            "app_version": data.app_version,
            "environment": data.environment,
            "message": data.message
        }
        
        # Format the message
        formatted = self.format_template.format(**template_vars)
        
        # Apply colors
        level_color = self.color_scheme.get(data.level, "white")
        formatted = self._colorize(formatted, level_color)
        
        # Add severity emoji
        emoji = self.get_severity_emoji(data.level)
        formatted = f"{emoji} {formatted}"
        
        return formatted
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color, "")
        reset_code = self.COLORS.get("reset", "")
        
        if color_code and reset_code:
            return f"{color_code}{text}{reset_code}"
        
        return text