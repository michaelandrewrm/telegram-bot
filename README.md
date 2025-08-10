# Telegram Notification Bot

A comprehensive Python-based Telegram bot for automated notifications, monitoring alerts, and event-driven messaging. This bot can be integrated into applications, CI/CD pipelines, monitoring systems, and used for scheduled notifications.

## 🚀 Features

### Core Notification Features
- ✅ Send text notifications to individual chats or groups
- ✅ Support for media files (images, documents, videos)
- ✅ Markdown and HTML formatting support
- ✅ Simple `send_notification()` function for easy integration
- ✅ Bulk messaging to multiple chats

### Event-Driven Capabilities
- ✅ Application event integration
- ✅ Webhook endpoint for external triggers
- ✅ CLI commands for manual notifications
- ✅ REST API for HTTP-based notifications

### Scheduling & Automation
- ✅ Cron-based scheduled notifications
- ✅ Interval-based recurring messages
- ✅ One-time scheduled notifications
- ✅ Daily/weekly system reports

### System Monitoring
- ✅ CPU, memory, and disk usage alerts
- ✅ Configurable thresholds
- ✅ Real-time system information
- ✅ Automated monitoring alerts

### User Management
- ✅ Subscription management (/subscribe, /unsubscribe)
- ✅ User authorization and access control
- ✅ Subscription types (system, errors, events, scheduled)

### Security & Reliability
- ✅ Environment-based configuration
- ✅ Webhook token validation
- ✅ Rate limiting and retry logic
- ✅ Comprehensive error handling and logging

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/telegram-bot.git
cd telegram-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

4. **Get your Bot Token:**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Create a new bot with `/newbot`
   - Copy the token to your `.env` file

5. **Get your Chat ID:**
   - Message your bot
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token_here
DEFAULT_CHAT_IDS=123456789,987654321

# Optional
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret
API_HOST=0.0.0.0
API_PORT=8080
API_SECRET_KEY=your_api_secret_key
LOG_LEVEL=INFO
LOG_FILE=bot.log

# Monitoring Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=90
```

### YAML Configuration (config.yaml)

```yaml
bot:
  name: "Notification Bot"
  webhook_url: null
  polling_interval: 1

notifications:
  default_parse_mode: "Markdown"
  retry_attempts: 3
  retry_delay: 1

features:
  enable_subscriptions: true
  enable_file_uploads: true
  enable_scheduling: true
  enable_monitoring: true
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from bot import send_notification

# Simple notification
await send_notification("Hello from your bot! 👋")

# Notification to specific chat
await send_notification("Private message", chat_id="123456789")

# Formatted notification
message = """
🚀 *Deployment Complete*

**Version:** v2.1.0
**Status:** ✅ Success
**Duration:** 3m 45s
"""
await send_notification(message, parse_mode="Markdown")
```

### 2. Run the Bot

```bash
# Start with polling (recommended for development)
python -m bot.main

# Or use the CLI
python -m bot.cli run

# Start API server
python -m bot.cli api --host 0.0.0.0 --port 8080
```

### 3. Send via CLI

```bash
# Simple message
python -m bot.cli send "Hello from CLI!"

# Message to specific chat
python -m bot.cli send "Private message" --chat-id 123456789

# Send file
python -m bot.cli send "Check this out" --file ./image.jpg

# System information
python -m bot.cli system
```

## 📖 Usage Examples

### Application Integration

```python
import asyncio
from bot import send_notification

async def on_user_registration(user_email):
    """Send notification when user registers."""
    await send_notification(
        f"📝 New user registered: {user_email}",
        chat_id="123456789"
    )

async def on_error(error_message):
    """Send error notifications."""
    message = f"""
❌ *Application Error*

**Error:** {error_message}
**Time:** {datetime.now()}
**Severity:** High

Please investigate immediately.
"""
    await send_notification(message, parse_mode="Markdown")

# Usage
asyncio.run(on_user_registration("user@example.com"))
```

### Webhook Integration

```bash
# Send notification via webhook
curl -X POST http://localhost:8080/webhook/notify \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Token: your_webhook_token" \
  -d '{
    "message": "CI/CD pipeline completed successfully!",
    "level": "INFO",
    "source": "GitHub Actions"
  }'
```

### REST API Usage

```python
import requests

# Send notification via API
response = requests.post(
    "http://localhost:8080/api/v1/notify",
    headers={
        "Authorization": "Bearer your_api_secret_key",
        "Content-Type": "application/json"
    },
    json={
        "message": "API notification test",
        "chat_id": "123456789",
        "parse_mode": "Markdown"
    }
)
```

### Scheduling Notifications

```python
from bot.services.scheduler import scheduler_service

# Daily report at 9 AM
await scheduler_service.schedule_notification(
    job_id="daily_report",
    message="📊 Daily system report",
    chat_ids=["123456789"],
    trigger_type="cron",
    hour=9,
    minute=0
)

# One-time notification
from datetime import datetime, timedelta
future_time = datetime.now() + timedelta(hours=2)

