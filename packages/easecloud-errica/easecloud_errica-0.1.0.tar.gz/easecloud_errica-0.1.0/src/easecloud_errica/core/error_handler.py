"""
Core error handler for comprehensive exception capture and notification
"""

import sys
import traceback
import threading
import asyncio
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from ..formatters import MessageData


class ErrorHandler:
    """Comprehensive error handler for unhandled exceptions"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, config: Dict[str, Any], channel_manager=None):
        if ErrorHandler._instance is not None:
            raise RuntimeError("ErrorHandler is a singleton")
        
        self.config = config
        self.channel_manager = channel_manager
        self.enabled = config.get("enabled", True)
        
        # Configuration
        self.capture_unhandled = config.get("capture_unhandled_exceptions", True)
        self.capture_asyncio = config.get("capture_asyncio_exceptions", True)
        self.capture_threading = config.get("capture_threading_exceptions", True)
        self.auto_send_notifications = config.get("auto_send_notifications", True)
        
        # App information
        self.app_name = config.get("app_name", "Unknown App")
        self.app_version = config.get("app_version", "1.0.0")
        self.environment = config.get("environment", "production")
        
        # Store original handlers
        self.original_excepthook = sys.excepthook
        self.original_threading_excepthook = getattr(threading, 'excepthook', None)
        
        # Error tracking
        self.error_count = 0
        self.current_context = {}
        
        # Install exception hooks
        self._install_handlers()
        
        ErrorHandler._instance = self
    
    @classmethod
    def get_instance(cls, **kwargs):
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance
    
    def _install_handlers(self):
        """Install global exception handlers"""
        if not self.enabled:
            return
            
        if self.capture_unhandled:
            sys.excepthook = self._handle_exception
            
        if self.capture_threading and hasattr(threading, 'excepthook'):
            threading.excepthook = self._handle_threading_exception
            
        if self.capture_asyncio:
            self._install_asyncio_handler()
    
    def _install_asyncio_handler(self):
        """Install asyncio exception handler"""
        try:
            loop = asyncio.get_running_loop()
            loop.set_exception_handler(self._handle_asyncio_exception)
        except RuntimeError:
            # No running loop, will install when loop starts
            pass
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Handle unhandled exceptions"""
        if not self.enabled:
            self.original_excepthook(exc_type, exc_value, exc_traceback)
            return
            
        try:
            self.error_count += 1
            
            # Create MessageData
            data = self._create_message_data(
                level="CRITICAL",
                message=f"Unhandled Exception: {exc_type.__name__}: {str(exc_value)}",
                exception=exc_value,
                source="unhandled_exception"
            )
            
            # Send notification if enabled
            if self.auto_send_notifications and self.channel_manager:
                self.channel_manager.send_error(data)
            else:
                print(f"🚨 Unhandled Exception: {exc_type.__name__}: {str(exc_value)}")
            
        except Exception as handler_error:
            print(f"Error in global error handler: {handler_error}")
        
        # Call original excepthook
        self.original_excepthook(exc_type, exc_value, exc_traceback)
    
    def _handle_threading_exception(self, args):
        """Handle threading exceptions"""
        if not self.enabled:
            if self.original_threading_excepthook:
                self.original_threading_excepthook(args)
            return
            
        try:
            self.error_count += 1
            
            thread_name = args.thread.name if args.thread else "Unknown"
            exc_type = args.exc_type.__name__ if args.exc_type else "Unknown"
            exc_message = str(args.exc_value) if args.exc_value else "Unknown"
            
            # Create MessageData
            data = self._create_message_data(
                level="ERROR",
                message=f"Threading Exception in {thread_name}: {exc_type}: {exc_message}",
                exception=args.exc_value,
                source="threading_exception",
                context={"thread_name": thread_name}
            )
            
            # Send notification if enabled
            if self.auto_send_notifications and self.channel_manager:
                self.channel_manager.send_error(data)
            else:
                print(f"🧵 Threading Error: {exc_type}: {exc_message}")
            
        except Exception as handler_error:
            print(f"Error in threading error handler: {handler_error}")
        
        # Call original handler if it exists
        if self.original_threading_excepthook:
            self.original_threading_excepthook(args)
    
    def _handle_asyncio_exception(self, loop, context):
        """Handle asyncio exceptions"""
        if not self.enabled:
            loop.default_exception_handler(context)
            return
            
        try:
            self.error_count += 1
            
            exception = context.get('exception')
            exc_type = type(exception).__name__ if exception else "AsyncioError"
            exc_message = str(exception) if exception else context.get('message', 'Unknown asyncio error')
            
            # Create MessageData
            data = self._create_message_data(
                level="ERROR",
                message=f"Asyncio Exception: {exc_type}: {exc_message}",
                exception=exception,
                source="asyncio_exception",
                context={"asyncio_context": str(context)}
            )
            
            # Send notification if enabled
            if self.auto_send_notifications and self.channel_manager:
                self.channel_manager.send_error(data)
            else:
                print(f"⚡ Asyncio Error: {exc_type}: {exc_message}")
            
        except Exception as handler_error:
            print(f"Error in asyncio error handler: {handler_error}")
        
        # Call default handler
        loop.default_exception_handler(context)
    
    def capture_manual_exception(self, exception: Exception, context: Optional[Dict] = None, 
                                source: str = "manual", level: str = "ERROR"):
        """Manually capture an exception"""
        try:
            self.error_count += 1
            
            # Create MessageData
            data = self._create_message_data(
                level=level,
                message=f"Manual Exception ({source}): {type(exception).__name__}: {str(exception)}",
                exception=exception,
                source=source,
                context=context
            )
            
            # Send notification if enabled
            if self.auto_send_notifications and self.channel_manager:
                self.channel_manager.send_error(data)
            else:
                print(f"🔥 Manual Exception: {type(exception).__name__}: {str(exception)}")
                    
        except Exception as handler_error:
            print(f"Failed to capture manual exception: {handler_error}")
    
    def capture_custom_message(self, message: str, level: str = "INFO", 
                              context: Optional[Dict] = None, source: str = "custom"):
        """Capture a custom message"""
        try:
            # Create MessageData
            data = self._create_message_data(
                level=level,
                message=message,
                source=source,
                context=context
            )
            
            # Send notification if enabled
            if self.auto_send_notifications and self.channel_manager:
                self.channel_manager.send_message(data)
            else:
                print(f"📢 Custom Message [{level}]: {message}")
                    
        except Exception as handler_error:
            print(f"Failed to capture custom message: {handler_error}")
    
    def _create_message_data(self, level: str, message: str, exception: Optional[Exception] = None,
                           source: str = "unknown", context: Optional[Dict] = None) -> MessageData:
        """Create MessageData object"""
        # Combine current context with provided context
        combined_context = dict(self.current_context)
        if context:
            combined_context.update(context)
        
        # Add source information
        combined_context["source"] = source
        
        # Extract source location from traceback if available
        source_location = {}
        if exception and hasattr(exception, '__traceback__') and exception.__traceback__:
            tb = exception.__traceback__
            while tb.tb_next:
                tb = tb.tb_next
            frame = tb.tb_frame
            source_location = {
                "filename": frame.f_code.co_filename,
                "function": frame.f_code.co_name,
                "line": str(tb.tb_lineno)
            }
        
        return MessageData(
            level=level,
            message=message,
            timestamp=datetime.now(),
            app_name=self.app_name,
            app_version=self.app_version,
            environment=self.environment,
            exception=exception,
            context=combined_context,
            source_location=source_location
        )
    
    def set_context(self, **kwargs):
        """Set context for error reporting"""
        self.current_context = kwargs
    
    def add_context(self, **kwargs):
        """Add to existing context"""
        self.current_context.update(kwargs)
    
    def clear_context(self):
        """Clear current context"""
        self.current_context.clear()
    
    def set_channel_manager(self, channel_manager):
        """Set the channel manager for sending notifications"""
        self.channel_manager = channel_manager
    
    def disable(self):
        """Disable global error handling"""
        self.enabled = False
        
        # Restore original handlers
        sys.excepthook = self.original_excepthook
        if self.original_threading_excepthook and hasattr(threading, 'excepthook'):
            threading.excepthook = self.original_threading_excepthook
    
    def enable(self):
        """Re-enable global error handling"""
        self.enabled = True
        self._install_handlers()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get error handler statistics"""
        return {
            "enabled": self.enabled,
            "error_count": self.error_count,
            "capture_unhandled": self.capture_unhandled,
            "capture_asyncio": self.capture_asyncio,
            "capture_threading": self.capture_threading,
            "auto_send_notifications": self.auto_send_notifications,
            "current_context": dict(self.current_context),
            "app_info": {
                "name": self.app_name,
                "version": self.app_version,
                "environment": self.environment
            }
        }


def initialize_error_handler(config: Dict[str, Any], channel_manager=None) -> Optional[ErrorHandler]:
    """
    Initialize the global error handler
    
    Args:
        config: Error handler configuration
        channel_manager: Channel manager instance for sending notifications
    
    Returns:
        ErrorHandler instance or None if initialization failed
    """
    try:
        handler = ErrorHandler.get_instance(config=config, channel_manager=channel_manager)
        print("🛡️ Global Error Handler initialized - capturing all exceptions")
        return handler
    except Exception as e:
        print(f"Failed to initialize global error handler: {e}")
        return None


def capture_exception(exception: Exception, context: Optional[Dict] = None, 
                     source: str = "manual", level: str = "ERROR"):
    """
    Standalone function to capture exceptions
    
    Args:
        exception: The exception to capture
        context: Additional context information
        source: Source identifier for the exception
        level: Log level for the exception
    """
    handler = ErrorHandler.get_instance()
    if handler:
        handler.capture_manual_exception(exception, context, source, level)
    else:
        print(f"No error handler available. Exception: {exception}")


def capture_message(message: str, level: str = "INFO", context: Optional[Dict] = None, 
                   source: str = "custom"):
    """
    Standalone function to capture custom messages
    
    Args:
        message: The message to capture
        level: Log level
        context: Additional context information
        source: Source identifier
    """
    handler = ErrorHandler.get_instance()
    if handler:
        handler.capture_custom_message(message, level, context, source)
    else:
        print(f"No error handler available. Message: {message}")


def get_error_handler() -> Optional[ErrorHandler]:
    """Get the current error handler instance"""
    return ErrorHandler._instance