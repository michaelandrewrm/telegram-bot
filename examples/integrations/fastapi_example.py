"""
FastAPI Integration Example
Shows how to integrate Telegram notifications into a FastAPI application.
"""

# Install the notifier package:
# pip install /path/to/telegram-bot

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import logging
import traceback

# Import our notification package
from telegram_notifier import TelegramNotifier, send_notification_sync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="FastAPI with Telegram Notifications",
    description="Example integration of Telegram notifications with FastAPI",
    version="1.0.0"
)

# Configure Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your_token_here')
TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS', 'your_chat_id').split(',')

# Initialize Telegram notifier
notifier = TelegramNotifier(
    bot_token=TELEGRAM_BOT_TOKEN,
    default_chat_ids=TELEGRAM_CHAT_IDS
)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    age: Optional[int] = None

class OrderCreate(BaseModel):
    customer_email: EmailStr
    amount: float
    items: list[str]

class NotificationRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None

# Notification helpers
async def notify_error_async(error_msg: str, request_info: Dict[str, Any] = None):
    """Send error notification asynchronously."""
    message = f"🚨 **FastAPI Error**\\n\\n{error_msg}"
    
    if request_info:
        message += f"""
        
**Request Details:**
• URL: {request_info.get('url', 'Unknown')}
• Method: {request_info.get('method', 'Unknown')}
• Client IP: {request_info.get('client_ip', 'Unknown')}
• User Agent: {request_info.get('user_agent', 'Unknown')[:100]}...
"""
    
    message += f"\\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return await notifier.send(message)

async def notify_user_action_async(action: str, details: str = "", user_info: Dict[str, Any] = None):
    """Notify about user actions asynchronously."""
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
    
    return await notifier.send(message)

async def notify_system_event_async(event: str, details: str = ""):
    """Notify about system events asynchronously."""
    message = f"""
⚡ **System Event**

**Event:** {event}
**Details:** {details}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return await notifier.send(message)

# Background task functions
async def send_notification_background(message: str, chat_id: Optional[str] = None):
    """Send notification in background."""
    try:
        await notifier.send(message, chat_id=chat_id)
        logger.info("Background notification sent successfully")
    except Exception as e:
        logger.error(f"Background notification failed: {e}")

# Application events
@app.on_event("startup")
async def startup_event():
    """Send notification when app starts."""
    try:
        await notify_system_event_async("FastAPI App Started", "Application is now running")
        logger.info("Startup notification sent")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Send notification when app shuts down."""
    try:
        await notify_system_event_async("FastAPI App Shutdown", "Application is shutting down")
        logger.info("Shutdown notification sent")
    except Exception as e:
        logger.error(f"Failed to send shutdown notification: {e}")

