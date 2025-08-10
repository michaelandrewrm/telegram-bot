"""Example: Sending notifications from application code."""

import asyncio
import sys
import os

# Add the bot package to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import send_notification


async def example_application_notification():
    """Example of sending a notification from application code."""
    
    # Simple text notification
    await send_notification(
        message="🚀 Application started successfully!",
        chat_id="YOUR_CHAT_ID"  # Replace with actual chat ID
    )
    
    # Notification with custom formatting
    message = """
📊 *Daily Report*

• Tasks completed: 150
• Errors encountered: 2
• System uptime: 99.9%

All systems are running smoothly! ✅
"""
    
    await send_notification(
        message=message,
        parse_mode="Markdown"
    )


async def example_error_notification():
    """Example of sending error notifications."""
    
    try:
        # Simulate some operation that might fail
        result = 10 / 0
    except Exception as e:
        # Send error notification
        error_message = f"""
❌ *Application Error*

**Error Type:** {type(e).__name__}
**Error Message:** {str(e)}
**Function:** example_error_notification
**Time:** {asyncio.get_event_loop().time()}

Please check the logs for more details.
"""
        
        await send_notification(
            message=error_message,
            parse_mode="Markdown"
        )


async def example_status_update():
    """Example of sending status updates."""
    
    # Data processing completion
    await send_notification(
        message="✅ Data processing job completed successfully. Processed 1,000 records in 2.5 minutes."
    )
    
    # Backup completion
    await send_notification(
        message="💾 Database backup completed. Backup size: 2.3GB. Next backup scheduled for tomorrow at 2:00 AM."
    )


async def example_monitoring_alert():
    """Example of sending monitoring alerts."""
    
    # High CPU usage alert
    cpu_usage = 95.5
    if cpu_usage > 90:
        await send_notification(
            message=f"""
🚨 *High CPU Usage Alert*

Current CPU usage: {cpu_usage}%
Threshold: 90%

Please investigate the system load.
""",
            parse_mode="Markdown"
        )


if __name__ == "__main__":
    async def main():
        print("Running application notification examples...")
        
        await example_application_notification()
        print("✅ Application notification sent")
        
        await example_error_notification()
        print("✅ Error notification sent")
        
        await example_status_update()
        print("✅ Status update sent")
        
        await example_monitoring_alert()
        print("✅ Monitoring alert sent")
        
        print("All examples completed!")
    
    asyncio.run(main())
