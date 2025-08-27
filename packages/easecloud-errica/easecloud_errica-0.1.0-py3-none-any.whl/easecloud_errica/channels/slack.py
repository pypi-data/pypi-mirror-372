"""
Slack notification channel implementation
"""

import json
import requests
from typing import Dict, Any, Optional, List

from .base import BaseChannel, ChannelResult
from ..formatters import JsonFormatter, MessageData


class SlackFormatter(JsonFormatter):
    """Slack-specific formatter for rich message blocks"""
    
    def format_message(self, data: MessageData) -> str:
        """Format message for Slack using blocks"""
        blocks = self._create_message_blocks(data)
        
        payload = {
            "blocks": blocks,
            "username": self.config.get("username", "Errica"),
            "icon_emoji": self.config.get("icon_emoji", ":warning:")
        }
        
        # Add channel if specified
        channel = self.config.get("channel")
        if channel:
            payload["channel"] = channel
        
        return json.dumps(payload)
    
    def format_exception(self, data: MessageData) -> str:
        """Format exception for Slack using blocks"""
        blocks = self._create_exception_blocks(data)
        
        payload = {
            "blocks": blocks,
            "username": self.config.get("username", "Errica"),
            "icon_emoji": self.config.get("icon_emoji", ":rotating_light:")
        }
        
        # Add channel if specified
        channel = self.config.get("channel")
        if channel:
            payload["channel"] = channel
        
        # Add mentions for critical errors
        if data.level == "CRITICAL":
            mention = self.config.get("mention_on_critical", "")
            if mention:
                payload["text"] = f"{mention} Critical error in {data.app_name}"
        
        return json.dumps(payload)
    
    def _create_message_blocks(self, data: MessageData) -> List[Dict]:
        """Create Slack blocks for regular message"""
        severity_info = self.config.get("severity_config", {}).get(data.level, {})
        color = severity_info.get("color", "warning")
        
        # Header block
        header_text = f"*{data.level}* | {data.app_name} v{data.app_version} | {data.environment.upper()}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": header_text
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        # Add source location if available
        if data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            blocks[1]["fields"].append({
                "type": "mrkdwn",
                "text": f"*Location:*\n`{location}`"
            })
        
        # Message block
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Message:*\n```{data.message}```"
            }
        })
        
        # Context block if available
        if data.context and self.should_include_context(data):
            context_text = json.dumps(data.context, indent=2)
            if len(context_text) < 2500:  # Slack limit for text blocks
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Context:*\n```{context_text}```"
                    }
                })
        
        # Wrap in attachment for color
        return [{
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " "
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"{data.level} Alert"
                },
                "style": "danger" if data.level in ["CRITICAL", "ERROR"] else "primary"
            }
        }] + blocks
    
    def _create_exception_blocks(self, data: MessageData) -> List[Dict]:
        """Create Slack blocks for exception"""
        severity_info = self.config.get("severity_config", {}).get(data.level, {})
        color = severity_info.get("color", "danger")
        
        # Header block with exception type
        exc_type = type(data.exception).__name__ if data.exception else "Exception"
        header_text = f":rotating_light: *Exception Report* | {exc_type}"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{data.level} - {data.app_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": header_text
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{data.environment.upper()}"
                    }
                ]
            }
        ]
        
        # Add source location if available
        if data.source_location:
            location = f"{data.source_location.get('module', 'unknown')}:{data.source_location.get('function', 'unknown')}:{data.source_location.get('line', 'unknown')}"
            blocks[2]["fields"].append({
                "type": "mrkdwn",
                "text": f"*Location:*\n`{location}`"
            })
        
        # Message block
        blocks.append({
            "type": "section", 
            "text": {
                "type": "mrkdwn",
                "text": f"*Error Message:*\n```{data.message}```"
            }
        })
        
        # Exception details if available
        if data.exception:
            exc_details = f"{type(data.exception).__name__}: {str(data.exception)}"
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Exception:*\n```{exc_details}```"
                }
            })
        
        # Context block if available
        if data.context and self.should_include_context(data):
            context_text = json.dumps(data.context, indent=2)
            if len(context_text) < 2500:  # Slack limit
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Context:*\n```{context_text}```"
                    }
                })
        
        return blocks


