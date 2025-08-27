"""
Errica by EaseCloud — Your Python error monitor

This package provides comprehensive error monitoring and notification capabilities
across multiple channels including Telegram, Slack, webhooks, email, and console output.

Features:
- Multi-channel notification routing
- Global exception handling
- Task and batch monitoring
- Rate limiting and deduplication
- Configurable error routing
- Rich message formatting

Usage:
    Basic setup:
    >>> from easecloud_errica import setup_monitoring
    >>> setup_monitoring()
    
    With custom configuration:
    >>> from easecloud_errica import setup_monitoring, create_config_from_env
    >>> config = create_config_from_env()
    >>> setup_monitoring(config)
    
    Context monitoring:
    >>> from easecloud_errica import task_monitor
    >>> with task_monitor("user_registration"):
    ...     # Your code here
    ...     pass
"""

__version__ = "0.1.0"
__author__ = "EaseCloud.io"
__email__ = "info@easecloud.io"

# Core imports
from .core import (
    ErricaConfig, create_default_config, create_config_from_env, load_config_from_file,
    ErrorHandler, initialize_error_handler, capture_exception, capture_message, get_error_handler,
    ErricaMonitoring, setup_monitoring, task_monitor, batch_monitor, error_context,
    capture_task_error, capture_custom_error, send_custom_alert, test_monitoring,
    monitor_function, monitor_async_function, task_context, batch_context
)

from .core.channel_manager import ChannelManager

# Channel imports
from .channels import (
    BaseChannel, ChannelResult, TelegramChannel, SlackChannel, 
    WebhookChannel, ConsoleChannel
)

# Formatter imports
from .formatters import (
    BaseFormatter, MessageData, MarkdownFormatter, JsonFormatter, ConsoleFormatter
)

# Utility imports
from .utils import RateLimiter, MessageDeduplicator

# Main exports
__all__ = [
    # Package info
    "__version__",
    "__author__", 
    "__email__",
    
    # Configuration
    "ErricaConfig",
    "create_default_config", 
    "create_config_from_env",
    "load_config_from_file",
    
    # Core monitoring
    "ErrorHandler",
    "ErricaMonitoring", 
    "ChannelManager",
    "initialize_error_handler",
    "setup_monitoring",
    
    # Context managers and decorators
    "task_monitor",
    "batch_monitor",
    "error_context",
    "monitor_function",
    "monitor_async_function",
    "task_context",
    "batch_context",
    
    # Error capture functions
    "capture_exception",
    "capture_message",
    "capture_task_error",
    "capture_custom_error",
    "send_custom_alert",
    
    # Utility functions
    "test_monitoring",
    "get_error_handler",
    
    # Channels
    "BaseChannel",
    "ChannelResult",
    "TelegramChannel",
    "SlackChannel", 
    "WebhookChannel",
    "ConsoleChannel",
    
    # Formatters
    "BaseFormatter",
    "MessageData",
    "MarkdownFormatter", 
    "JsonFormatter",
    "ConsoleFormatter",
    
    # Utilities
    "RateLimiter",
    "MessageDeduplicator",
    
    # High-level functions
    "quick_setup",
    "create_monitor"
]

# Global state
_global_channel_manager = None
_global_error_handler = None


def quick_setup(config_file: str = None, **kwargs) -> tuple:
    """
    Quick setup for error monitoring with automatic configuration detection
    
    Args:
        config_file: Optional path to configuration file
        **kwargs: Override configuration values
    
    Returns:
        tuple: (channel_manager, error_handler) - The main monitoring components
    
    Example:
        >>> manager, handler = quick_setup()
        >>> # Monitoring is now active
        
        >>> # With environment-based config
        >>> manager, handler = quick_setup()
        
        >>> # With custom config file
        >>> manager, handler = quick_setup("monitoring.yaml")
    """
    global _global_channel_manager, _global_error_handler
    
    try:
        # Create configuration
        if config_file:
            config = load_config_from_file(config_file)
        else:
            config = create_config_from_env()
        
        # Apply any overrides
        if kwargs:
            for key, value in kwargs.items():
                config.set_config(key, value)
        
        # Validate configuration
        errors = config.validate_config()
        if errors:
            print("� Configuration validation warnings:")
            for channel, channel_errors in errors.items():
                for error in channel_errors:
                    print(f"  - {channel}: {error}")
        
        # Create channel manager
        _global_channel_manager = ChannelManager(config)
        
        # Initialize error handler
        error_config = config.get_global_error_config()
        app_config = config.get_app_config()
        error_config.update(app_config)
        
        _global_error_handler = initialize_error_handler(error_config, _global_channel_manager)
        
        # Setup monitoring
        setup_monitoring(_global_channel_manager)
        
        print(f"=� Errica v{__version__} initialized")
        print(f"   =� Active channels: {', '.join(_global_channel_manager.enabled_channels)}")
        
        return _global_channel_manager, _global_error_handler
        
    except Exception as e:
        print(f"L Failed to setup Errica: {e}")
        raise


