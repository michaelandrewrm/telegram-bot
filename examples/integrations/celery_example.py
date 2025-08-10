"""
Celery Integration Example
Shows how to integrate Telegram notifications into Celery tasks.
"""

# Install the notifier package:
# pip install /path/to/telegram-bot

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from celery import Celery
from celery.signals import task_success, task_failure, task_retry, worker_ready, worker_shutdown

# Import our notification package
from telegram_notifier import send_notification_sync

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Celery
app = Celery('telegram_notifier_example')

# Celery configuration
app.conf.update(
    broker_url=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_annotations={
        '*': {'rate_limit': '10/s'}
    },
    worker_hijack_root_logger=False,
)

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS', '').split(',')

# Notification helper functions
def send_task_notification(title: str, message: str, task_info: Dict[str, Any] = None):
    """Send Celery task notification."""
    try:
        notification_msg = f"⚙️ **{title}**\\n\\n{message}"
        
        if task_info:
            notification_msg += f"""
            
**Task Details:**
• Task ID: {task_info.get('task_id', 'Unknown')}
• Task Name: {task_info.get('task_name', 'Unknown')}
• Worker: {task_info.get('hostname', 'Unknown')}
• Started: {task_info.get('started_at', 'Unknown')}
"""
        
        notification_msg += f"\\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = send_notification_sync(notification_msg)
        logger.info(f"Task notification sent: {success}")
        return success
        
    except Exception as e:
        logger.error(f"Failed to send task notification: {e}")
        return False

def send_error_notification(error_msg: str, task_info: Dict[str, Any] = None, exception: Exception = None):
    """Send error notification for failed tasks."""
    try:
        notification_msg = f"🚨 **Celery Task Error**\\n\\n{error_msg}"
        
        if task_info:
            notification_msg += f"""
            
**Task Details:**
• Task ID: {task_info.get('task_id', 'Unknown')}
• Task Name: {task_info.get('task_name', 'Unknown')}
• Worker: {task_info.get('hostname', 'Unknown')}
• Failed At: {task_info.get('failed_at', 'Unknown')}
"""
        
        if exception:
            notification_msg += f"\\n**Exception:** {str(exception)[:200]}..."
        
        notification_msg += f"\\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = send_notification_sync(notification_msg)
        logger.info(f"Error notification sent: {success}")
        return success
        
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")
        return False

