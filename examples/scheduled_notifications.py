"""Example: Scheduled task notifications."""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the bot package to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.services.scheduler import scheduler_service
from bot.services.notification import notification_service


async def setup_daily_notifications():
    """Setup daily notification schedules."""
    
    # Daily morning greeting at 9 AM
    await scheduler_service.schedule_notification(
        job_id="daily_morning_greeting",
        message="🌅 Good morning! Have a productive day ahead! 💪",
        chat_ids=["YOUR_CHAT_ID"],  # Replace with actual chat IDs
        trigger_type="cron",
        hour=9,
        minute=0
    )
    
    # Daily afternoon check-in at 2 PM
    await scheduler_service.schedule_notification(
        job_id="daily_afternoon_checkin",
        message="🕐 Afternoon check-in: How's your day going? Take a break if needed! ☕",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron", 
        hour=14,
        minute=0
    )
    
    # Daily evening summary at 6 PM
    await scheduler_service.schedule_notification(
        job_id="daily_evening_summary",
        message="🌆 End of workday! Time to wrap up and enjoy your evening! 🎉",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        hour=18,
        minute=0
    )


async def setup_weekly_notifications():
    """Setup weekly notification schedules."""
    
    # Monday motivation at 8 AM
    await scheduler_service.schedule_notification(
        job_id="monday_motivation",
        message="🚀 Monday Motivation: New week, new opportunities! Let's make it count! 💪",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day_of_week=0,  # Monday
        hour=8,
        minute=0
    )
    
    # Wednesday mid-week check at 10 AM
    await scheduler_service.schedule_notification(
        job_id="wednesday_midweek",
        message="📈 Wednesday Check: You're halfway through the week! Keep up the great work! 🌟",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day_of_week=2,  # Wednesday
        hour=10,
        minute=0
    )
    
    # Friday celebration at 5 PM
    await scheduler_service.schedule_notification(
        job_id="friday_celebration", 
        message="🎉 TGIF! Another successful week completed! Time to celebrate! 🥳",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day_of_week=4,  # Friday
        hour=17,
        minute=0
    )


async def setup_reminder_notifications():
    """Setup reminder notifications."""
    
    # Hourly hydration reminder during work hours
    for hour in range(9, 18):  # 9 AM to 5 PM
        await scheduler_service.schedule_notification(
            job_id=f"hydration_reminder_{hour}",
            message="💧 Hydration reminder: Time for a glass of water! Stay healthy! 🥤",
            chat_ids=["YOUR_CHAT_ID"],
            trigger_type="cron",
            hour=hour,
            minute=0
        )
    
    # Bi-weekly backup reminder
    await scheduler_service.schedule_notification(
        job_id="backup_reminder",
        message="💾 Backup Reminder: Don't forget to backup your important files! 🔒",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day_of_week=1,  # Tuesday
        hour=10,
        minute=0
    )
    
    # Monthly goal review
    await scheduler_service.schedule_notification(
        job_id="monthly_goal_review",
        message="🎯 Monthly Goal Review: Time to review your progress and set new goals! 📊",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day=1,  # First day of month
        hour=9,
        minute=0
    )


async def setup_system_maintenance_schedules():
    """Setup system maintenance schedules."""
    
    # Daily system health check at midnight
    await scheduler_service.schedule_custom_job(
        job_id="daily_health_check",
        func=send_daily_health_check,
        trigger_type="cron",
        hour=0,
        minute=0
    )
    
    # Weekly log cleanup on Sunday at 3 AM
    await scheduler_service.schedule_custom_job(
        job_id="weekly_log_cleanup",
        func=perform_log_cleanup,
        trigger_type="cron",
        day_of_week=6,  # Sunday
        hour=3,
        minute=0
    )
    
    # Monthly system report on first Monday at 8 AM
    await scheduler_service.schedule_custom_job(
        job_id="monthly_system_report",
        func=send_monthly_system_report,
        trigger_type="cron",
        day=1,
        hour=8,
        minute=0
    )


async def setup_development_schedules():
    """Setup development-related schedules."""
    
    # Daily code commit reminder at 4 PM (weekdays only)
    for day in range(5):  # Monday to Friday
        await scheduler_service.schedule_notification(
            job_id=f"commit_reminder_day_{day}",
            message="💻 Code Commit Reminder: Don't forget to commit your changes! 🔄",
            chat_ids=["YOUR_CHAT_ID"],
            trigger_type="cron",
            day_of_week=day,
            hour=16,
            minute=0
        )
    
    # Weekly dependency update check on Friday at 11 AM
    await scheduler_service.schedule_notification(
        job_id="dependency_update_check",
        message="📦 Dependency Update Check: Time to check for package updates! 🔄",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="cron",
        day_of_week=4,  # Friday
        hour=11,
        minute=0
    )


