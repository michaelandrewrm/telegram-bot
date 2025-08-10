"""Scheduling service for automated notifications."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from ..config import config
from ..services.notification import notification_service
from ..services.subscription import subscription_service
from ..constants import SUBSCRIPTION_TYPES
import structlog

logger = structlog.get_logger(__name__)


class SchedulerService:
    """Service for scheduling automated notifications and tasks."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=config.scheduler_timezone,
            max_workers=config.scheduler_max_workers
        )
        self._scheduled_jobs: Dict[str, Any] = {}
    
    async def start(self):
        """Start the scheduler service."""
        try:
            self.scheduler.start()
            logger.info("Scheduler service started")
            
            # Schedule default jobs
            await self._schedule_default_jobs()
            
        except Exception as e:
            logger.error("Error starting scheduler", error=str(e))
    
    async def stop(self):
        """Stop the scheduler service."""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler service stopped")
        except Exception as e:
            logger.error("Error stopping scheduler", error=str(e))
    
    async def _schedule_default_jobs(self):
        """Schedule default recurring jobs."""
        if config.enable_scheduling:
            # Daily system report at 9 AM
            await self.schedule_daily_system_report(hour=9, minute=0)
            
            # Weekly summary on Mondays at 10 AM
            await self.schedule_weekly_summary(day_of_week=0, hour=10, minute=0)
    
    async def schedule_notification(
        self,
        job_id: str,
        message: str,
        chat_ids: List[int],
        trigger_type: str,
        **trigger_kwargs
    ) -> bool:
        """Schedule a notification.
        
        Args:
            job_id: Unique job identifier
            message: Message to send
            chat_ids: List of chat IDs to send to
            trigger_type: Type of trigger (cron, interval, date)
            **trigger_kwargs: Trigger-specific arguments
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            # Create the trigger
            if trigger_type == 'cron':
                trigger = CronTrigger(**trigger_kwargs)
            elif trigger_type == 'interval':
                trigger = IntervalTrigger(**trigger_kwargs)
            elif trigger_type == 'date':
                trigger = DateTrigger(**trigger_kwargs)
            else:
                logger.error("Invalid trigger type", trigger_type=trigger_type)
                return False
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=self._send_scheduled_notification,
                trigger=trigger,
                args=[message, chat_ids],
                id=job_id,
                replace_existing=True
            )
            
            self._scheduled_jobs[job_id] = {
                'job': job,
                'message': message,
                'chat_ids': chat_ids,
                'trigger_type': trigger_type,
                'trigger_kwargs': trigger_kwargs,
                'created_at': datetime.now()
            }
            
            logger.info("Notification scheduled",
                       job_id=job_id,
                       trigger_type=trigger_type,
                       next_run=job.next_run_time)
            
            return True
            
        except Exception as e:
            logger.error("Error scheduling notification",
                        job_id=job_id,
                        error=str(e))
            return False
    
    async def schedule_daily_system_report(
        self,
        hour: int = 9,
        minute: int = 0,
        job_id: str = "daily_system_report"
    ) -> bool:
        """Schedule daily system reports.
        
        Args:
            hour: Hour of day to send (0-23)
            minute: Minute of hour to send (0-59)
            job_id: Job identifier
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            job = self.scheduler.add_job(
                func=self._send_daily_system_report,
                trigger=CronTrigger(hour=hour, minute=minute),
                id=job_id,
                replace_existing=True
            )
            
            logger.info("Daily system report scheduled",
                       job_id=job_id,
                       time=f"{hour:02d}:{minute:02d}",
                       next_run=job.next_run_time)
            
            return True
            
        except Exception as e:
            logger.error("Error scheduling daily system report", error=str(e))
            return False
    
    async def schedule_weekly_summary(
        self,
        day_of_week: int = 0,  # Monday
        hour: int = 10,
        minute: int = 0,
        job_id: str = "weekly_summary"
    ) -> bool:
        """Schedule weekly summaries.
        
        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day to send (0-23)
            minute: Minute of hour to send (0-59)
            job_id: Job identifier
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            job = self.scheduler.add_job(
                func=self._send_weekly_summary,
                trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
                id=job_id,
                replace_existing=True
            )
            
            logger.info("Weekly summary scheduled",
                       job_id=job_id,
                       day_of_week=day_of_week,
                       time=f"{hour:02d}:{minute:02d}",
                       next_run=job.next_run_time)
            
            return True
            
        except Exception as e:
            logger.error("Error scheduling weekly summary", error=str(e))
            return False
    
    async def schedule_custom_job(
        self,
        job_id: str,
        func: Callable,
        trigger_type: str,
        **trigger_kwargs
    ) -> bool:
        """Schedule a custom job.
        
        Args:
            job_id: Unique job identifier
            func: Function to execute
            trigger_type: Type of trigger (cron, interval, date)
            **trigger_kwargs: Trigger-specific arguments
            
        Returns:
            True if scheduled successfully, False otherwise
        """
        try:
            # Create the trigger
            if trigger_type == 'cron':
                trigger = CronTrigger(**trigger_kwargs)
            elif trigger_type == 'interval':
                trigger = IntervalTrigger(**trigger_kwargs)
            elif trigger_type == 'date':
                trigger = DateTrigger(**trigger_kwargs)
            else:
                logger.error("Invalid trigger type", trigger_type=trigger_type)
                return False
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                replace_existing=True
            )
            
            logger.info("Custom job scheduled",
                       job_id=job_id,
                       trigger_type=trigger_type,
                       next_run=job.next_run_time)
            
            return True
            
        except Exception as e:
            logger.error("Error scheduling custom job",
                        job_id=job_id,
                        error=str(e))
            return False
    
    async def unschedule_job(self, job_id: str) -> bool:
        """Remove a scheduled job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if removed successfully, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)
            
            if job_id in self._scheduled_jobs:
                del self._scheduled_jobs[job_id]
            
            logger.info("Job unscheduled", job_id=job_id)
            return True
            
        except Exception as e:
            logger.error("Error unscheduling job", job_id=job_id, error=str(e))
            return False
    
    async def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get list of scheduled jobs.
        
        Returns:
            List of job information dictionaries
        """
        jobs = []
        
        for job in self.scheduler.get_jobs():
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run_time': getattr(job, 'next_run_time', None),
                'trigger': str(job.trigger)
            }
            
            # Add custom job info if available
            if job.id in self._scheduled_jobs:
                custom_info = self._scheduled_jobs[job.id]
                job_info.update({
                    'message': custom_info.get('message'),
                    'chat_ids': custom_info.get('chat_ids'),
                    'created_at': custom_info.get('created_at')
                })
            
            jobs.append(job_info)
        
        return jobs
    
    async def _send_scheduled_notification(self, message: str, chat_ids: List[int]):
        """Send a scheduled notification."""
        try:
            for chat_id in chat_ids:
                await notification_service.send_notification(
                    message=message,
                    chat_id=chat_id,
                    parse_mode='Markdown'
                )
            
            logger.info("Scheduled notification sent",
                       message_preview=message[:50],
                       chat_count=len(chat_ids))
            
        except Exception as e:
            logger.error("Error sending scheduled notification", error=str(e))
    
    async def _send_daily_system_report(self):
        """Send daily system report to subscribers."""
        try:
            from ..services.monitoring import monitoring_service
            
            # Get system subscribers
            subscribers = await subscription_service.get_subscribers(
                SUBSCRIPTION_TYPES['SYSTEM']
            )
            
            if not subscribers:
                logger.info("No system subscribers for daily report")
                return
            
            # Send system report
            await monitoring_service.send_system_report()
            
            logger.info("Daily system report sent", subscribers=len(subscribers))
            
        except Exception as e:
            logger.error("Error sending daily system report", error=str(e))
    
    async def _send_weekly_summary(self):
        """Send weekly summary to subscribers."""
        try:
            # Get scheduled subscribers
            subscribers = await subscription_service.get_subscribers(
                SUBSCRIPTION_TYPES['SCHEDULED']
            )
            
            if not subscribers:
                logger.info("No scheduled subscribers for weekly summary")
                return
            
            # Create summary message
            message = f"""
📊 *Weekly Summary*

This week's highlights:
• System uptime: Good
• Notifications sent: Check logs
• Active subscribers: {len(subscribers)}

Have a great week ahead! 🚀

🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            # Send to subscribers
            for user_id in subscribers:
                await notification_service.send_notification(
                    message=message,
                    chat_id=user_id,
                    parse_mode='Markdown'
                )
            
            logger.info("Weekly summary sent", subscribers=len(subscribers))
            
        except Exception as e:
            logger.error("Error sending weekly summary", error=str(e))


# Global scheduler service instance
scheduler_service = SchedulerService()