def create_monitor(config: ErricaConfig = None) -> tuple:
    """
    Create a new monitor instance with explicit configuration
    
    Args:
        config: ErricaConfig instance
    
    Returns:
        tuple: (channel_manager, error_handler)
    """
    if config is None:
        config = create_default_config()
    
    # Create channel manager
    channel_manager = ChannelManager(config)
    
    # Initialize error handler
    error_config = config.get_global_error_config()
    app_config = config.get_app_config()
    error_config.update(app_config)
    
    error_handler = initialize_error_handler(error_config, channel_manager)
    
    return channel_manager, error_handler


def get_global_manager() -> ChannelManager:
    """Get the global channel manager instance"""
    global _global_channel_manager
    return _global_channel_manager


def get_global_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    return _global_error_handler


def set_global_manager(manager: ChannelManager):
    """Set the global channel manager instance"""
    global _global_channel_manager
    _global_channel_manager = manager


def shutdown_monitoring():
    """Shutdown global monitoring"""
    global _global_channel_manager, _global_error_handler
    
    if _global_channel_manager:
        _global_channel_manager.shutdown()
        _global_channel_manager = None
    
    if _global_error_handler:
        _global_error_handler.disable()
        _global_error_handler = None
    
    print("=� Errica shutdown complete")


# Package-level convenience functions for backward compatibility and ease of use

def log_error(message: str, exception: Exception = None, context: dict = None, 
              level: str = "ERROR", channels: list = None):
    """
    Log an error message to configured channels
    
    Args:
        message: Error message
        exception: Optional exception object
        context: Additional context information
        level: Error level (ERROR, WARNING, INFO, etc.)
        channels: Specific channels to send to (if None, uses routing config)
    """
    if _global_channel_manager:
        if exception:
            from datetime import datetime
            app_config = _global_channel_manager.config.get_app_config()
            data = MessageData(
                level=level,
                message=message,
                timestamp=datetime.now(),
                app_name=app_config.get("name", "Unknown App"),
                app_version=app_config.get("version", "1.0.0"),
                environment=app_config.get("environment", "production"),
                exception=exception,
                context=context
            )
            _global_channel_manager.send_error(data, channels)
        else:
            _global_channel_manager.send_custom_message(message, level, context, channels)
    else:
        print(f"� No global manager available. {level}: {message}")


def log_info(message: str, context: dict = None, channels: list = None):
    """Log an info message"""
    log_error(message, None, context, "INFO", channels)


def log_warning(message: str, context: dict = None, channels: list = None):
    """Log a warning message"""
    log_error(message, None, context, "WARNING", channels)


def log_critical(message: str, exception: Exception = None, context: dict = None, channels: list = None):
    """Log a critical error message"""
    log_error(message, exception, context, "CRITICAL", channels)


def send_alert(message: str, severity: str = "INFO", context: dict = None, channels: list = None):
    """Send a custom alert (alias for log_error)"""
    log_error(message, None, context, severity, channels)


def health_check() -> dict:
    """Run health checks on all channels"""
    if _global_channel_manager:
        return _global_channel_manager.health_check_all()
    return {"error": "No global channel manager available"}


def get_monitoring_stats() -> dict:
    """Get comprehensive monitoring statistics"""
    stats = {"errica_version": __version__}
    
    if _global_channel_manager:
        stats["channel_manager"] = _global_channel_manager.get_stats()
    
    if _global_error_handler:
        stats["error_handler"] = _global_error_handler.get_stats()
    
    # Add monitoring stats
    monitoring_stats = ErricaMonitoring.get_stats()
    stats["monitoring"] = monitoring_stats
    
    return stats


# Version information
def get_version():
    """Get package version"""
    return __version__


# Initialize package
# Package loaded silently