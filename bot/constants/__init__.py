"""Constants for the Telegram bot."""

# Bot commands
COMMANDS = {
    'START': 'start',
    'HELP': 'help',
    'STATUS': 'status',
    'SUBSCRIBE': 'subscribe',
    'UNSUBSCRIBE': 'unsubscribe',
    'LIST_SUBSCRIPTIONS': 'subscriptions',
    'SYSTEM_INFO': 'system',
    'TEST': 'test'
}

# Message templates
MESSAGES = {
    'WELCOME': """
🤖 *Welcome to the Notification Bot!*

This bot can send you automated notifications for:
• Application events and errors
• System monitoring alerts
• Scheduled reminders
• Custom notifications via API

Use /help to see available commands.
""",
    
    'HELP': """
🤖 *Notification Bot Help*

*Available Commands:*
/start - Start the bot and get welcome message
/help - Show this help message
/status - Check bot status
/system - Get system information
/subscribe <type> - Subscribe to notification type
/unsubscribe <type> - Unsubscribe from notification type
/subscriptions - List your subscriptions
/test - Send a test notification

*Notification Types:*
• `system` - System monitoring alerts
• `errors` - Application error notifications
• `events` - General application events
• `scheduled` - Scheduled notifications

*Examples:*
`/subscribe system` - Subscribe to system alerts
`/unsubscribe errors` - Unsubscribe from error notifications

For API usage, visit: /docs
""",
    
    'STATUS_OK': """
✅ *Bot Status: Online*

• Bot is running normally
• All services operational
• Ready to send notifications

🕒 Last checked: {timestamp}
""",
    
    'STATUS_ERROR': """
❌ *Bot Status: Error*

• Some services may be unavailable
• Check logs for details

🕒 Last checked: {timestamp}
""",
    
    'SUBSCRIPTION_SUCCESS': """
✅ *Subscription Updated*

You are now subscribed to: `{subscription_type}`

Use /subscriptions to see all your subscriptions.
""",
    
    'UNSUBSCRIPTION_SUCCESS': """
✅ *Unsubscription Updated*

You are no longer subscribed to: `{subscription_type}`

Use /subscriptions to see your remaining subscriptions.
""",
    
    'SUBSCRIPTIONS_LIST': """
📋 *Your Subscriptions*

{subscriptions}

Use /subscribe <type> to add more subscriptions.
Use /unsubscribe <type> to remove subscriptions.
""",
    
    'NO_SUBSCRIPTIONS': """
📋 *Your Subscriptions*

You have no active subscriptions.

Use /subscribe <type> to start receiving notifications.
Available types: system, errors, events, scheduled
""",
    
    'INVALID_SUBSCRIPTION_TYPE': """
❌ *Invalid Subscription Type*

Available types:
• `system` - System monitoring alerts
• `errors` - Application error notifications  
• `events` - General application events
• `scheduled` - Scheduled notifications

Example: `/subscribe system`
""",
    
    'TEST_NOTIFICATION': """
🧪 *Test Notification*

This is a test message to verify that notifications are working correctly.

If you received this message, the bot is functioning properly!

🕒 {timestamp}
""",
    
    'UNAUTHORIZED': """
🚫 *Unauthorized Access*

You are not authorized to use this bot.

Contact the administrator for access.
""",
    
    'ERROR_GENERIC': """
❌ *An error occurred*

Please try again later or contact the administrator.

Error ID: {error_id}
""",
    
    'COMMAND_NOT_FOUND': """
❓ *Unknown Command*

I didn't understand that command. Use /help to see available commands.
""",
    
    'RATE_LIMITED': """
⏰ *Rate Limited*

You're sending commands too quickly. Please wait a moment and try again.
""",
    
    'MAINTENANCE_MODE': """
🔧 *Maintenance Mode*

The bot is currently under maintenance. Please try again later.
"""
}

# Subscription types
SUBSCRIPTION_TYPES = {
    'SYSTEM': 'system',
    'ERRORS': 'errors', 
    'EVENTS': 'events',
    'SCHEDULED': 'scheduled'
}