await scheduler_service.schedule_notification(
    job_id="reminder",
    message="⏰ Meeting in 10 minutes!",
    chat_ids=["123456789"],
    trigger_type="date",
    run_date=future_time
)
```

## 🤖 Bot Commands

Users can interact with the bot using these commands:

- `/start` - Initialize the bot and get welcome message
- `/help` - Show available commands and usage
- `/status` - Check bot status and connectivity
- `/system` - Get current system information
- `/subscribe <type>` - Subscribe to notification type
- `/unsubscribe <type>` - Unsubscribe from notification type
- `/subscriptions` - List your active subscriptions
- `/test` - Send a test notification

### Subscription Types

- `system` - System monitoring alerts (CPU, memory, disk)
- `errors` - Application error notifications
- `events` - General application events
- `scheduled` - Scheduled notifications and reports

## 🔧 API Reference

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/notify` | Send notification |
| `POST` | `/webhook/notify` | Webhook notifications |
| `GET` | `/api/v1/subscriptions` | Get all subscriptions |
| `GET` | `/api/v1/system/metrics` | Get system metrics |
| `POST` | `/api/v1/system/report` | Send system report |
| `POST` | `/api/v1/schedule` | Schedule notification |
| `DELETE` | `/api/v1/schedule/{job_id}` | Remove scheduled job |
| `GET` | `/api/v1/schedule` | List scheduled jobs |

### CLI Commands

```bash
# Notification commands
python -m bot.cli send "message" [options]
python -m bot.cli system [--chat-id ID]

# Scheduling commands  
python -m bot.cli schedule job_id "message" --chat-ids "ID1,ID2" --cron "0 9 * * *"
python -m bot.cli unschedule job_id
python -m bot.cli jobs

# Management commands
python -m bot.cli status
python -m bot.cli metrics
python -m bot.cli run
python -m bot.cli api [--host HOST] [--port PORT]
```

## 🔍 Monitoring and Alerts

### System Monitoring

The bot automatically monitors system resources and sends alerts when thresholds are exceeded:

```python
# Configure thresholds in .env or config.yaml
CPU_THRESHOLD=80      # Alert when CPU > 80%
MEMORY_THRESHOLD=80   # Alert when memory > 80%  
DISK_THRESHOLD=90     # Alert when disk > 90%
```

### Custom Monitoring

```python
from bot.services.monitoring import monitoring_service

# Get current metrics
metrics = await monitoring_service.get_current_metrics()
print(f"CPU: {metrics['cpu_percent']}%")

# Send system report
await monitoring_service.send_system_report()

# Check if process is running
is_running = await monitoring_service.check_process_status("nginx")
```

## 📊 Scheduling

### Cron Expressions

```python
# Daily at 9:00 AM
"0 9 * * *"

# Every weekday at 6:00 PM  
"0 18 * * 1-5"

# Every Monday at 8:00 AM
"0 8 * * 1"

# Every 30 minutes
"*/30 * * * *"
```

### Schedule Types

1. **Cron-based**: Use cron expressions for complex schedules
2. **Interval-based**: Repeat every X seconds/minutes/hours
3. **One-time**: Schedule for specific date/time

## 🛡️ Security

### Best Practices

1. **Environment Variables**: Store sensitive data in `.env` files
2. **Webhook Security**: Use secure tokens for webhook validation
3. **API Authentication**: Protect API endpoints with secret keys
4. **User Authorization**: Configure allowed users in settings
5. **Rate Limiting**: Built-in protection against spam

### Configuration

```yaml
security:
  require_webhook_auth: true
  allowed_users: [123456789, 987654321]  # Empty = allow all
  rate_limit: 10  # requests per minute per user
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check bot token in `.env` file
   - Verify internet connectivity
   - Check logs for errors

2. **Notifications not sending**
   - Verify chat IDs are correct
   - Check user has started the bot
   - Review error logs

3. **Webhook not working**
   - Confirm webhook URL is accessible
   - Verify webhook secret token
   - Check firewall settings

4. **Scheduling issues**
   - Validate cron expressions
   - Check timezone settings
   - Ensure scheduler service is running

### Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check bot status
python -m bot.cli status

# Test connectivity
python -m bot.cli send "Test message" --chat-id YOUR_CHAT_ID

# View logs
tail -f bot.log
```

## 📝 Development

### Project Structure

```
telegram-bot/
├── bot/                 # Main package
│   ├── __init__.py
│   ├── main.py          # Bot entry point
│   ├── api.py           # FastAPI application
│   ├── cli.py           # CLI interface
│   ├── config/          # Configuration management
│   ├── handlers/        # Command handlers
│   ├── services/        # Core services
│   ├── utils/           # Utilities
│   ├── constants/       # Constants and messages
│   └── middlewares/     # Custom middlewares
├── examples/            # Usage examples
├── tests/              # Unit tests
├── .env.example        # Example environment file
├── config.yaml         # Configuration file
├── requirements.txt    # Dependencies
└── README.md          # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with coverage
pytest --cov=bot tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: This README and code comments
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions

## 🚀 Roadmap

- [ ] Database integration for persistent storage
- [ ] Web dashboard for management
- [ ] Message templates and variables
- [ ] File attachment support in webhooks
- [ ] Integration with popular monitoring tools
- [ ] Docker container support
- [ ] Kubernetes deployment manifests
- [ ] Additional notification channels (email, SMS)

---

**Happy coding! 🎉**

For more examples and advanced usage, check the `examples/` directory.
