# Errica by EaseCloud — Your Python error monitor

A comprehensive multi-channel error monitoring and notification system for Python applications. Monitor errors, exceptions, and custom events across multiple notification channels including Telegram, Slack, webhooks, and console output.

## 🚀 Features

- **Multi-Channel Notifications**: Send alerts to Telegram, Slack, webhooks, and console
- **Smart Routing**: Route different error levels to different channels based on environment
- **Global Exception Handling**: Automatically capture unhandled exceptions, asyncio errors, and threading errors
- **Task Monitoring**: Context managers for monitoring tasks and batch operations
- **Rate Limiting**: Prevent spam with configurable rate limits per channel
- **Message Deduplication**: Avoid duplicate notifications within configurable time windows
- **Rich Formatting**: Channel-specific message formatting (Markdown for Telegram/Slack, JSON for webhooks, colored output for console)
- **Health Checks**: Monitor channel health and connectivity
- **Comprehensive Configuration**: YAML configuration with environment variable support

## 📦 Installation

```bash
pip install easecloud-errica
```

### Optional Dependencies

```bash
# For Telegram/Slack/Webhook support (included by default)
pip install easecloud-errica[all]

# For SOCKS proxy support (Telegram)
pip install easecloud-errica[socks]

# For development
pip install easecloud-errica[dev]
```

## 🚀 Quick Start

### Basic Usage

```python
from easecloud_errica import quick_setup, task_monitor, log_error, log_info

# Quick setup with environment variables
manager, handler = quick_setup()

# Log messages
log_info("Application started")
log_error("Something went wrong", exception, {"user_id": 123})

# Monitor tasks
with task_monitor("user_sync"):
    # Your code here
    sync_users()
```

### Environment Variables

Set these environment variables for automatic configuration:

```bash
# App identification
export APP_NAME="My Application"
export APP_VERSION="1.0.0"
export ENVIRONMENT="production"

# Telegram (optional)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

# Slack (optional)
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Generic webhook (optional)
export WEBHOOK_URL="https://your-webhook-endpoint.com/alerts"
```

## 📋 Configuration

### YAML Configuration

Create a `config.yaml` file:

```yaml
app:
  name: "My Application"
  version: "1.0.0"
  environment: "production"

channels:
  telegram:
    enabled: true
    bot_token: "YOUR_BOT_TOKEN"
    chat_id: "YOUR_CHAT_ID"

  slack:
    enabled: true
    webhook_url: "YOUR_SLACK_WEBHOOK"
    channel: "#alerts"

  console:
    enabled: true
    use_colors: true

routing:
  level_routing:
    CRITICAL: ["telegram", "slack"]
    ERROR: ["telegram", "slack"]
    WARNING: ["slack", "console"]
    INFO: ["console"]
```

### Programmatic Configuration

```python
from easecloud_errica import ErricaConfig, create_monitor

config = ErricaConfig()
config.set_config("channels.telegram.enabled", True)
config.set_config("channels.telegram.bot_token", "your_token")

manager, handler = create_monitor(config)
```

## 📡 Supported Channels

### Telegram

- Rich message formatting with Markdown
- File attachments for large error reports
- Proxy support for restricted networks
- Rate limiting and deduplication

### Slack

- Rich message blocks and attachments
- Thread support for related errors
- Custom emoji and mentions
- Color-coded severity levels

### Webhook

- Generic HTTP webhook support
- JSON or form-encoded payloads
- Custom headers and authentication
- Configurable retry logic

### Console

- Colored terminal output
- Detailed exception formatting
- Progress indicators
- Structured logging format

## 🔧 Advanced Usage

### Custom Error Routing

```python
from easecloud_errica import create_config_from_env, create_monitor

config = create_config_from_env()

# Route critical errors to all channels
config.set_config("routing.level_routing.CRITICAL",
                 ["telegram", "slack", "console"])

# Route errors differently per environment
config.set_config("routing.environment_routing.production.ERROR",
                 ["telegram"])
config.set_config("routing.environment_routing.development.ERROR",
                 ["console"])

manager, handler = create_monitor(config)
```

