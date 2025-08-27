"""
Console notification channel implementation
"""

import sys
from typing import Dict, Any, Optional

from .base import BaseChannel, ChannelResult
from ..formatters.console import ConsoleFormatter
from ..formatters import MessageData


class ConsoleChannel(BaseChannel):
    """Console channel for terminal output with enhanced formatting"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("console", config)
        
        # Console-specific configuration
        self.output_stream = config.get("output_stream", "stdout")  # stdout or stderr
        self.show_detailed_exceptions = config.get("show_detailed_exceptions", True)
        
        # Get the appropriate output stream
        if self.output_stream == "stderr":
            self.stream = sys.stderr
        else:
            self.stream = sys.stdout
    
    def _create_formatter(self) -> ConsoleFormatter:
        """Create console formatter"""
        formatter_config = self.config.copy()
        return ConsoleFormatter(formatter_config)
    
    def _send_message_impl(self, formatted_message: str, data: MessageData) -> ChannelResult:
        """Send message to console"""
        try:
            # Print to the configured stream
            print(formatted_message, file=self.stream)
            self.stream.flush()
            
            return ChannelResult(True, "Message printed to console", {"stream": self.output_stream})
            
        except Exception as e:
            return ChannelResult(False, f"Failed to print to console: {e}")
    
    def _send_file_impl(self, file_content: str, filename: str, data: MessageData) -> ChannelResult:
        """Send file content to console (print the content)"""
        try:
            # Print file header
            header = f"\n{'='*60}\nFILE CONTENT: {filename}\n{'='*60}"
            print(header, file=self.stream)
            
            # Print file content
            print(file_content, file=self.stream)
            
            # Print file footer
            footer = f"{'='*60}\nEND OF FILE: {filename}\n{'='*60}\n"
            print(footer, file=self.stream)
            
            self.stream.flush()
            
            return ChannelResult(True, "File content printed to console", {"filename": filename, "stream": self.output_stream})
            
        except Exception as e:
            return ChannelResult(False, f"Failed to print file to console: {e}")
    
    def send_message(self, data: MessageData, force: bool = False) -> ChannelResult:
        """Override to handle detailed exceptions"""
        if not self.enabled:
            return ChannelResult(False, f"Channel {self.name} is disabled")
        
        # For exceptions, use detailed formatting if enabled
        if data.exception and self.show_detailed_exceptions:
            try:
                detailed_message = self.formatter.format_detailed_exception(data)
                print(detailed_message, file=self.stream)
                self.stream.flush()
                return ChannelResult(True, "Detailed exception printed to console", {"stream": self.output_stream})
            except Exception as e:
                # Fall back to regular formatting
                pass
        
        # Use regular message sending for non-exceptions or if detailed formatting fails
        return super().send_message(data, force)
    
    def health_check(self) -> ChannelResult:
        """Check console health (always healthy)"""
        try:
            # Test that we can write to the stream
            original_position = self.stream.tell() if hasattr(self.stream, 'tell') else None
            test_message = "Console health check"
            print(test_message, file=self.stream)
            self.stream.flush()
            
            return ChannelResult(True, "Console is healthy", {"stream": self.output_stream})
            
        except Exception as e:
            return ChannelResult(False, f"Console health check failed: {e}")
    
    def send_progress_update(self, task_name: str, current: int, total: int, 
                           message: Optional[str] = None) -> ChannelResult:
        """Send a progress update to console"""
        try:
            # Calculate percentage
            percentage = (current / total) * 100 if total > 0 else 0
            
            # Create progress bar
            bar_length = 50
            filled_length = int(bar_length * current // total) if total > 0 else 0
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            # Build progress message
            progress_msg = f"\r{task_name}: |{bar}| {current}/{total} ({percentage:.1f}%)"
            if message:
                progress_msg += f" - {message}"
            
            # Print without newline (overwrite previous line)
            print(progress_msg, end='', file=self.stream)
            self.stream.flush()
            
            # Add newline if completed
            if current >= total:
                print("", file=self.stream)
            
            return ChannelResult(True, "Progress update printed", {
                "task": task_name,
                "current": current,
                "total": total,
                "percentage": percentage
            })
            
        except Exception as e:
            return ChannelResult(False, f"Failed to print progress update: {e}")
    
    def send_table(self, headers: list, rows: list, title: Optional[str] = None) -> ChannelResult:
        """Send a formatted table to console"""
        try:
            # Calculate column widths
            col_widths = [len(str(header)) for header in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    if i < len(col_widths):
                        col_widths[i] = max(col_widths[i], len(str(cell)))
            
            # Build table
            lines = []
            
            # Title
            if title:
                total_width = sum(col_widths) + 3 * (len(headers) - 1)
                lines.append(f"\n{title}")
                lines.append("=" * max(total_width, len(title)))
            
            # Header
            header_line = " | ".join(str(headers[i]).ljust(col_widths[i]) for i in range(len(headers)))
            lines.append(header_line)
            lines.append("-" * len(header_line))
            
            # Rows
            for row in rows:
                row_line = " | ".join(str(row[i]).ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i]) for i in range(len(headers)))
                lines.append(row_line)
            
            # Print table
            table_output = "\n".join(lines) + "\n"
            print(table_output, file=self.stream)
            self.stream.flush()
            
            return ChannelResult(True, "Table printed to console", {
                "rows": len(rows),
                "columns": len(headers),
                "title": title
            })
            
        except Exception as e:
            return ChannelResult(False, f"Failed to print table: {e}")
    
    def send_custom_alert(self, message: str, severity: str = "INFO", 
                         context: Optional[Dict[str, Any]] = None) -> ChannelResult:
        """Send a custom alert to console"""
        from datetime import datetime
        
        # Create MessageData for the alert
        data = MessageData(
            level=severity,
            message=message,
            timestamp=datetime.now(),
            app_name=self.config.get("app_name", "Unknown App"),
            app_version=self.config.get("app_version", "1.0.0"),
            environment=self.config.get("environment", "production"),
            context=context
        )
        
        return self.send_message(data)