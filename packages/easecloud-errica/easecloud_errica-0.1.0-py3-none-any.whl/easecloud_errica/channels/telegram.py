"""
Telegram notification channel implementation
"""

import os
import tempfile
import requests
from typing import Dict, Any, Optional

from .base import BaseChannel, ChannelResult
from ..formatters import MarkdownFormatter, MessageData


class TelegramChannel(BaseChannel):
    """Telegram channel for sending notifications via Telegram Bot API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("telegram", config)
        
        # Telegram-specific configuration
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")
        
        if not self.bot_token or not self.chat_id:
            raise ValueError("Telegram channel requires bot_token and chat_id")
        
        # Setup API URLs
        self.message_api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        self.document_api_url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        
        # Setup requests session with proxy if needed
        self.session = requests.Session()
        self.proxy_enabled = self._setup_proxy()
        
        # Environment-specific behavior
        self.environment = config.get("environment", "production")
        self.is_local = self.environment in ["local", "development", "dev"]
        
        # Should we skip actual API calls in local environment?
        self.skip_api_in_local = self.is_local and not self.proxy_enabled and not config.get("force_api_in_local", False)
    
    def _create_formatter(self) -> MarkdownFormatter:
        """Create markdown formatter for Telegram"""
        formatter_config = self.config.get("formatter", {})
        formatter_config.update(self.config.get("severity_config", {}))
        return MarkdownFormatter(formatter_config)
    
    def _setup_proxy(self) -> bool:
        """Setup proxy configuration for Telegram API calls"""
        proxy_config = self.config.get("proxy", {})
        proxy_enabled = proxy_config.get("enabled", False)
        
        if not proxy_enabled:
            return False
        
        proxy_type = proxy_config.get("type", "http")
        proxy_host = proxy_config.get("host", "")
        proxy_port = proxy_config.get("port", 0)
        proxy_username = proxy_config.get("username", "")
        proxy_password = proxy_config.get("password", "")
        
        if not proxy_host or not proxy_port:
            return False
        
        # Build proxy URL
        auth_string = ""
        if proxy_username and proxy_password:
            auth_string = f"{proxy_username}:{proxy_password}@"
        
        proxy_url = f"{proxy_type}://{auth_string}{proxy_host}:{proxy_port}"
        
        self.session.proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        return True
    
    def _send_message_impl(self, formatted_message: str, data: MessageData) -> ChannelResult:
        """Send message to Telegram"""
        if self.skip_api_in_local:
            print(f"[TELEGRAM-LOCAL] {data.level}: {data.message}")
            return ChannelResult(True, "Message logged locally (local environment)", {"local": True})
        
        try:
            # Telegram message limit is 4096 characters
            if len(formatted_message) > 4000:
                return ChannelResult(False, "Message too long for Telegram, should use file")
            
            response = self.session.post(self.message_api_url, data={
                "chat_id": self.chat_id,
                "text": formatted_message,
                "parse_mode": "Markdown"
            })
            response.raise_for_status()
            
            result_data = response.json()
            return ChannelResult(True, "Message sent successfully", result_data)
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send Telegram message: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending Telegram message: {e}")
    
    def _send_file_impl(self, file_content: str, filename: str, data: MessageData) -> ChannelResult:
        """Send file to Telegram"""
        if self.skip_api_in_local:
            print(f"[TELEGRAM-LOCAL-FILE] {data.level}: {filename}")
            print(f"Content preview: {file_content[:200]}...")
            return ChannelResult(True, "File logged locally (local environment)", {"local": True, "filename": filename})
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Send the file
                with open(temp_file_path, 'rb') as file:
                    files = {'document': (filename, file, 'text/plain')}
                    
                    # Create caption
                    caption = self._create_file_caption(data)
                    
                    data_payload = {
                        'chat_id': self.chat_id,
                        'caption': caption,
                        'parse_mode': 'Markdown'
                    }
                    
                    response = self.session.post(self.document_api_url, data=data_payload, files=files)
                    response.raise_for_status()
                    
                    result_data = response.json()
                    return ChannelResult(True, "File sent successfully", result_data)
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
                    
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send Telegram file: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending Telegram file: {e}")
    
    def _create_file_caption(self, data: MessageData) -> str:
        """Create caption for file attachment"""
        level_emoji = self.formatter.get_severity_emoji(data.level)
        env_emoji = self.formatter.get_environment_emoji(data.environment)
        
        exc_type = "Unknown"
        if data.exception:
            exc_type = type(data.exception).__name__
        
        caption_parts = [
            f"{level_emoji} **{data.level} Report**",
            f"{env_emoji} `{data.app_name} v{data.app_version}`",
            f"🌍 `{data.environment.upper()}`"
        ]
        
        if data.exception:
            caption_parts.append(f"⚡ `{exc_type}`")
        
        if data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            caption_parts.append(f"📍 `{location}`")
        
        return "\n".join(caption_parts)
    
    def health_check(self) -> ChannelResult:
        """Check Telegram bot health"""
        if self.skip_api_in_local:
            return ChannelResult(True, "Health check skipped (local environment)", {"local": True})
        
        try:
            # Use getMe API to check bot status
            get_me_url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = self.session.get(get_me_url)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get("ok"):
                return ChannelResult(True, "Telegram bot is healthy", bot_info.get("result", {}))
            else:
                return ChannelResult(False, f"Telegram API error: {bot_info.get('description', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to connect to Telegram API: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error during health check: {e}")
    
    def send_custom_alert(self, message: str, severity: str = "INFO", 
                         context: Optional[Dict[str, Any]] = None,
                         send_as_file: bool = False) -> ChannelResult:
        """Send a custom alert message (compatibility method)"""
        from datetime import datetime
        
        # Create MessageData for the alert
        data = MessageData(
            level=severity,
            message=message,
            timestamp=datetime.now(),
            app_name=self.config.get("app_name", "Unknown App"),
            app_version=self.config.get("app_version", "1.0.0"),
            environment=self.environment,
            context=context
        )
        
        if send_as_file:
            return self.send_file(data)
        else:
            return self.send_message(data)