# Exception handlers
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle 500 errors and send notification."""
    error_msg = f"Internal Server Error: {str(exc)}"
    
    request_info = {
        'url': str(request.url),
        'method': request.method,
        'client_ip': request.client.host,
        'user_agent': request.headers.get('user-agent', 'Unknown')
    }
    
    # Send notification in background
    asyncio.create_task(notify_error_async(error_msg, request_info))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "The error has been logged and administrators have been notified."
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    # Only notify for server errors (5xx), not client errors (4xx)
    if exc.status_code >= 500:
        error_msg = f"HTTP {exc.status_code}: {exc.detail}"
        request_info = {
            'url': str(request.url),
            'method': request.method,
            'client_ip': request.client.host,
        }
        asyncio.create_task(notify_error_async(error_msg, request_info))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "FastAPI with Telegram Notifications", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test telegram connection
        telegram_connected = await notifier.test_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "telegram_configured": bool(TELEGRAM_BOT_TOKEN),
            "telegram_connected": telegram_connected
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/api/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, request: Request, background_tasks: BackgroundTasks):
    """Create user endpoint with notification."""
    try:
        # Your user creation logic here
        # user_record = await create_user_in_database(user)
        
        # Prepare notification
        user_info = {
            'ip': request.client.host,
            'user_agent': request.headers.get('user-agent', 'Unknown')
        }
        
        # Send notification in background
        background_tasks.add_task(
            notify_user_action_async,
            "User Registration",
            f"New user: {user.email} ({user.name})",
            user_info
        )
        
        return {
            "message": "User created successfully",
            "email": user.email,
            "name": user.name
        }
        
    except Exception as e:
        error_msg = f"Failed to create user: {str(e)}"
        await notify_error_async(error_msg, {
            'url': str(request.url),
            'method': request.method,
            'client_ip': request.client.host,
            'user_agent': request.headers.get('user-agent', 'Unknown')
        })
        
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.post("/api/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    """Create order endpoint with notification."""
    try:
        # Your order processing logic here
        # order_record = await process_order(order)
        
        # Send notification for orders
        order_details = f"💰 New Order: ${order.amount} by {order.customer_email}\\nItems: {', '.join(order.items)}"
        
        background_tasks.add_task(
            notify_user_action_async,
            "New Order",
            order_details
        )
        
        return {
            "message": "Order created successfully",
            "order_id": "ORD-12345",  # Your actual order ID
            "amount": order.amount,
            "customer": order.customer_email
        }
        
    except Exception as e:
        await notify_error_async(f"Order processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process order")

@app.post("/api/notify")
async def manual_notification(notification: NotificationRequest):
    """Manual notification endpoint for testing."""
    try:
        success = await notifier.send(
            f"📱 Manual Notification\\n\\n{notification.message}",
            chat_id=notification.chat_id
        )
        
        return {
            "success": success,
            "message": "Notification sent" if success else "Failed to send notification"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-error")
async def test_error():
    """Endpoint to test error handling and notifications."""
    raise Exception("This is a test error to verify notification system")

# Background jobs (you can integrate with APScheduler)
async def send_daily_report():
    """Send daily report (call this from a background scheduler)."""
    try:
        # Gather your app statistics
        report = f"""
📊 **Daily FastAPI Report**

**Date:** {datetime.now().strftime('%Y-%m-%d')}

**Statistics:**
• App status: Running
• Health check: Available at /health
• Last report: {datetime.now().strftime('%H:%M:%S')}

**Status:** All systems operational ✅
"""
        
        success = await notifier.send(report)
        logger.info(f"Daily report sent: {success}")
        
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")
        await notify_error_async(f"Daily report failed: {str(e)}")

# WebSocket example (optional)
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications."""
    await websocket.accept()
    
    # Notify about new WebSocket connection
    await notify_system_event_async(
        "WebSocket Connection", 
        f"New WebSocket client connected from {websocket.client.host}"
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Echo the message and send via Telegram
            await websocket.send_text(f"Echo: {data}")
            await notifier.send(f"📱 WebSocket Message: {data}")
            
    except WebSocketDisconnect:
        await notify_system_event_async(
            "WebSocket Disconnection", 
            f"WebSocket client disconnected from {websocket.client.host}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Send startup notification (for development)
    try:
        send_notification_sync("🚀 FastAPI Development Server Starting...")
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
    
    # Run the app
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Usage examples:
# 
# 1. Start the app:
#    python main.py
#    # or: uvicorn main:app --reload
#
# 2. Test manual notification:
#    curl -X POST http://localhost:8000/api/notify \
#         -H "Content-Type: application/json" \
#         -d '{"message": "Hello from FastAPI!"}'
#
# 3. Test user creation:
#    curl -X POST http://localhost:8000/api/users \
#         -H "Content-Type: application/json" \
#         -d '{"email": "test@example.com", "name": "Test User", "age": 25}'
#
# 4. Test error handling:
#    curl -X POST http://localhost:8000/api/test-error
#
# 5. Check health:
#    curl http://localhost:8000/health
#
# 6. View API docs:
#    Open http://localhost:8000/docs in your browser