async def send_daily_health_check():
    """Custom function for daily health check."""
    try:
        from bot.services.monitoring import monitoring_service
        
        # Get system metrics
        metrics = await monitoring_service.get_current_metrics()
        
        # Create health check message
        message = f"""
🔍 *Daily Health Check*

**CPU Usage:** {metrics.get('cpu_percent', 'N/A')}%
**Memory Usage:** {metrics.get('memory_percent', 'N/A')}%
**Disk Usage:** {metrics.get('disk_percent', 'N/A')}%

**Status:** {'✅ Healthy' if all(metrics.get(key, 0) < 80 for key in ['cpu_percent', 'memory_percent', 'disk_percent']) else '⚠️ Needs Attention'}

🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        
        # Send to default chats
        await notification_service.send_to_default_chats(message)
        
    except Exception as e:
        await notification_service.send_to_default_chats(
            f"❌ Health check failed: {str(e)}"
        )


async def perform_log_cleanup():
    """Custom function for log cleanup."""
    try:
        # Simulate log cleanup (implement your actual cleanup logic)
        await asyncio.sleep(1)  # Simulate cleanup time
        
        message = """
🧹 *Weekly Log Cleanup Completed*

• Old log files removed
• Disk space freed: 250MB  
• Cleanup duration: 30 seconds

Next cleanup: Next Sunday at 3:00 AM
"""
        
        await notification_service.send_to_default_chats(message)
        
    except Exception as e:
        await notification_service.send_to_default_chats(
            f"❌ Log cleanup failed: {str(e)}"
        )


async def send_monthly_system_report():
    """Custom function for monthly system report."""
    try:
        # Generate monthly report (implement your actual report logic)
        message = f"""
📊 *Monthly System Report*

**Period:** {datetime.now().strftime('%B %Y')}

**Uptime:** 99.8%
**Notifications Sent:** 1,247
**Active Users:** 23
**System Health:** Excellent ✅

**Key Metrics:**
• Average CPU: 25%
• Average Memory: 45%
• Average Disk: 60%

**Incidents:** 2 minor, resolved
**Scheduled Maintenance:** Next month

System performance remains optimal! 🚀
"""
        
        await notification_service.send_to_default_chats(message)
        
    except Exception as e:
        await notification_service.send_to_default_chats(
            f"❌ Monthly report failed: {str(e)}"
        )


async def setup_one_time_notifications():
    """Setup one-time notifications."""
    
    # Schedule a notification for 5 minutes from now
    future_time = datetime.now() + timedelta(minutes=5)
    await scheduler_service.schedule_notification(
        job_id="test_one_time",
        message="⏰ This is a one-time test notification scheduled 5 minutes ago!",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="date",
        run_date=future_time
    )
    
    # Schedule a reminder for tomorrow at 9 AM
    tomorrow_9am = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    await scheduler_service.schedule_notification(
        job_id="tomorrow_reminder",
        message="📅 This is your reminder for today! Have a great day! ☀️",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="date",
        run_date=tomorrow_9am
    )


async def setup_interval_notifications():
    """Setup interval-based notifications."""
    
    # Every 5 minutes (for testing - remove in production)
    await scheduler_service.schedule_notification(
        job_id="test_interval_5min",
        message="⏱️ 5-minute interval test notification",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="interval",
        minutes=5
    )
    
    # Every hour status check
    await scheduler_service.schedule_notification(
        job_id="hourly_status",
        message="📊 Hourly status: All systems operational! ✅",
        chat_ids=["YOUR_CHAT_ID"],
        trigger_type="interval",
        hours=1
    )


if __name__ == "__main__":
    async def main():
        print("Setting up scheduled notifications...")
        
        # Start scheduler service
        await scheduler_service.start()
        
        try:
            # Setup different types of schedules
            await setup_daily_notifications()
            print("✅ Daily notifications scheduled")
            
            await setup_weekly_notifications()
            print("✅ Weekly notifications scheduled")
            
            await setup_reminder_notifications()
            print("✅ Reminder notifications scheduled")
            
            await setup_system_maintenance_schedules()
            print("✅ System maintenance schedules set")
            
            await setup_development_schedules()
            print("✅ Development schedules set")
            
            await setup_one_time_notifications()
            print("✅ One-time notifications scheduled")
            
            # Uncomment for testing (be careful - creates frequent notifications)
            # await setup_interval_notifications()
            # print("✅ Interval notifications scheduled")
            
            # List all scheduled jobs
            jobs = await scheduler_service.get_scheduled_jobs()
            print(f"\n📋 Total scheduled jobs: {len(jobs)}")
            
            for job in jobs[:5]:  # Show first 5 jobs
                print(f"  • {job['id']} - Next run: {job['next_run_time']}")
            
            print("\nAll schedules have been set up successfully!")
            print("The scheduler will continue running in the background.")
            
            # Keep the script running to see scheduled notifications
            print("\nPress Ctrl+C to stop...")
            try:
                while True:
                    await asyncio.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\nStopping scheduler...")
                
        finally:
            await scheduler_service.stop()
    
    asyncio.run(main())
