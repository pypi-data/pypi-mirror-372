"""
Enhanced configuration management for multi-channel error monitoring
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime


class ErricaConfig:
    """Configuration manager for error monitoring with multi-channel support"""
    
    DEFAULT_CONFIG = {
        "app": {
            "name": "Unknown App",
            "version": "1.0.0",
            "environment": "production"
        },
        "channels": {
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "chat_id": "",
                "proxy": {
                    "enabled": False,
                    "type": "http",
                    "host": "",
                    "port": 0,
                    "username": "",
                    "password": ""
                },
                "rate_limiting": {
                    "max_messages_per_minute": 20,
                    "max_messages_per_hour": 100
                },
                "deduplication_window_minutes": 5,
                "send_exceptions_as_files": True,
                "max_message_length": 4000,
                "severity_config": {
                    "CRITICAL": {
                        "emoji": "🚨",
                        "color": "#FF0000",
                        "send_as_file": True,
                        "notify_immediately": True
                    },
                    "ERROR": {
                        "emoji": "❌",
                        "color": "#FF6B6B",
                        "send_as_file": True,
                        "notify_immediately": True
                    },
                    "WARNING": {
                        "emoji": "⚠️",
                        "color": "#FFB74D",
                        "send_as_file": False,
                        "notify_immediately": False
                    },
                    "INFO": {
                        "emoji": "ℹ️",
                        "color": "#4FC3F7",
                        "send_as_file": False,
                        "notify_immediately": False
                    },
                    "DEBUG": {
                        "emoji": "🔍",
                        "color": "#9E9E9E",
                        "send_as_file": False,
                        "notify_immediately": False
                    }
                },
                "environment_emoji": {
                    "production": "🏭",
                    "staging": "🧪",
                    "development": "🛠️",
                    "local": "💻"
                },
                "retry_config": {
                    "max_retries": 3,
                    "base_delay": 1,
                    "max_delay": 30,
                    "exponential_base": 2
                }
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "",
                "username": "Errica",
                "icon_emoji": ":warning:",
                "rate_limiting": {
                    "max_messages_per_minute": 30,
                    "max_messages_per_hour": 200
                },
                "deduplication_window_minutes": 5,
                "thread_errors": True,
                "mention_on_critical": "@channel",
                "severity_config": {
                    "CRITICAL": {
                        "color": "danger",
                        "mention": True,
                        "send_as_file": True
                    },
                    "ERROR": {
                        "color": "warning",
                        "mention": False,
                        "send_as_file": False
                    },
                    "WARNING": {
                        "color": "warning",
                        "mention": False,
                        "send_as_file": False
                    },
                    "INFO": {
                        "color": "good",
                        "mention": False,
                        "send_as_file": False
                    }
                },
                "retry_config": {
                    "max_retries": 3,
                    "base_delay": 1,
                    "max_delay": 30,
                    "exponential_base": 2
                }
            },
            "webhook": {
                "enabled": False,
                "url": "",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "auth": {
                    "type": "none",  # none, basic, bearer, custom
                    "username": "",
                    "password": "",
                    "token": "",
                    "custom_headers": {}
                },
                "payload_format": "json",  # json, form
                "timeout": 30,
                "rate_limiting": {
                    "max_messages_per_minute": 60,
                    "max_messages_per_hour": 1000
                },
                "deduplication_window_minutes": 5,
                "retry_config": {
                    "max_retries": 3,
                    "base_delay": 1,
                    "max_delay": 30,
                    "exponential_base": 2
                }
            },
            "email": {
                "enabled": False,
                "smtp_host": "",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "use_tls": True,
                "from_email": "",
                "to_emails": [],
                "cc_emails": [],
                "subject_template": "[{level}] {app_name} - {message}",
                "rate_limiting": {
                    "max_messages_per_minute": 5,
                    "max_messages_per_hour": 50
                },
                "deduplication_window_minutes": 10,
                "retry_config": {
                    "max_retries": 3,
                    "base_delay": 2,
                    "max_delay": 60,
                    "exponential_base": 2
                }
            },
            "console": {
                "enabled": True,
                "use_colors": True,
                "include_timestamp": True,
                "include_level": True,
                "include_source": True,
                "format": "{timestamp} [{level}] {app_name}: {message}",
                "color_scheme": {
                    "CRITICAL": "red",
                    "ERROR": "red",
                    "WARNING": "yellow",
                    "INFO": "blue",
                    "DEBUG": "gray"
                }
            }
        },
        "global_error_handling": {
            "enabled": True,
            "capture_unhandled_exceptions": True,
            "capture_asyncio_exceptions": True,
            "capture_threading_exceptions": True,
            "auto_send_notifications": True,
            "include_system_info": True,
            "include_environment_vars": False,
            "mask_sensitive_keys": [
                "password", "token", "secret", "key", "auth",
                "api_key", "private", "credential"
            ]
        },
        "routing": {
            "default_channels": ["console"],
            "level_routing": {
                "CRITICAL": ["telegram", "slack", "email"],
                "ERROR": ["telegram", "slack"],
                "WARNING": ["slack", "console"],
                "INFO": ["console"],
                "DEBUG": ["console"]
            },
            "environment_routing": {
                "production": {
                    "CRITICAL": ["telegram", "email"],
                    "ERROR": ["telegram", "slack"],
                    "WARNING": ["slack"],
                    "INFO": ["console"]
                },
                "staging": {
                    "CRITICAL": ["slack", "telegram"],
                    "ERROR": ["slack"],
                    "WARNING": ["slack"],
                    "INFO": ["console"]
                },
                "development": {
                    "ERROR": ["console"],
                    "WARNING": ["console"],
                    "INFO": ["console"]
                }
            }
        }
    }
    
    def __init__(self, config_file: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to YAML configuration file
            config_dict: Configuration dictionary to use directly
        """
        self.config = self._deep_copy(self.DEFAULT_CONFIG)
        
        # Load from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Override with dictionary if provided
        if config_dict:
            self.update_config(config_dict)
        
        # Load from environment variables
        self._load_from_environment()
    
    def _deep_copy(self, obj):
        """Deep copy a dictionary"""
        import copy
        return copy.deepcopy(obj)
    
    def load_from_file(self, config_file: str):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self.update_config(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration with new values"""
        self._deep_update(self.config, new_config)
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Recursively update nested dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # App configuration
        app_name = os.getenv("APP_NAME")
        if app_name:
            self.config["app"]["name"] = app_name
        
        app_version = os.getenv("APP_VERSION")
        if app_version:
            self.config["app"]["version"] = app_version
        
        environment = os.getenv("ENVIRONMENT")
        if environment:
            self.config["app"]["environment"] = environment
        
        # Telegram configuration
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if telegram_token:
            self.config["channels"]["telegram"]["bot_token"] = telegram_token
            self.config["channels"]["telegram"]["enabled"] = True
        
        telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_chat:
            self.config["channels"]["telegram"]["chat_id"] = telegram_chat
        
        # Slack configuration
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            self.config["channels"]["slack"]["webhook_url"] = slack_webhook
            self.config["channels"]["slack"]["enabled"] = True
        
        slack_channel = os.getenv("SLACK_CHANNEL")
        if slack_channel:
            self.config["channels"]["slack"]["channel"] = slack_channel
        
        # Webhook configuration
        webhook_url = os.getenv("WEBHOOK_URL")
        if webhook_url:
            self.config["channels"]["webhook"]["url"] = webhook_url
            self.config["channels"]["webhook"]["enabled"] = True
        
        # Email configuration
        smtp_host = os.getenv("SMTP_HOST")
        if smtp_host:
            self.config["channels"]["email"]["smtp_host"] = smtp_host
            self.config["channels"]["email"]["enabled"] = True
        
        smtp_user = os.getenv("SMTP_USERNAME")
        if smtp_user:
            self.config["channels"]["email"]["smtp_username"] = smtp_user
        
        smtp_pass = os.getenv("SMTP_PASSWORD")
        if smtp_pass:
            self.config["channels"]["email"]["smtp_password"] = smtp_pass
        
        from_email = os.getenv("FROM_EMAIL")
        if from_email:
            self.config["channels"]["email"]["from_email"] = from_email
        
        to_emails = os.getenv("TO_EMAILS")
        if to_emails:
            self.config["channels"]["email"]["to_emails"] = [email.strip() for email in to_emails.split(",")]
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.config.get("app", {})
    
    def get_channel_config(self, channel_name: str) -> Dict[str, Any]:
        """Get configuration for a specific channel"""
        return self.config.get("channels", {}).get(channel_name, {})
    
    def get_enabled_channels(self) -> List[str]:
        """Get list of enabled channels"""
        enabled = []
        channels = self.config.get("channels", {})
        for name, config in channels.items():
            if config.get("enabled", False):
                enabled.append(name)
        return enabled
    
    def get_routing_config(self) -> Dict[str, Any]:
        """Get message routing configuration"""
        return self.config.get("routing", {})
    
    def get_global_error_config(self) -> Dict[str, Any]:
        """Get global error handling configuration"""
        return self.config.get("global_error_handling", {})
    
    def get_channels_for_level(self, level: str, environment: Optional[str] = None) -> List[str]:
        """Get channels that should receive messages for a given level"""
        routing = self.get_routing_config()
        
        # Try environment-specific routing first
        if environment:
            env_routing = routing.get("environment_routing", {}).get(environment, {})
            if level in env_routing:
                return env_routing[level]
        
        # Fall back to level routing
        level_routing = routing.get("level_routing", {})
        if level in level_routing:
            return level_routing[level]
        
        # Fall back to default channels
        return routing.get("default_channels", ["console"])
    
    def set_config(self, key: str, value: Any):
        """Set configuration value by dot-notation key"""
        keys = key.split('.')
        target = self.config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def get_config(self, key: str = None) -> Any:
        """Get configuration value by dot-notation key"""
        if key is None:
            return self.config
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration and return any errors"""
        errors = {}
        
        # Validate enabled channels
        for channel_name in self.get_enabled_channels():
            channel_config = self.get_channel_config(channel_name)
            channel_errors = []
            
            if channel_name == "telegram":
                if not channel_config.get("bot_token"):
                    channel_errors.append("bot_token is required")
                if not channel_config.get("chat_id"):
                    channel_errors.append("chat_id is required")
            
            elif channel_name == "slack":
                if not channel_config.get("webhook_url"):
                    channel_errors.append("webhook_url is required")
            
            elif channel_name == "webhook":
                if not channel_config.get("url"):
                    channel_errors.append("url is required")
            
            elif channel_name == "email":
                if not channel_config.get("smtp_host"):
                    channel_errors.append("smtp_host is required")
                if not channel_config.get("from_email"):
                    channel_errors.append("from_email is required")
                if not channel_config.get("to_emails"):
                    channel_errors.append("to_emails is required")
            
            if channel_errors:
                errors[channel_name] = channel_errors
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self._deep_copy(self.config)
    
    def save_to_file(self, file_path: str):
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)


def create_default_config() -> ErricaConfig:
    """Create configuration with default values"""
    return ErricaConfig()


def create_config_from_env() -> ErricaConfig:
    """Create configuration from environment variables"""
    config = ErricaConfig()
    return config


def load_config_from_file(file_path: str) -> ErricaConfig:
    """Load configuration from file"""
    return ErricaConfig(config_file=file_path)