"""
Markdown formatter for Telegram and Slack channels
"""

import json
import traceback
from typing import Dict, Any, Optional
from .base import BaseFormatter, MessageData


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter for channels that support markdown (Telegram, Slack)"""
    
    def format_message(self, data: MessageData) -> str:
        """Format a regular message"""
        level_emoji = self.get_severity_emoji(data.level)
        env_emoji = self.get_environment_emoji(data.environment)
        
        # Build header
        header_parts = [
            f"{level_emoji} **{data.level}**",
            f"{env_emoji} `{data.app_name} v{data.app_version}`",
            f"🌍 `{data.environment.upper()}`"
        ]
        
        header = " | ".join(header_parts)
        
        # Build message body
        lines = [
            header,
            f"⏰ `{data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}`",
        ]
        
        # Add source location if available
        if data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            lines.append(f"📍 `{location}`")
        
        lines.extend([
            "",
            f"💬 **Message:**",
            f"```",
            data.message,
            f"```"
        ])
        
        # Add context if available and should be included
        if self.should_include_context(data):
            lines.extend([
                "",
                f"🔍 **Context:**",
                f"```json",
                json.dumps(data.context, indent=2),
                f"```"
            ])
        
        return "\n".join(lines)
    
    def format_exception(self, data: MessageData) -> str:
        """Format an exception message"""
        level_emoji = self.get_severity_emoji(data.level)
        env_emoji = self.get_environment_emoji(data.environment)
        
        # Build header
        header_parts = [
            f"{level_emoji} **Exception Report**",
            f"{env_emoji} `{data.app_name} v{data.app_version}`",
            f"🌍 `{data.environment.upper()}`"
        ]
        
        if data.exception:
            header_parts.append(f"⚡ `{type(data.exception).__name__}`")
        
        header = "\n".join(header_parts)
        
        # Build message body
        lines = [
            header,
            f"⏰ `{data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}`",
        ]
        
        # Add source location if available
        if data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            lines.append(f"📍 `{location}`")
        
        lines.extend([
            "",
            f"💬 **Message:**",
            f"```",
            data.message,
            f"```"
        ])
        
        # Add exception details if available
        if data.exception:
            lines.extend([
                "",
                f"🔥 **Exception:**",
                f"```",
                f"{type(data.exception).__name__}: {str(data.exception)}",
                f"```"
            ])
        
        # Add context if available
        if self.should_include_context(data):
            lines.extend([
                "",
                f"🔍 **Context:**",
                f"```json",
                json.dumps(data.context, indent=2),
                f"```"
            ])
        
        return "\n".join(lines)
    
    def format_exception_file(self, data: MessageData) -> str:
        """Format detailed exception for file attachment"""
        lines = [
            "=" * 80,
            f"EXCEPTION REPORT - {data.app_name} v{data.app_version}",
            "=" * 80,
            f"Environment: {data.environment.upper()}",
            f"Timestamp: {data.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Severity: {data.level}",
            "",
            "APPLICATION DETAILS:",
            "-" * 40,
            f"App Name: {data.app_name}",
            f"App Version: {data.app_version}",
            f"Environment: {data.environment}",
        ]
        
        # Add source location details
        if data.source_location:
            lines.extend([
                f"Module: {data.source_location.get('module', 'unknown')}",
                f"Function: {data.source_location.get('function', 'unknown')}",
                f"Line: {data.source_location.get('line', 'unknown')}",
            ])
        
        lines.extend([
            "",
            "LOG MESSAGE:",
            "-" * 40,
            data.message,
            ""
        ])
        
        # Add exception details
        if data.exception:
            lines.extend([
                "EXCEPTION DETAILS:",
                "-" * 40,
                "",
                "Exception Information:",
                f"Type: {type(data.exception).__name__}",
                f"Message: {str(data.exception)}",
                "",
                "Full Traceback:",
                "-" * 20
            ])
            
            # Get the full traceback
            if hasattr(data.exception, '__traceback__') and data.exception.__traceback__:
                tb_lines = traceback.format_exception(type(data.exception), data.exception, data.exception.__traceback__)
                lines.extend(tb_lines)
        
        # Add context information
        if data.context:
            lines.extend([
                "",
                "CONTEXT INFORMATION:",
                "-" * 40,
                json.dumps(data.context, indent=2),
                ""
            ])
        
        lines.extend([
            "",
            "=" * 80,
            f"End of Exception Report - {data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80
        ])
        
        return "\n".join(lines)