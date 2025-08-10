"""FastAPI application for webhook and REST API endpoints."""

import asyncio
import hmac
import hashlib
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from ..config import config
from ..services.notification import notification_service
from ..services.subscription import subscription_service
from ..services.monitoring import monitoring_service
from ..services.scheduler import scheduler_service
from ..utils.validators import validate_chat_id, validate_message, validate_webhook_token
import structlog

logger = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=config.api_title,
    version=config.api_version,
    docs_url=config.api_docs_url if config.api_enabled else None,
    redoc_url="/redoc" if config.api_enabled else None
)

# Security
security = HTTPBearer()


# Pydantic models
class NotificationRequest(BaseModel):
    """Request model for sending notifications."""
    message: str = Field(..., min_length=1, max_length=4096, description="Message text")
    chat_id: Optional[str] = Field(None, description="Specific chat ID to send to")
    chat_ids: Optional[List[str]] = Field(None, description="List of chat IDs to send to")
    parse_mode: Optional[str] = Field("Markdown", description="Message parse mode")
    disable_web_page_preview: bool = Field(True, description="Disable web page preview")


class WebhookRequest(BaseModel):
    """Request model for webhook notifications."""
    message: str = Field(..., min_length=1, description="Message text")
    level: str = Field("INFO", description="Message level")
    source: Optional[str] = Field(None, description="Message source")
    timestamp: Optional[str] = Field(None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ScheduleRequest(BaseModel):
    """Request model for scheduling notifications."""
    job_id: str = Field(..., description="Unique job identifier")
    message: str = Field(..., min_length=1, description="Message to send")
    chat_ids: List[str] = Field(..., description="Chat IDs to send to")
    trigger_type: str = Field(..., description="Trigger type (cron, interval, date)")
    trigger_kwargs: Dict[str, Any] = Field(..., description="Trigger parameters")


class ResponseModel(BaseModel):
    """Standard response model."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


# Dependency functions
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for protected endpoints."""
    if credentials.credentials != config.api_secret_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


async def verify_webhook_token(request: Request):
    """Verify webhook token."""
    token = request.headers.get("X-Webhook-Token")
    if not token or not validate_webhook_token(token, config.webhook_secret or ""):
        raise HTTPException(status_code=401, detail="Invalid webhook token")
    return token


# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test bot connection
        is_healthy = await notification_service.test_connection()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "bot_connected": is_healthy,
            "services": {
                "notification": True,
                "monitoring": monitoring_service.is_running if config.enable_monitoring else False,
                "scheduler": True if config.enable_scheduling else False
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/v1/notify", response_model=ResponseModel)
async def send_notification_api(
    request: NotificationRequest,
    api_key: str = Depends(verify_api_key)
):
    """Send a notification via API."""
    try:
        # Validate message
        is_valid, error = validate_message(request.message)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Determine target chat IDs
        chat_ids = []
        if request.chat_id:
            if not validate_chat_id(request.chat_id):
                raise HTTPException(status_code=400, detail="Invalid chat_id")
            chat_ids = [request.chat_id]
        elif request.chat_ids:
            for chat_id in request.chat_ids:
                if not validate_chat_id(chat_id):
                    raise HTTPException(status_code=400, detail=f"Invalid chat_id: {chat_id}")
            chat_ids = request.chat_ids
        else:
            # Send to default chats
            chat_ids = config.default_chat_ids
        
        if not chat_ids:
            raise HTTPException(status_code=400, detail="No chat IDs specified and no defaults configured")
        
        # Send notifications
        results = []
        for chat_id in chat_ids:
            success = await notification_service.send_notification(
                message=request.message,
                chat_id=chat_id,
                parse_mode=request.parse_mode,
                disable_web_page_preview=request.disable_web_page_preview
            )
            results.append({"chat_id": chat_id, "success": success})
        
        successful_sends = sum(1 for r in results if r["success"])
        
        return ResponseModel(
            success=successful_sends > 0,
            message=f"Sent to {successful_sends}/{len(results)} chats",
            data={"results": results}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in send notification API", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/webhook/notify")
async def webhook_notification(
    request: WebhookRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_webhook_token)
):
    """Receive webhook notifications."""
    try:
        # Format message
        from ..utils.formatters import format_message
        
        formatted_message = format_message(
            title=request.source or "Webhook Notification",
            message=request.message,
            level=request.level,
            markdown=True
        )
        
        # Send to default chats in background
        background_tasks.add_task(
            notification_service.send_to_default_chats,
            formatted_message
        )
        
        logger.info("Webhook notification received",
                   source=request.source,
                   level=request.level,
                   message_preview=request.message[:50])
        
        return ResponseModel(
            success=True,
            message="Webhook notification queued"
        )
        
    except Exception as e:
        logger.error("Error processing webhook", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/subscriptions", response_model=ResponseModel)
async def get_all_subscriptions(api_key: str = Depends(verify_api_key)):
    """Get all subscriptions."""
    try:
        subscriptions = await subscription_service.get_all_subscriptions()
        stats = await subscription_service.get_stats()
        
        return ResponseModel(
            success=True,
            message="Subscriptions retrieved",
            data={
                "subscriptions": subscriptions,
                "stats": stats
            }
        )
        
    except Exception as e:
        logger.error("Error getting subscriptions", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/system/metrics", response_model=ResponseModel)
async def get_system_metrics(api_key: str = Depends(verify_api_key)):
    """Get current system metrics."""
    try:
        metrics = await monitoring_service.get_current_metrics()
        
        return ResponseModel(
            success=True,
            message="System metrics retrieved",
            data={"metrics": metrics}
        )
        
    except Exception as e:
        logger.error("Error getting system metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/system/report", response_model=ResponseModel)
async def send_system_report(
    chat_id: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Send system report."""
    try:
        target_chat_id = None
        if chat_id:
            if not validate_chat_id(chat_id):
                raise HTTPException(status_code=400, detail="Invalid chat_id")
            target_chat_id = chat_id
        
        await monitoring_service.send_system_report(target_chat_id)
        
        return ResponseModel(
            success=True,
            message="System report sent"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error sending system report", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/schedule", response_model=ResponseModel)
async def schedule_notification(
    request: ScheduleRequest,
    api_key: str = Depends(verify_api_key)
):
    """Schedule a notification."""
    try:
        # Validate chat IDs
        for chat_id in request.chat_ids:
            if not validate_chat_id(chat_id):
                raise HTTPException(status_code=400, detail=f"Invalid chat_id: {chat_id}")
        
        # Schedule the notification
        success = await scheduler_service.schedule_notification(
            job_id=request.job_id,
            message=request.message,
            chat_ids=request.chat_ids,
            trigger_type=request.trigger_type,
            **request.trigger_kwargs
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to schedule notification")
        
        return ResponseModel(
            success=True,
            message=f"Notification scheduled with ID: {request.job_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error scheduling notification", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/v1/schedule/{job_id}", response_model=ResponseModel)
async def unschedule_notification(
    job_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Remove a scheduled notification."""
    try:
        success = await scheduler_service.unschedule_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return ResponseModel(
            success=True,
            message=f"Job {job_id} unscheduled"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error unscheduling notification", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/schedule", response_model=ResponseModel)
async def get_scheduled_jobs(api_key: str = Depends(verify_api_key)):
    """Get all scheduled jobs."""
    try:
        jobs = await scheduler_service.get_scheduled_jobs()
        
        return ResponseModel(
            success=True,
            message="Scheduled jobs retrieved",
            data={"jobs": jobs}
        )
        
    except Exception as e:
        logger.error("Error getting scheduled jobs", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {"error": "Endpoint not found", "path": str(request.url.path)}


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error("Internal server error", path=str(request.url.path), error=str(exc))
    return {"error": "Internal server error"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "bot.api:app",
        host=config.api_host,
        port=config.api_port,
        reload=False
    )
