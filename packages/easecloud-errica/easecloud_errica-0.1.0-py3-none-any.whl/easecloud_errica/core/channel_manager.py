"""
Channel manager for routing and orchestrating notifications across multiple channels
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..channels import BaseChannel, ChannelResult, TelegramChannel, SlackChannel, WebhookChannel, ConsoleChannel
from ..formatters import MessageData
from .config import ErricaConfig


class ChannelManager:
    """Manages multiple notification channels and routes messages appropriately"""
    
    def __init__(self, config: ErricaConfig):
        self.config = config
        self.channels: Dict[str, BaseChannel] = {}
        self.enabled_channels: List[str] = []
        
        # Threading for parallel sends
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="Errica")
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "messages_sent": 0,
            "errors_sent": 0,
            "failed_sends": 0,
            "channels_initialized": 0
        }
        
        # Initialize channels
        self._initialize_channels()
    
    def _initialize_channels(self):
        """Initialize all enabled channels"""
        app_config = self.config.get_app_config()
        
        for channel_name in self.config.get_enabled_channels():
            try:
                channel_config = self.config.get_channel_config(channel_name)
                
                # Add app info to channel config
                channel_config.update({
                    "app_name": app_config.get("name", "Unknown App"),
                    "app_version": app_config.get("version", "1.0.0"),
                    "environment": app_config.get("environment", "production")
                })
                
                # Create channel instance
                channel = self._create_channel(channel_name, channel_config)
                if channel:
                    self.channels[channel_name] = channel
                    self.enabled_channels.append(channel_name)
                    self.stats["channels_initialized"] += 1
                    print(f"✅ Initialized {channel_name} channel")
                    
            except Exception as e:
                print(f"❌ Failed to initialize {channel_name} channel: {e}")
    
    def _create_channel(self, channel_name: str, config: Dict[str, Any]) -> Optional[BaseChannel]:
        """Create a channel instance"""
        if channel_name == "telegram":
            return TelegramChannel(config)
        elif channel_name == "slack":
            return SlackChannel(config)
        elif channel_name == "webhook":
            return WebhookChannel(config)
        elif channel_name == "console":
            return ConsoleChannel(config)
        else:
            print(f"Unknown channel type: {channel_name}")
            return None
    
    def send_message(self, data: MessageData, channels: Optional[List[str]] = None) -> Dict[str, ChannelResult]:
        """Send a message to specified channels or route based on configuration"""
        with self.lock:
            self.stats["messages_sent"] += 1
        
        # Determine target channels
        if channels is None:
            channels = self.config.get_channels_for_level(data.level, data.environment)
        
        # Filter to only enabled channels
        target_channels = [ch for ch in channels if ch in self.channels]
        
        if not target_channels:
            return {"error": ChannelResult(False, "No enabled channels available")}
        
        # Send to channels in parallel
        return self._send_to_channels_parallel(data, target_channels, "send_message")
    
    def send_error(self, data: MessageData, channels: Optional[List[str]] = None) -> Dict[str, ChannelResult]:
        """Send an error message (determines if file or message based on channel config)"""
        with self.lock:
            self.stats["errors_sent"] += 1
        
        # Determine target channels
        if channels is None:
            channels = self.config.get_channels_for_level(data.level, data.environment)
        
        # Filter to only enabled channels
        target_channels = [ch for ch in channels if ch in self.channels]
        
        if not target_channels:
            return {"error": ChannelResult(False, "No enabled channels available")}
        
        # Send to channels in parallel, letting each channel decide message vs file
        results = {}
        
        def send_to_channel(channel_name: str) -> Tuple[str, ChannelResult]:
            channel = self.channels[channel_name]
            
            # Let channel decide if it should send as file
            if channel.should_send_as_file(data):
                return channel_name, channel.send_file(data)
            else:
                return channel_name, channel.send_message(data)
        
        # Execute in parallel
        futures = []
        for channel_name in target_channels:
            future = self.executor.submit(send_to_channel, channel_name)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                channel_name, result = future.result(timeout=30)
                results[channel_name] = result
                
                if not result.success:
                    with self.lock:
                        self.stats["failed_sends"] += 1
                        
            except Exception as e:
                # Handle channel that failed completely
                results["unknown_channel"] = ChannelResult(False, f"Channel execution failed: {e}")
                with self.lock:
                    self.stats["failed_sends"] += 1
        
        return results
    
    def send_custom_message(self, message: str, level: str = "INFO", 
                          context: Optional[Dict[str, Any]] = None, 
                          channels: Optional[List[str]] = None) -> Dict[str, ChannelResult]:
        """Send a custom message"""
        app_config = self.config.get_app_config()
        
        data = MessageData(
            level=level,
            message=message,
            timestamp=datetime.now(),
            app_name=app_config.get("name", "Unknown App"),
            app_version=app_config.get("version", "1.0.0"),
            environment=app_config.get("environment", "production"),
            context=context
        )
        
        return self.send_message(data, channels)
    
    def send_to_channels(self, message: str, level: str, context: Optional[Dict[str, Any]], 
                        channels: List[str]) -> Dict[str, ChannelResult]:
        """Send message to specific channels"""
        return self.send_custom_message(message, level, context, channels)
    
    def _send_to_channels_parallel(self, data: MessageData, channels: List[str], 
                                 method: str) -> Dict[str, ChannelResult]:
        """Send to multiple channels in parallel"""
        results = {}
        
        def send_to_channel(channel_name: str) -> Tuple[str, ChannelResult]:
            channel = self.channels[channel_name]
            if method == "send_message":
                return channel_name, channel.send_message(data)
            elif method == "send_file":
                return channel_name, channel.send_file(data)
            else:
                return channel_name, ChannelResult(False, f"Unknown method: {method}")
        
        # Execute in parallel
        futures = []
        for channel_name in channels:
            if channel_name in self.channels:
                future = self.executor.submit(send_to_channel, channel_name)
                futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                channel_name, result = future.result(timeout=30)
                results[channel_name] = result
                
                if not result.success:
                    with self.lock:
                        self.stats["failed_sends"] += 1
                        
            except Exception as e:
                # Handle channel that failed completely
                results["unknown_channel"] = ChannelResult(False, f"Channel execution failed: {e}")
                with self.lock:
                    self.stats["failed_sends"] += 1
        
        return results
    
    def health_check_all(self) -> Dict[str, ChannelResult]:
        """Run health checks on all channels"""
        results = {}
        
        def check_channel(channel_name: str) -> Tuple[str, ChannelResult]:
            channel = self.channels[channel_name]
            return channel_name, channel.health_check()
        
        # Execute health checks in parallel
        futures = []
        for channel_name in self.channels:
            future = self.executor.submit(check_channel, channel_name)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                channel_name, result = future.result(timeout=10)
                results[channel_name] = result
            except Exception as e:
                results["unknown_channel"] = ChannelResult(False, f"Health check failed: {e}")
        
        return results
    
    def get_channel(self, channel_name: str) -> Optional[BaseChannel]:
        """Get a specific channel instance"""
        return self.channels.get(channel_name)
    
    def is_channel_enabled(self, channel_name: str) -> bool:
        """Check if a channel is enabled"""
        return channel_name in self.enabled_channels
    
    def get_stats(self) -> Dict[str, Any]:
        """Get channel manager statistics"""
        with self.lock:
            stats = dict(self.stats)
        
        # Add channel-specific stats
        channel_stats = {}
        for name, channel in self.channels.items():
            if hasattr(channel, 'get_stats'):
                channel_stats[name] = channel.get_stats()
        
        stats["channels"] = channel_stats
        stats["enabled_channels"] = self.enabled_channels
        stats["total_channels"] = len(self.channels)
        
        return stats
    
    def reset_channel_limits(self, channel_name: Optional[str] = None):
        """Reset rate limiting and deduplication for channels"""
        if channel_name:
            channel = self.channels.get(channel_name)
            if channel and hasattr(channel, 'reset_limits'):
                channel.reset_limits()
        else:
            # Reset all channels
            for channel in self.channels.values():
                if hasattr(channel, 'reset_limits'):
                    channel.reset_limits()
    
    def add_channel(self, channel_name: str, channel_config: Dict[str, Any]) -> bool:
        """Dynamically add a new channel"""
        try:
            # Add app info to channel config
            app_config = self.config.get_app_config()
            channel_config.update({
                "app_name": app_config.get("name", "Unknown App"),
                "app_version": app_config.get("version", "1.0.0"),
                "environment": app_config.get("environment", "production")
            })
            
            channel = self._create_channel(channel_name, channel_config)
            if channel:
                self.channels[channel_name] = channel
                if channel_name not in self.enabled_channels:
                    self.enabled_channels.append(channel_name)
                
                with self.lock:
                    self.stats["channels_initialized"] += 1
                
                print(f"✅ Dynamically added {channel_name} channel")
                return True
                
        except Exception as e:
            print(f"❌ Failed to add {channel_name} channel: {e}")
        
        return False
    
    def remove_channel(self, channel_name: str) -> bool:
        """Remove a channel"""
        if channel_name in self.channels:
            del self.channels[channel_name]
            if channel_name in self.enabled_channels:
                self.enabled_channels.remove(channel_name)
            print(f"🗑️ Removed {channel_name} channel")
            return True
        return False
    
    def send_task_start(self, task_name: str, category: str, context: Optional[Dict] = None):
        """Send task start notification"""
        message = f"Task started: {task_name}"
        self.send_custom_message(message, "INFO", {
            "task_name": task_name,
            "category": category,
            "type": "task_start",
            **(context or {})
        }, ["console"])  # Usually only to console
    
    def send_task_complete(self, task_name: str, category: str, duration: float, 
                          context: Optional[Dict] = None):
        """Send task completion notification"""
        message = f"Task completed: {task_name} (took {duration:.2f}s)"
        self.send_custom_message(message, "INFO", {
            "task_name": task_name,
            "category": category,
            "duration": duration,
            "type": "task_complete",
            **(context or {})
        }, ["console"])  # Usually only to console
    
    def send_task_error(self, task_name: str, error: Exception, context: Optional[Dict] = None):
        """Send task error notification"""
        app_config = self.config.get_app_config()
        
        data = MessageData(
            level="ERROR",
            message=f"Task failed: {task_name}",
            timestamp=datetime.now(),
            app_name=app_config.get("name", "Unknown App"),
            app_version=app_config.get("version", "1.0.0"),
            environment=app_config.get("environment", "production"),
            exception=error,
            context={
                "task_name": task_name,
                "type": "task_error",
                **(context or {})
            }
        )
        
        return self.send_error(data)
    
    def shutdown(self):
        """Shutdown the channel manager"""
        print("🔄 Shutting down Channel Manager...")
        self.executor.shutdown(wait=True)
        print("✅ Channel Manager shutdown complete")