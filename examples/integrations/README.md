# Integration Examples

This directory contains practical examples of integrating the Telegram Bot notification system into different Python frameworks and applications.

## Available Examples

### 1. Django Integration (`django_example.py`)
Complete Django integration with:
- Custom middleware for error notifications
- Management commands for batch operations
- Views with notification support
- Model signals for data changes
- Admin integration

**Setup:**
```bash
pip install django
python manage.py migrate
python manage.py runserver
```

### 2. Flask Integration (`flask_example.py`)
Flask application with:
- Error handlers with notifications
- Background task support
- Request logging
- API endpoints with notifications
- Custom decorators

**Setup:**
```bash
pip install flask
python flask_example.py
```

### 3. FastAPI Integration (`fastapi_example.py`)
Modern async FastAPI integration:
- Async notification support
- Background tasks
- Exception handlers
- WebSocket notifications
- Automatic API documentation

**Setup:**
```bash
pip install fastapi uvicorn
uvicorn fastapi_example:app --reload
```

### 4. Celery Integration (`celery_example.py`)
Celery task queue integration:
- Task success/failure notifications
- Progress notifications for long tasks
- Worker monitoring
- Periodic task notifications
- Retry handling

**Setup:**
```bash
pip install celery redis
celery -A celery_example worker --loglevel=info
celery -A celery_example beat --loglevel=info
```

## Common Setup

All examples require the telegram-bot notification package:

```bash
# Install from local development
cd /path/to/telegram-bot
pip install .

# Or install in development mode
pip install -e .
```

Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_IDS="chat_id1,chat_id2"
```

## Quick Start

1. Choose the framework example that matches your application
2. Install the required dependencies
3. Copy the relevant code into your project
4. Configure your Telegram bot token and chat IDs
5. Customize the notification logic for your needs

## Customization

Each example includes:
- Error handling and notifications
- Success notifications for important events
- Progress notifications for long-running operations
- Health check integrations
- Background task support

Modify the notification logic, message formats, and trigger conditions to match your application's requirements.

## Testing

Each example includes test endpoints and commands to verify the integration:
- Manual notification endpoints
- Error simulation endpoints
- Health check endpoints
- Background task triggers

## Production Considerations

- Use environment variables for sensitive configuration
- Implement rate limiting for notifications
- Consider using background tasks for non-critical notifications
- Set up proper logging and monitoring
- Test notification delivery in staging environments