### Task and Batch Monitoring

```python
from easecloud_errica import task_monitor, batch_monitor

# Monitor individual tasks
with task_monitor("user_registration", category="auth"):
    register_user(user_data)

# Monitor batch operations
with batch_monitor("notification_batch", category="notifications", batch_size=100):
    send_notifications(notification_list)

# Decorators for functions
from easecloud_errica import monitor_function, monitor_async_function

@monitor_function
def process_data(data):
    return transform(data)

@monitor_async_function
async def fetch_data():
    return await api_call()
```

### Manual Error Capture

```python
from easecloud_errica import log_error, send_alert, capture_exception

# Log errors with context
log_error("Payment processing failed", exception, {
    "user_id": 123,
    "payment_amount": 99.99,
    "payment_method": "credit_card"
})

# Send custom alerts
send_alert("High CPU usage detected", "WARNING", {
    "cpu_usage": "85%",
    "threshold": "80%"
})

# Capture exceptions with custom context
try:
    risky_operation()
except Exception as e:
    capture_exception(e, {"operation": "data_sync"}, "manual")
```

### Health Monitoring

```python
from easecloud_errica import health_check, get_monitoring_stats

# Check channel health
results = health_check()
for channel, result in results.items():
    if not result.success:
        print(f"❌ {channel}: {result.message}")

# Get comprehensive statistics
stats = get_monitoring_stats()
print(f"Messages sent: {stats['channel_manager']['messages_sent']}")
print(f"Errors captured: {stats['error_handler']['error_count']}")
```

## 🔍 Examples

See the `examples/` directory for comprehensive examples:

- `basic_usage.py` - Simple setup and usage
- `advanced_usage.py` - Advanced configuration and features
- `multi_channel_demo.py` - Multi-channel demonstration
- `config_example.yaml` - Complete configuration reference

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=easecloud_errica

# Run specific test types
pytest -m unit
pytest -m integration
```

## 📚 Documentation

- [Development Guide](docs/development.md) - Setup, testing, and contributing
- [GitHub Actions Workflows](docs/workflows.md) - CI/CD and automated publishing
- [Configuration Reference](docs/configuration.md)
- [Channel Setup Guides](docs/channels/)
- [API Documentation](docs/api.md)

## 🚀 CI/CD & Publishing

Errica uses automated GitHub Actions workflows for testing and publishing:

- **Automated Testing**: Multi-platform testing on every PR and push
- **Automated Publishing**:
  - `main` branch → Dev releases to Test PyPI (`0.1.0-dev.123+sha`)
  - `release/**` branches → Beta releases to Test PyPI (`0.1.0-beta.1`)
  - GitHub releases → Stable releases to PyPI (`1.0.0`)
- **Manual Releases**: Use GitHub Actions to create properly versioned releases

**Quick Release:**

1. Go to Actions → "Create Release"
2. Enter version (e.g., `1.0.0`)
3. Workflow handles version updates, tagging, and PyPI publishing

See [Workflows Documentation](docs/workflows.md) for complete details.

## 🤝 Contributing

Contributions are welcome! Please read our [Development Guide](docs/development.md) for setup instructions and [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/easecloudio/easecloud-errica)
- [PyPI Package](https://pypi.org/project/easecloud-errica/)
- [Documentation](https://easecloud-errica.readthedocs.io/)
- [Issue Tracker](https://github.com/easecloudio/easecloud-errica/issues)

## 🎯 Roadmap

- [ ] Email channel implementation
- [ ] Database logging channel
- [ ] Metrics integration (Prometheus, StatsD)
- [ ] Web dashboard for monitoring
- [ ] Custom channel plugin system
- [ ] Advanced filtering and correlation
- [ ] Integration with popular frameworks (Django, Flask, FastAPI)