# Log levels
LOG_LEVELS = {
    'DEBUG': 'DEBUG',
    'INFO': 'INFO',
    'WARNING': 'WARNING',
    'ERROR': 'ERROR',
    'CRITICAL': 'CRITICAL'
}

# Emojis for different message types
EMOJIS = {
    'INFO': 'ℹ️',
    'SUCCESS': '✅',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🚨',
    'DEBUG': '🔍',
    'SYSTEM': '🖥️',
    'NETWORK': '🌐',
    'DATABASE': '🗄️',
    'FILE': '📄',
    'CLOCK': '🕒',
    'ROBOT': '🤖',
    'BELL': '🔔',
    'MUTE': '🔕',
    'KEY': '🔑',
    'LOCK': '🔒',
    'UNLOCK': '🔓',
    'GEAR': '⚙️',
    'CHART': '📊',
    'FIRE': '🔥',
    'LIGHTNING': '⚡',
    'HEART': '❤️',
    'THUMBS_UP': '👍',
    'THUMBS_DOWN': '👎'
}

# API response codes
API_RESPONSES = {
    'SUCCESS': {'code': 200, 'message': 'Success'},
    'CREATED': {'code': 201, 'message': 'Created'},
    'BAD_REQUEST': {'code': 400, 'message': 'Bad Request'},
    'UNAUTHORIZED': {'code': 401, 'message': 'Unauthorized'},
    'FORBIDDEN': {'code': 403, 'message': 'Forbidden'},
    'NOT_FOUND': {'code': 404, 'message': 'Not Found'},
    'RATE_LIMITED': {'code': 429, 'message': 'Too Many Requests'},
    'INTERNAL_ERROR': {'code': 500, 'message': 'Internal Server Error'},
    'SERVICE_UNAVAILABLE': {'code': 503, 'message': 'Service Unavailable'}
}

# File upload limits
FILE_LIMITS = {
    'MAX_PHOTO_SIZE': 10 * 1024 * 1024,  # 10MB
    'MAX_DOCUMENT_SIZE': 50 * 1024 * 1024,  # 50MB
    'MAX_VIDEO_SIZE': 50 * 1024 * 1024,  # 50MB
    'MAX_AUDIO_SIZE': 50 * 1024 * 1024,  # 50MB
    'ALLOWED_PHOTO_TYPES': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'ALLOWED_DOCUMENT_TYPES': ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.zip'],
    'ALLOWED_VIDEO_TYPES': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
    'ALLOWED_AUDIO_TYPES': ['.mp3', '.wav', '.ogg', '.m4a']
}

# Rate limiting
RATE_LIMITS = {
    'MESSAGES_PER_MINUTE': 20,
    'COMMANDS_PER_MINUTE': 10,
    'API_CALLS_PER_MINUTE': 60,
    'WEBHOOK_CALLS_PER_MINUTE': 100
}

# Monitoring thresholds (default values)
MONITORING_THRESHOLDS = {
    'CPU_WARNING': 70.0,
    'CPU_CRITICAL': 90.0,
    'MEMORY_WARNING': 80.0,
    'MEMORY_CRITICAL': 95.0,
    'DISK_WARNING': 85.0,
    'DISK_CRITICAL': 95.0,
    'LOAD_WARNING': 2.0,
    'LOAD_CRITICAL': 5.0
}

# Retry settings
RETRY_SETTINGS = {
    'MAX_ATTEMPTS': 3,
    'INITIAL_DELAY': 1.0,
    'EXPONENTIAL_BASE': 2.0,
    'MAX_DELAY': 60.0
}

# Database table names
DB_TABLES = {
    'USERS': 'users',
    'SUBSCRIPTIONS': 'subscriptions',
    'MESSAGES': 'messages',
    'SCHEDULES': 'schedules',
    'LOGS': 'logs'
}

# Timezone settings
TIMEZONE_SETTINGS = {
    'DEFAULT': 'UTC',
    'COMMON_TIMEZONES': [
        'UTC',
        'US/Eastern',
        'US/Central', 
        'US/Mountain',
        'US/Pacific',
        'Europe/London',
        'Europe/Berlin',
        'Europe/Paris',
        'Asia/Tokyo',
        'Asia/Shanghai',
        'Asia/Kolkata',
        'Australia/Sydney'
    ]
}