# Celery signal handlers
@task_success.connect
def on_task_success(sender=None, task_id=None, result=None, retries=None, einfo=None, **kwargs):
    """Handle successful task completion."""
    # Only notify for important tasks (you can customize this logic)
    important_tasks = ['process_large_dataset', 'send_bulk_emails', 'generate_report']
    
    if sender and sender.__name__ in important_tasks:
        task_info = {
            'task_id': task_id,
            'task_name': sender.__name__,
            'hostname': kwargs.get('hostname', 'Unknown'),
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        send_task_notification(
            "Task Completed Successfully",
            f"Task '{sender.__name__}' completed successfully",
            task_info
        )

@task_failure.connect
def on_task_failure(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    """Handle task failure."""
    task_info = {
        'task_id': task_id,
        'task_name': sender.__name__ if sender else 'Unknown',
        'hostname': kwargs.get('hostname', 'Unknown'),
        'failed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    send_error_notification(
        f"Task '{sender.__name__ if sender else 'Unknown'}' failed",
        task_info,
        exception
    )

@task_retry.connect
def on_task_retry(sender=None, task_id=None, reason=None, einfo=None, **kwargs):
    """Handle task retry."""
    # Only notify for multiple retries to avoid spam
    if kwargs.get('retries', 0) > 2:
        task_info = {
            'task_id': task_id,
            'task_name': sender.__name__ if sender else 'Unknown',
            'hostname': kwargs.get('hostname', 'Unknown'),
            'retry_count': kwargs.get('retries', 0)
        }
        
        send_task_notification(
            "Task Retry Alert",
            f"Task '{sender.__name__ if sender else 'Unknown'}' retrying (attempt #{kwargs.get('retries', 0)})",
            task_info
        )

@worker_ready.connect
def on_worker_ready(sender=None, **kwargs):
    """Handle worker startup."""
    send_task_notification(
        "Celery Worker Started",
        f"Worker '{sender.hostname}' is ready to process tasks"
    )

@worker_shutdown.connect
def on_worker_shutdown(sender=None, **kwargs):
    """Handle worker shutdown."""
    send_task_notification(
        "Celery Worker Shutdown",
        f"Worker '{sender.hostname}' is shutting down"
    )

# Sample tasks with notifications
@app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_user_data(self, user_id: int, data: Dict[str, Any]):
    """Process user data with error handling and notifications."""
    try:
        logger.info(f"Processing user data for user {user_id}")
        
        # Simulate processing
        import time
        time.sleep(2)  # Simulate work
        
        # Your actual processing logic here
        result = {
            'user_id': user_id,
            'processed_fields': len(data),
            'processed_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        logger.info(f"User data processed successfully for user {user_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Error processing user data: {exc}")
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying task in {self.default_retry_delay} seconds...")
            raise self.retry(countdown=self.default_retry_delay, exc=exc)
        else:
            # Final failure - send notification
            send_error_notification(
                f"Failed to process user data for user {user_id} after {self.max_retries} retries",
                {
                    'task_id': self.request.id,
                    'task_name': 'process_user_data',
                    'user_id': user_id
                },
                exc
            )
            raise exc

@app.task(bind=True)
def send_bulk_emails(self, recipient_list: list, subject: str, body: str):
    """Send bulk emails with progress notifications."""
    try:
        total_emails = len(recipient_list)
        
        # Send start notification
        send_task_notification(
            "Bulk Email Started",
            f"Starting to send {total_emails} emails"
        )
        
        # Process emails
        sent_count = 0
        failed_count = 0
        
        for i, email in enumerate(recipient_list):
            try:
                # Your email sending logic here
                # send_email(email, subject, body)
                sent_count += 1
                
                # Progress notification every 100 emails
                if (i + 1) % 100 == 0:
                    progress = ((i + 1) / total_emails) * 100
                    send_task_notification(
                        "Bulk Email Progress",
                        f"Progress: {i + 1}/{total_emails} emails sent ({progress:.1f}%)"
                    )
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send email to {email}: {e}")
        
        # Send completion notification
        result = {
            'total_emails': total_emails,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'success_rate': (sent_count / total_emails) * 100 if total_emails > 0 else 0
        }
        
        send_task_notification(
            "Bulk Email Completed",
            f"Bulk email job completed\\n"
            f"• Total: {total_emails}\\n"
            f"• Sent: {sent_count}\\n"
            f"• Failed: {failed_count}\\n"
            f"• Success Rate: {result['success_rate']:.1f}%"
        )
        
        return result
        
    except Exception as exc:
        send_error_notification(
            f"Bulk email job failed",
            {
                'task_id': self.request.id,
                'task_name': 'send_bulk_emails',
                'total_emails': len(recipient_list)
            },
            exc
        )
        raise exc

@app.task(bind=True)
def generate_report(self, report_type: str, date_range: Dict[str, str]):
    """Generate report with notifications."""
    try:
        # Send start notification
        send_task_notification(
            "Report Generation Started",
            f"Generating {report_type} report for {date_range.get('start')} to {date_range.get('end')}"
        )
        
        # Simulate report generation
        import time
        time.sleep(10)  # Simulate long-running task
        
        # Your actual report generation logic here
        report_data = {
            'report_type': report_type,
            'date_range': date_range,
            'generated_at': datetime.now().isoformat(),
            'file_path': f"/reports/{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        }
        
        # Send completion notification with file
        send_task_notification(
            "Report Generated Successfully",
            f"Report '{report_type}' has been generated\\n"
            f"• File: {report_data['file_path']}\\n"
            f"• Generated: {report_data['generated_at']}"
        )
        
        return report_data
        
    except Exception as exc:
        send_error_notification(
            f"Report generation failed for {report_type}",
            {
                'task_id': self.request.id,
                'task_name': 'generate_report',
                'report_type': report_type
            },
            exc
        )
        raise exc

@app.task
def periodic_health_check():
    """Periodic health check task."""
    try:
        # Check various system components
        checks = {
            'database': True,  # Your DB check here
            'redis': True,     # Your Redis check here
            'api': True,       # Your API check here
            'disk_space': True # Your disk space check here
        }
        
        failed_checks = [name for name, status in checks.items() if not status]
        
        if failed_checks:
            send_error_notification(
                f"Health Check Failed",
                {
                    'task_name': 'periodic_health_check',
                    'failed_checks': failed_checks
                }
            )
        else:
            # Only send success notification occasionally (daily)
            if datetime.now().hour == 9 and datetime.now().minute < 5:  # 9 AM
                send_task_notification(
                    "Daily Health Check",
                    "All system components are healthy ✅"
                )
        
        return {'status': 'healthy' if not failed_checks else 'unhealthy', 'checks': checks}
        
    except Exception as exc:
        send_error_notification(
            "Health check task failed",
            {'task_name': 'periodic_health_check'},
            exc
        )
        raise exc

@app.task
def cleanup_old_files():
    """Cleanup old files with notification."""
    try:
        # Your cleanup logic here
        deleted_files = []  # List of deleted files
        
        send_task_notification(
            "File Cleanup Completed",
            f"Cleaned up {len(deleted_files)} old files"
        )
        
        return {'deleted_files': len(deleted_files)}
        
    except Exception as exc:
        send_error_notification(
            "File cleanup failed",
            {'task_name': 'cleanup_old_files'},
            exc
        )
        raise exc

# Periodic tasks configuration
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Health check every 5 minutes
    'health-check': {
        'task': 'main.periodic_health_check',
        'schedule': crontab(minute='*/5'),
    },
    # Daily cleanup at 2 AM
    'daily-cleanup': {
        'task': 'main.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),
    },
    # Weekly report on Sunday at 9 AM
    'weekly-report': {
        'task': 'main.generate_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=0),
        'args': ('weekly', {'start': '7 days ago', 'end': 'today'})
    },
}

app.conf.timezone = 'UTC'

if __name__ == '__main__':
    # Start the worker
    app.start()

# Usage examples:
#
# 1. Start Celery worker:
#    celery -A main worker --loglevel=info
#
# 2. Start Celery beat (for periodic tasks):
#    celery -A main beat --loglevel=info
#
# 3. Monitor tasks:
#    celery -A main flower
#
# 4. Execute tasks from Python:
#    from main import process_user_data, send_bulk_emails
#    
#    # Async execution
#    result = process_user_data.delay(123, {'name': 'John', 'email': 'john@example.com'})
#    
#    # Get result
#    print(result.get())
#
# 5. Execute tasks from command line:
#    celery -A main call main.process_user_data --args='[123, {"name": "John"}]'
