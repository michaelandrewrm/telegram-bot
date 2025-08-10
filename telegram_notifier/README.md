# Telegram Notifier Package

A simple and powerful Python package for sending Telegram notifications from any Python application.

## Quick Start

### Installation

```bash
# Install from local development
cd /path/to/telegram-bot
pip install .

# Or install in development mode
pip install -e .
```

### Basic Usage

```python
from telegram_notifier import TelegramNotifier, send_notification_sync

# Option 1: Using the class (recommended for async applications)
notifier = TelegramNotifier(
    bot_token="your_bot_token",
    default_chat_ids=["chat_id1", "chat_id2"]
)

# Send async notification
await notifier.send("Hello from Python!")

# Send file
await notifier.send_file("/path/to/file.pdf", caption="Report attached")

# Test connection
is_connected = await notifier.test_connection()

# Option 2: Using the sync function (for simple scripts)
success = send_notification_sync("Quick notification!")
```

### Environment Configuration

Create a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_IDS=chat_id1,chat_id2,chat_id3
```

Or set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_IDS="chat_id1,chat_id2"
```

## Features

- **Simple API**: Easy-to-use functions for quick notifications
- **Async Support**: Full async/await support for modern applications
- **File Attachments**: Send documents, images, and other files
- **Multiple Recipients**: Send to multiple chat IDs at once
- **Error Handling**: Robust error handling with detailed logging
- **Configuration**: Flexible configuration via environment variables or direct parameters
- **Framework Integration**: Ready-to-use examples for Django, Flask, FastAPI, and Celery

## API Reference

### TelegramNotifier Class

```python
class TelegramNotifier:
    def __init__(self, bot_token: str = None, default_chat_ids: List[str] = None)
    
    async def send(self, message: str, chat_id: str = None) -> bool
    async def send_file(self, file_path: str, caption: str = "", chat_id: str = None) -> bool
    async def test_connection(self) -> bool
```

### Convenience Functions

```python
def send_notification_sync(message: str, chat_id: str = None) -> bool
```

## Integration Examples

### Django
```python
# views.py
from telegram_notifier import send_notification_sync

def create_user(request):
    # Your user creation logic
    send_notification_sync(f"New user registered: {user.email}")
    return JsonResponse({"status": "success"})
```

### Flask
```python
# app.py
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

@app.route('/api/orders', methods=['POST'])
async def create_order():
    # Process order
    await notifier.send(f"New order: ${order.total}")
    return {"status": "created"}
```

### FastAPI
```python
# main.py
from telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

@app.post("/users/")
async def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    # Create user logic
    background_tasks.add_task(
        notifier.send, 
        f"New user: {user.email}"
    )
    return user
```

### Celery
```python
# tasks.py
from telegram_notifier import send_notification_sync

@app.task
def process_data(data):
    try:
        # Process data
        send_notification_sync("Data processing completed")
    except Exception as e:
        send_notification_sync(f"Data processing failed: {e}")
```

## Error Handling

The package includes comprehensive error handling:

```python
import logging

# Enable logging to see notification status
logging.basicConfig(level=logging.INFO)

# The functions return True/False for success/failure
success = await notifier.send("Test message")
if not success:
    print("Failed to send notification")

# Or use try/catch for detailed error handling
try:
    await notifier.send("Test message")
except Exception as e:
    print(f"Notification error: {e}")
```

## Configuration Options

### Environment Variables
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather
- `TELEGRAM_CHAT_IDS`: Comma-separated list of chat IDs

### Direct Configuration
```python
notifier = TelegramNotifier(
    bot_token="your_token",
    default_chat_ids=["123456789", "-987654321"]
)
```

### Getting Chat IDs
1. Start a chat with your bot
2. Send a message to the bot
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Look for the `chat.id` field in the response

## Advanced Usage

### Multiple Chat Groups
```python
# Send to specific chat
await notifier.send("Admin message", chat_id="admin_chat_id")

# Send to all default chats
await notifier.send("General announcement")
```

### File Attachments
```python
# Send document
await notifier.send_file("/path/to/report.pdf", "Monthly report")

# Send image
await notifier.send_file("/path/to/chart.png", "Sales chart")
```

### Health Monitoring
```python
# Check bot connection
if await notifier.test_connection():
    print("Bot is connected and working")
else:
    print("Bot connection failed")
```

## Troubleshooting

### Common Issues

1. **Bot Token Invalid**
   - Verify token from @BotFather
   - Check environment variable name

2. **Chat ID Not Found**
   - Ensure bot is added to the chat/channel
   - Verify chat ID format (use getUpdates to confirm)

3. **Import Errors**
   - Ensure package is installed: `pip list | grep telegram-notifier`
   - Try reinstalling: `pip install --force-reinstall .`

4. **Async Errors**
   - Use `send_notification_sync()` for non-async code
   - Ensure proper `await` usage in async functions

### Debug Mode
```python
import logging
logging.getLogger('telegram_notifier').setLevel(logging.DEBUG)

# This will show detailed request/response information
await notifier.send("Debug test")
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the integration examples in `examples/integrations/`
2. Review the troubleshooting section
3. Create an issue on GitHub with detailed error information
