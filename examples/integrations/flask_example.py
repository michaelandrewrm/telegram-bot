"""
Flask Integration Example
Shows how to integrate Telegram notifications into a Flask application.
"""

# Install the notifier package:
# pip install /path/to/telegram-bot

import os
from flask import Flask, request, jsonify, render_template
from telegram_notifier import TelegramNotifier, send_notification_sync
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure Telegram (you can also use a .env file)
app.config['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN', 'your_token_here')
app.config['TELEGRAM_CHAT_IDS'] = os.getenv('TELEGRAM_CHAT_IDS', 'your_chat_id').split(',')

# Initialize Telegram notifier
notifier = TelegramNotifier(
    bot_token=app.config['TELEGRAM_BOT_TOKEN'],
    default_chat_ids=app.config['TELEGRAM_CHAT_IDS']
)

# Notification helpers
def notify_error(error_msg: str, request_info: dict = None):
    """Send error notification with request context."""
    message = f"🚨 **Flask Error**\\n\\n{error_msg}"
    
    if request_info:
        message += f"""
        
**Request Details:**
• URL: {request_info.get('url', 'Unknown')}
• Method: {request_info.get('method', 'Unknown')}
• IP: {request_info.get('remote_addr', 'Unknown')}
• User Agent: {request_info.get('user_agent', 'Unknown')[:100]}...
"""
    
    message += f"\\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return send_notification_sync(message)

def notify_user_action(action: str, details: str = "", user_info: dict = None):
    """Notify about user actions."""
    message = f"""
👤 **User Action**

**Action:** {action}
**Details:** {details}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if user_info:
        message += f"""
**User Info:**
• IP: {user_info.get('ip', 'Unknown')}
• User Agent: {user_info.get('user_agent', 'Unknown')[:50]}...
"""
    
    return send_notification_sync(message)

def notify_system_event(event: str, details: str = ""):
    """Notify about system events."""
    message = f"""
⚡ **System Event**

**Event:** {event}
**Details:** {details}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return send_notification_sync(message)

# Error handlers
@app.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors and send notification."""
    error_msg = f"Internal Server Error: {str(error)}"
    
    request_info = {
        'url': request.url,
        'method': request.method,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    notify_error(error_msg, request_info)
    
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'The error has been logged and administrators have been notified.'
    }), 500

@app.errorhandler(404)
def handle_not_found(error):
    """Log 404 errors (optional notification)."""
    # Uncomment to get notified of 404s (can be noisy)
    # notify_error(f"404 Not Found: {request.url}")
    
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found.'
    }), 404

# Application startup
@app.before_first_request
def startup_notification():
    """Send notification when app starts."""
    notify_system_event("Flask App Started", "Application is now running")

# Routes with notifications
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create user endpoint with notification."""
    try:
        data = request.get_json()
        
        # Validate data
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        # Your user creation logic here
        # user = create_user_in_database(data)
        
        # Send notification
        user_info = {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
        
        notify_user_action(
            "User Registration",
            f"New user: {data['email']}",
            user_info
        )
        
        return jsonify({
            'message': 'User created successfully',
            'email': data['email']
        }), 201
        
    except Exception as e:
        error_msg = f"Failed to create user: {str(e)}"
        notify_error(error_msg, {
            'url': request.url,
            'method': request.method,
            'remote_addr': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        
        return jsonify({'error': 'Failed to create user'}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create order endpoint with notification."""
    try:
        data = request.get_json()
        
        # Your order processing logic here
        # order = process_order(data)
        
        # Send notification for orders
        order_amount = data.get('amount', 0)
        customer_email = data.get('customer_email', 'Unknown')
        
        notify_user_action(
            "New Order",
            f"💰 Order placed: ${order_amount} by {customer_email}"
        )
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': 'ORD-12345'  # Your actual order ID
        }), 201
        
    except Exception as e:
        notify_error(f"Order processing failed: {str(e)}")
        return jsonify({'error': 'Failed to process order'}), 500

@app.route('/api/notify', methods=['POST'])
def manual_notification():
    """Manual notification endpoint for testing."""
    try:
        data = request.get_json()
        message = data.get('message', 'Test notification')
        
        success = send_notification_sync(f"📱 Manual Notification\\n\\n{message}")
        
        return jsonify({
            'success': success,
            'message': 'Notification sent' if success else 'Failed to send notification'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'telegram_configured': bool(app.config['TELEGRAM_BOT_TOKEN'])
    })

# Background job example (requires APScheduler)
def send_daily_report():
    """Send daily report (call this from a background job)."""
    try:
        # Gather your app statistics
        report = f"""
📊 **Daily Flask App Report**

**Date:** {datetime.now().strftime('%Y-%m-%d')}

**Statistics:**
• App uptime: Available via health check
• Last report: {datetime.now().strftime('%H:%M:%S')}

**Status:** All systems operational ✅
"""
        
        success = send_notification_sync(report)
        logger.info(f"Daily report sent: {success}")
        
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")
        notify_error(f"Daily report failed: {str(e)}")

# CLI command for testing
@app.cli.command()
def test_notification():
    """CLI command to test notifications."""
    try:
        success = send_notification_sync("🧪 Flask CLI test notification")
        print(f"Notification sent: {success}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Send startup notification
    try:
        notify_system_event("Flask App Starting", "Development server starting...")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

# Usage examples:
# 
# 1. Start the app:
#    python app.py
#
# 2. Test manual notification:
#    curl -X POST http://localhost:5000/api/notify \
#         -H "Content-Type: application/json" \
#         -d '{"message": "Hello from Flask API!"}'
#
# 3. Test user creation:
#    curl -X POST http://localhost:5000/api/users \
#         -H "Content-Type: application/json" \
#         -d '{"email": "test@example.com", "name": "Test User"}'
#
# 4. Test CLI command:
#    flask test-notification