class SlackChannel(BaseChannel):
    """Slack channel for sending notifications via webhooks"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("slack", config)
        
        # Slack-specific configuration
        self.webhook_url = config.get("webhook_url")
        if not self.webhook_url:
            raise ValueError("Slack channel requires webhook_url")
        
        # Setup requests session
        self.session = requests.Session()
        
        # Slack-specific settings
        self.thread_errors = config.get("thread_errors", True)
        self.timeout = config.get("timeout", 30)
        
        # Thread tracking for related errors
        self.thread_ts_cache = {}
    
    def _create_formatter(self) -> SlackFormatter:
        """Create Slack formatter"""
        formatter_config = self.config.copy()
        return SlackFormatter(formatter_config)
    
    def _send_message_impl(self, formatted_message: str, data: MessageData) -> ChannelResult:
        """Send message to Slack"""
        try:
            # Parse the formatted message (JSON payload)
            payload = json.loads(formatted_message)
            
            # Add thread_ts if this is a follow-up error and threading is enabled
            if self.thread_errors and data.exception:
                thread_key = self._get_thread_key(data)
                if thread_key in self.thread_ts_cache:
                    payload["thread_ts"] = self.thread_ts_cache[thread_key]
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Store thread_ts if this started a new thread
            if self.thread_errors and data.exception and response.text == "ok":
                # Note: Webhook responses don't include thread_ts, so we'll use a simple caching strategy
                thread_key = self._get_thread_key(data)
                # Use current timestamp as a simple thread identifier
                import time
                self.thread_ts_cache[thread_key] = str(int(time.time()))
            
            return ChannelResult(True, "Message sent to Slack successfully", {"response": response.text})
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send Slack message: {e}")
        except json.JSONDecodeError as e:
            return ChannelResult(False, f"Invalid JSON payload for Slack: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending Slack message: {e}")
    
    def _send_file_impl(self, file_content: str, filename: str, data: MessageData) -> ChannelResult:
        """Send file to Slack (as a snippet in message)"""
        try:
            # Create a message with the file content as a code block
            if len(file_content) > 2500:
                # Truncate if too long for Slack
                file_content = file_content[:2500] + "\n... (truncated)"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{data.level} Report - {filename}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*App:* {data.app_name} v{data.app_version} | *Environment:* {data.environment.upper()}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{file_content}```"
                    }
                }
            ]
            
            payload = {
                "blocks": blocks,
                "username": self.config.get("username", "Errica"),
                "icon_emoji": self.config.get("icon_emoji", ":page_facing_up:")
            }
            
            # Add channel if specified
            channel = self.config.get("channel")
            if channel:
                payload["channel"] = channel
            
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return ChannelResult(True, "File content sent to Slack successfully", {"response": response.text})
            
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to send file to Slack: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error sending file to Slack: {e}")
    
    def _get_thread_key(self, data: MessageData) -> str:
        """Generate a key for thread tracking"""
        if data.exception:
            exc_type = type(data.exception).__name__
            # Use exception type + source location as thread key
            location = ""
            if data.source_location:
                location = f"{data.source_location.get('function', '')}:{data.source_location.get('line', '')}"
            return f"{exc_type}:{location}"
        return f"{data.level}:{data.message[:50]}"
    
    def health_check(self) -> ChannelResult:
        """Check Slack webhook health"""
        try:
            # Send a minimal test payload
            test_payload = {
                "text": "Health check from Errica",
                "username": self.config.get("username", "Errica"),
                "icon_emoji": ":white_check_mark:"
            }
            
            response = self.session.post(
                self.webhook_url,
                json=test_payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if response.text == "ok":
                return ChannelResult(True, "Slack webhook is healthy", {"response": response.text})
            else:
                return ChannelResult(False, f"Unexpected Slack response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            return ChannelResult(False, f"Failed to connect to Slack webhook: {e}")
        except Exception as e:
            return ChannelResult(False, f"Unexpected error during Slack health check: {e}")
    
    def send_custom_alert(self, message: str, severity: str = "INFO", 
                         context: Optional[Dict[str, Any]] = None) -> ChannelResult:
        """Send a custom alert message to Slack"""
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