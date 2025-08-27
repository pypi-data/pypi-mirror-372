"""
Generic webhook notification channel implementation
"""

import json
import requests
from urllib.parse import urlencode
from typing import Dict, Any, Optional

from .base import BaseChannel, ChannelResult
from ..formatters import JsonFormatter, MessageData


class WebhookChannel(BaseChannel):
    """Generic webhook channel for HTTP-based notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("webhook", config)
        
        # Webhook-specific configuration
        self.url = config.get("url")
        if not self.url:
            raise ValueError("Webhook channel requires url")
        
        self.method = config.get("method", "POST").upper()
        self.headers = config.get("headers", {"Content-Type": "application/json"})
        self.timeout = config.get("timeout", 30)
        self.payload_format = config.get("payload_format", "json")  # json or form
        
        # Authentication configuration
        self.auth_config = config.get("auth", {})
        
        # Setup requests session
        self.session = requests.Session()
        self._setup_authentication()
    
    def _create_formatter(self) -> JsonFormatter:
        """Create JSON formatter for webhooks"""
        formatter_config = self.config.get("formatter", {})
        formatter_config["pretty_print"] = self.config.get("pretty_print", False)
        return JsonFormatter(formatter_config)
    
    def _setup_authentication(self):
        """Setup authentication for webhook requests"""
        auth_type = self.auth_config.get("type", "none").lower()
        
        if auth_type == "basic":
            username = self.auth_config.get("username", "")
            password = self.auth_config.get("password", "")
            if username and password:
                self.session.auth = (username, password)
        
        elif auth_type == "bearer":
            token = self.auth_config.get("token", "")
            if token:
                self.session.headers["Authorization"] = f"Bearer {token}"
        
        elif auth_type == "custom":
            custom_headers = self.auth_config.get("custom_headers", {})
            self.session.headers.update(custom_headers)
        
        # Add any additional headers
        if self.headers:
            self.session.headers.update(self.headers)
    
    def _send_message_impl(self, formatted_message: str, data: MessageData) -> ChannelResult:
        """Send message to webhook"""
        try:
            # Prepare payload based on format
            if self.payload_format == "json":
                payload_data = json.loads(formatted_message)
                response = self._send_json_request(payload_data)
            elif self.payload_format == "form":
                payload_data = json.loads(formatted_message)
                response = self._send_form_request(payload_data)
            else:
                return ChannelResult(False, f"Unsupported payload format: {self.payload_format}")
            
            response.raise_for_status()
            
            # Try to parse response as JSON, fall back to text
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = {"text": response.text}
            
            return ChannelResult(
                True, 
                f"Message sent to webhook successfully (HTTP {response.status_code})", 
                {
                    "status_code": response.status_code,
                    "response": response_data,
                    "headers": dict(response.headers)
                }
            )
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send webhook request: {e}")
        except json.JSONDecodeError as e:
            return ChannelResult(False, f"Invalid JSON payload for webhook: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending webhook: {e}")
    
    def _send_file_impl(self, file_content: str, filename: str, data: MessageData) -> ChannelResult:
        """Send file content to webhook (as part of the payload)"""
        try:
            # Create payload with file content
            file_payload = {
                "type": "file",
                "filename": filename,
                "content": file_content,
                "app": {
                    "name": data.app_name,
                    "version": data.app_version,
                    "environment": data.environment
                },
                "timestamp": data.timestamp.isoformat(),
                "level": data.level,
                "message": data.message
            }
            
            if data.context:
                file_payload["context"] = data.context
            
            # Send based on format
            if self.payload_format == "json":
                response = self._send_json_request(file_payload)
            elif self.payload_format == "form":
                response = self._send_form_request(file_payload)
            else:
                return ChannelResult(False, f"Unsupported payload format: {self.payload_format}")
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = {"text": response.text}
            
            return ChannelResult(
                True,
                f"File sent to webhook successfully (HTTP {response.status_code})",
                {
                    "status_code": response.status_code,
                    "response": response_data,
                    "filename": filename
                }
            )
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send file to webhook: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending file to webhook: {e}")
    
    def _send_json_request(self, payload_data: Dict[str, Any]) -> requests.Response:
        """Send JSON request to webhook"""
        return self.session.request(
            method=self.method,
            url=self.url,
            json=payload_data,
            timeout=self.timeout
        )
    
    def _send_form_request(self, payload_data: Dict[str, Any]) -> requests.Response:
        """Send form-encoded request to webhook"""
        # Flatten nested dictionaries for form encoding
        flattened_data = self._flatten_dict(payload_data)
        
        if self.method == "GET":
            # For GET requests, add parameters to URL
            return self.session.get(
                url=self.url,
                params=flattened_data,
                timeout=self.timeout
            )
        else:
            # For POST/PUT/etc, send as form data
            return self.session.request(
                method=self.method,
                url=self.url,
                data=flattened_data,
                timeout=self.timeout
            )
    
    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, str]:
        """Flatten nested dictionary for form encoding"""
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", str(item)))
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    def health_check(self) -> ChannelResult:
        """Check webhook health"""
        try:
            # Send a minimal health check payload
            health_payload = {
                "type": "health_check",
                "timestamp": self._get_timestamp(),
                "source": "errica",
                "message": "Health check from Errica"
            }
            
            if self.payload_format == "json":
                response = self._send_json_request(health_payload)
            elif self.payload_format == "form":
                response = self._send_form_request(health_payload)
            else:
                return ChannelResult(False, f"Unsupported payload format: {self.payload_format}")
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = {"text": response.text}
            
            return ChannelResult(
                True, 
                f"Webhook is healthy (HTTP {response.status_code})",
                {
                    "status_code": response.status_code,
                    "response": response_data
                }
            )
                
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to connect to webhook: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error during webhook health check: {e}")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def send_custom_payload(self, payload: Dict[str, Any]) -> ChannelResult:
        """Send a custom payload to the webhook"""
        try:
            if self.payload_format == "json":
                response = self._send_json_request(payload)
            elif self.payload_format == "form":
                response = self._send_form_request(payload)
            else:
                return ChannelResult(False, f"Unsupported payload format: {self.payload_format}")
            
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = {"text": response.text}
            
            return ChannelResult(
                True,
                f"Custom payload sent successfully (HTTP {response.status_code})",
                {
                    "status_code": response.status_code,
                    "response": response_data
                }
            )
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send custom payload: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending custom payload: {e}")
    
    def send_custom_alert(self, message: str, severity: str = "INFO", 
                         context: Optional[Dict[str, Any]] = None) -> ChannelResult:
        """Send a custom alert message"""
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