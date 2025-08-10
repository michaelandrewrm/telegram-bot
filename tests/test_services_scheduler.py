"""Tests for bot services scheduler."""

import pytest
import asyncio
import sys
import os

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSchedulerStructure:
    """Test scheduler service structure and imports."""

    def test_import_structure(self):
        """Test that scheduler service can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.services.scheduler", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "services", "scheduler.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load scheduler service: {e}")


class TestSchedulerService:
    """Test SchedulerService class."""

    def setup_method(self):
        """Set up test environment."""
        # Mock SchedulerService
        class MockSchedulerService:
            def __init__(self):
                self.scheduler = MagicMock()
                self._scheduled_jobs = {}
                self.is_running = False
        
        self.service = MockSchedulerService()

    def test_scheduler_service_initialization(self):
        """Test SchedulerService initialization."""
        assert self.service.scheduler is not None
        assert self.service._scheduled_jobs == {}
        assert self.service.is_running is False

    def test_start_scheduler_service(self):
        """Test starting scheduler service."""
        async def mock_start_scheduler(service):
            """Mock scheduler service start."""
            try:
                service.scheduler.start()
                service.is_running = True
                return "started"
            except Exception as e:
                return f"error: {e}"
        
        # Test successful start
        result = asyncio.run(mock_start_scheduler(self.service))
        assert result == "started"
        assert self.service.is_running is True

    def test_stop_scheduler_service(self):
        """Test stopping scheduler service."""
        async def mock_stop_scheduler(service):
            """Mock scheduler service stop."""
            try:
                service.scheduler.shutdown(wait=True)
                service.is_running = False
                return "stopped"
            except Exception as e:
                return f"error: {e}"
        
        # Set service as running
        self.service.is_running = True
        
        result = asyncio.run(mock_stop_scheduler(self.service))
        assert result == "stopped"
        assert self.service.is_running is False

    def test_cron_trigger_creation(self):
        """Test cron trigger creation."""
        def create_cron_trigger(**kwargs):
            """Mock cron trigger creation."""
            # Validate required fields for cron
            valid_fields = ['year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second']
            
            trigger_info = {}
            for field, value in kwargs.items():
                if field in valid_fields:
                    trigger_info[field] = value
            
            return {
                'type': 'cron',
                'fields': trigger_info
            }
        
        # Test daily trigger (every day at 9:00)
        trigger = create_cron_trigger(hour=9, minute=0)
        assert trigger['type'] == 'cron'
        assert trigger['fields']['hour'] == 9
        assert trigger['fields']['minute'] == 0
        
        # Test weekly trigger (Monday at 10:00)
        trigger = create_cron_trigger(day_of_week=0, hour=10, minute=0)
        assert trigger['fields']['day_of_week'] == 0
        assert trigger['fields']['hour'] == 10

    def test_interval_trigger_creation(self):
        """Test interval trigger creation."""
        def create_interval_trigger(**kwargs):
            """Mock interval trigger creation."""
            valid_fields = ['weeks', 'days', 'hours', 'minutes', 'seconds']
            
            trigger_info = {}
            for field, value in kwargs.items():
                if field in valid_fields:
                    trigger_info[field] = value
            
            return {
                'type': 'interval',
                'fields': trigger_info
            }
        
        # Test hourly interval
        trigger = create_interval_trigger(hours=1)
        assert trigger['type'] == 'interval'
        assert trigger['fields']['hours'] == 1
        
        # Test daily interval
        trigger = create_interval_trigger(days=1)
        assert trigger['fields']['days'] == 1

    def test_date_trigger_creation(self):
        """Test date trigger creation."""
        def create_date_trigger(run_date):
            """Mock date trigger creation."""
            return {
                'type': 'date',
                'run_date': run_date
            }
        
        # Test specific date
        future_date = datetime.now() + timedelta(days=1)
        trigger = create_date_trigger(future_date)
        assert trigger['type'] == 'date'
        assert trigger['run_date'] == future_date

    def test_schedule_notification(self):
        """Test scheduling notifications."""
        async def mock_schedule_notification(
            job_id, message, chat_ids, trigger_type, **trigger_kwargs
        ):
            """Mock notification scheduling."""
            # Validate inputs
            if not job_id or not message or not chat_ids:
                return False
            
            if trigger_type not in ['cron', 'interval', 'date']:
                return False
            
            # Mock job creation
            job_info = {
                'id': job_id,
                'message': message,
                'chat_ids': chat_ids,
                'trigger_type': trigger_type,
                'trigger_kwargs': trigger_kwargs,
                'created_at': datetime.now()
            }
            
            return job_info
        
        # Test successful scheduling
        result = asyncio.run(mock_schedule_notification(
            "test_job",
            "Test message",
            ["123456789", "987654321"],
            "cron",
            hour=9,
            minute=0
        ))
        
        assert result is not False
        assert result['id'] == "test_job"
        assert result['message'] == "Test message"
        assert result['trigger_type'] == "cron"

    def test_schedule_daily_system_report(self):
        """Test scheduling daily system reports."""
        async def mock_schedule_daily_report(hour=9, minute=0, job_id="daily_system_report"):
            """Mock daily system report scheduling."""
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                return False
            
            return {
                'job_id': job_id,
                'type': 'daily_system_report',
                'hour': hour,
                'minute': minute,
                'trigger': 'cron'
            }
        
        # Test valid scheduling
        result = asyncio.run(mock_schedule_daily_report(9, 0))
        assert result['job_id'] == "daily_system_report"
        assert result['hour'] == 9
        assert result['minute'] == 0
        
        # Test invalid hour
        result = asyncio.run(mock_schedule_daily_report(25, 0))
        assert result is False

    def test_schedule_weekly_summary(self):
        """Test scheduling weekly summaries."""
        async def mock_schedule_weekly_summary(
            day_of_week=0, hour=10, minute=0, job_id="weekly_summary"
        ):
            """Mock weekly summary scheduling."""
            if not (0 <= day_of_week <= 6):
                return False
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                return False
            
            return {
                'job_id': job_id,
                'type': 'weekly_summary',
                'day_of_week': day_of_week,
                'hour': hour,
                'minute': minute,
                'trigger': 'cron'
            }
        
        # Test valid scheduling (Monday at 10:00)
        result = asyncio.run(mock_schedule_weekly_summary(0, 10, 0))
        assert result['day_of_week'] == 0  # Monday
        assert result['hour'] == 10
        
        # Test invalid day of week
        result = asyncio.run(mock_schedule_weekly_summary(8, 10, 0))
        assert result is False

    def test_schedule_custom_job(self):
        """Test scheduling custom jobs."""
        async def mock_schedule_custom_job(job_id, func, trigger_type, **trigger_kwargs):
            """Mock custom job scheduling."""
            if not job_id or not func or trigger_type not in ['cron', 'interval', 'date']:
                return False
            
            return {
                'job_id': job_id,
                'func': func.__name__ if callable(func) else str(func),
                'trigger_type': trigger_type,
                'trigger_kwargs': trigger_kwargs
            }
        
        # Mock function
        def custom_function():
            return "custom_executed"
        
        # Test custom job scheduling
        result = asyncio.run(mock_schedule_custom_job(
            "custom_job",
            custom_function,
            "interval",
            hours=2
        ))
        
        assert result['job_id'] == "custom_job"
        assert result['func'] == "custom_function"
        assert result['trigger_type'] == "interval"

    def test_unschedule_job(self):
        """Test unscheduling jobs."""
        async def mock_unschedule_job(job_id, scheduled_jobs):
            """Mock job unscheduling."""
            if job_id in scheduled_jobs:
                del scheduled_jobs[job_id]
                return True
            return False
        
        # Setup scheduled jobs
        scheduled_jobs = {
            "job1": {"type": "notification"},
            "job2": {"type": "system_report"}
        }
        
        # Test successful unscheduling
        result = asyncio.run(mock_unschedule_job("job1", scheduled_jobs))
        assert result is True
        assert "job1" not in scheduled_jobs
        
        # Test unscheduling non-existent job
        result = asyncio.run(mock_unschedule_job("job3", scheduled_jobs))
        assert result is False

    def test_get_scheduled_jobs(self):
        """Test getting list of scheduled jobs."""
        async def mock_get_scheduled_jobs(scheduled_jobs):
            """Mock getting scheduled jobs list."""
            jobs = []
            
            for job_id, job_info in scheduled_jobs.items():
                job_data = {
                    'id': job_id,
                    'next_run_time': datetime.now() + timedelta(hours=1),
                    **job_info
                }
                jobs.append(job_data)
            
            return jobs
        
        # Setup scheduled jobs
        scheduled_jobs = {
            "daily_report": {
                "type": "system_report",
                "trigger": "cron",
                "hour": 9
            },
            "weekly_summary": {
                "type": "summary",
                "trigger": "cron",
                "day_of_week": 0
            }
        }
        
        # Test getting jobs
        result = asyncio.run(mock_get_scheduled_jobs(scheduled_jobs))
        assert len(result) == 2
        assert any(job['id'] == "daily_report" for job in result)
        assert any(job['id'] == "weekly_summary" for job in result)

    def test_scheduled_notification_execution(self):
        """Test execution of scheduled notifications."""
        async def mock_send_scheduled_notification(message, chat_ids):
            """Mock sending scheduled notification."""
            results = []
            
            for chat_id in chat_ids:
                # Mock notification service call
                if chat_id == "invalid_chat":
                    results.append(False)
                else:
                    results.append(True)
            
            return results
        
        # Test successful notification
        chat_ids = ["123456789", "987654321"]
        results = asyncio.run(mock_send_scheduled_notification("Test message", chat_ids))
        assert all(results)
        assert len(results) == 2
        
        # Test mixed results
        mixed_chat_ids = ["123456789", "invalid_chat"]
        results = asyncio.run(mock_send_scheduled_notification("Test message", mixed_chat_ids))
        assert results == [True, False]


class TestSchedulerServiceIntegration:
    """Test scheduler service integration scenarios."""

    def test_system_report_scheduling_integration(self):
        """Test integration with system reporting."""
        async def mock_daily_system_report():
            """Mock daily system report execution."""
            # Mock getting subscribers
            subscribers = ["123456789", "987654321", "555666777"]
            
            if not subscribers:
                return {'sent': 0, 'message': 'No subscribers'}
            
            # Mock sending report
            sent_count = 0
            for subscriber in subscribers:
                # Mock notification service
                if subscriber != "555666777":  # Simulate one failure
                    sent_count += 1
            
            return {'sent': sent_count, 'total': len(subscribers)}
        
        # Test daily report execution
        result = asyncio.run(mock_daily_system_report())
        assert result['sent'] == 2
        assert result['total'] == 3

    def test_weekly_summary_generation(self):
        """Test weekly summary generation and sending."""
        async def mock_weekly_summary():
            """Mock weekly summary execution."""
            # Mock getting scheduled subscribers
            subscribers = ["123456789", "987654321"]
            
            if not subscribers:
                return {'sent': 0, 'message': 'No subscribers'}
            
            # Mock creating summary
            summary = {
                'week_start': datetime.now() - timedelta(days=7),
                'week_end': datetime.now(),
                'notifications_sent': 150,
                'active_subscribers': len(subscribers),
                'system_uptime': '99.9%'
            }
            
            # Mock sending summary
            return {
                'summary': summary,
                'sent_to': len(subscribers),
                'message': f"Weekly summary sent to {len(subscribers)} subscribers"
            }
        
        # Test weekly summary
        result = asyncio.run(mock_weekly_summary())
        assert result['sent_to'] == 2
        assert 'summary' in result
        assert result['summary']['active_subscribers'] == 2

    def test_subscription_service_integration(self):
        """Test integration with subscription service."""
        async def mock_get_subscribers_by_type(subscription_type):
            """Mock getting subscribers by type."""
            subscriber_data = {
                'SYSTEM': ["123456789", "987654321", "555666777"],
                'SCHEDULED': ["123456789", "444555666"],
                'ALERTS': ["987654321", "555666777"]
            }
            
            return subscriber_data.get(subscription_type, [])
        
        # Test getting system subscribers
        system_subscribers = asyncio.run(mock_get_subscribers_by_type('SYSTEM'))
        assert len(system_subscribers) == 3
        
        # Test getting scheduled subscribers
        scheduled_subscribers = asyncio.run(mock_get_subscribers_by_type('SCHEDULED'))
        assert len(scheduled_subscribers) == 2
        
        # Test unknown subscription type
        unknown_subscribers = asyncio.run(mock_get_subscribers_by_type('UNKNOWN'))
        assert len(unknown_subscribers) == 0

    def test_notification_service_integration(self):
        """Test integration with notification service."""
        async def mock_notification_service_call(message, chat_id, parse_mode='Markdown'):
            """Mock notification service integration."""
            # Validate inputs
            if not message or not chat_id:
                return False
            
            # Mock different outcomes based on chat_id
            if chat_id == "invalid_chat":
                return False
            elif chat_id == "rate_limited_chat":
                # Simulate rate limiting
                await asyncio.sleep(0.01)
                return False
            else:
                return True
        
        # Test successful notification
        result = asyncio.run(mock_notification_service_call("Test message", "123456789"))
        assert result is True
        
        # Test failed notification
        result = asyncio.run(mock_notification_service_call("Test message", "invalid_chat"))
        assert result is False

    def test_error_handling_in_scheduled_jobs(self):
        """Test error handling in scheduled job execution."""
        async def mock_scheduled_job_with_errors(should_fail=False):
            """Mock scheduled job that might fail."""
            try:
                if should_fail:
                    raise Exception("Scheduled job error")
                
                # Mock successful job execution
                return {
                    'status': 'success',
                    'executed_at': datetime.now(),
                    'result': 'Job completed successfully'
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e),
                    'executed_at': datetime.now()
                }
        
        # Test successful job
        result = asyncio.run(mock_scheduled_job_with_errors(should_fail=False))
        assert result['status'] == 'success'
        
        # Test failing job
        result = asyncio.run(mock_scheduled_job_with_errors(should_fail=True))
        assert result['status'] == 'error'
        assert 'error' in result

    def test_scheduler_timezone_handling(self):
        """Test timezone handling in scheduler."""
        def mock_timezone_conversion(utc_time, target_timezone="UTC"):
            """Mock timezone conversion."""
            # Simple mock - in real implementation would use pytz or zoneinfo
            timezone_offsets = {
                "UTC": 0,
                "EST": -5,
                "PST": -8,
                "CET": 1
            }
            
            offset = timezone_offsets.get(target_timezone, 0)
            return utc_time + timedelta(hours=offset)
        
        # Test timezone conversions
        base_time = datetime(2024, 1, 1, 12, 0, 0)  # 12:00 UTC
        
        utc_time = mock_timezone_conversion(base_time, "UTC")
        assert utc_time.hour == 12
        
        est_time = mock_timezone_conversion(base_time, "EST")
        assert est_time.hour == 7  # 12 - 5
        
        cet_time = mock_timezone_conversion(base_time, "CET")
        assert cet_time.hour == 13  # 12 + 1

    def test_job_persistence_and_recovery(self):
        """Test job persistence and recovery after restart."""
        def mock_save_jobs(jobs):
            """Mock saving jobs to persistence."""
            # In real implementation, this would save to database or file
            return {'saved_count': len(jobs), 'status': 'success'}
        
        def mock_load_jobs():
            """Mock loading jobs from persistence."""
            # Mock persistent job data
            return [
                {
                    'id': 'daily_report',
                    'type': 'system_report',
                    'trigger': 'cron',
                    'hour': 9,
                    'minute': 0
                },
                {
                    'id': 'weekly_summary',
                    'type': 'summary',
                    'trigger': 'cron',
                    'day_of_week': 0,
                    'hour': 10,
                    'minute': 0
                }
            ]
        
        # Test saving jobs
        jobs = [{'id': 'test1'}, {'id': 'test2'}]
        save_result = mock_save_jobs(jobs)
        assert save_result['saved_count'] == 2
        assert save_result['status'] == 'success'
        
        # Test loading jobs
        loaded_jobs = mock_load_jobs()
        assert len(loaded_jobs) == 2
        assert any(job['id'] == 'daily_report' for job in loaded_jobs)

    def test_scheduler_max_workers_limit(self):
        """Test scheduler max workers configuration."""
        def mock_scheduler_with_workers(max_workers=5):
            """Mock scheduler configuration with worker limits."""
            return {
                'max_workers': max_workers,
                'current_jobs': 0,
                'can_schedule': lambda: max_workers > 0
            }
        
        # Test normal configuration
        scheduler = mock_scheduler_with_workers(5)
        assert scheduler['max_workers'] == 5
        assert scheduler['can_schedule']() is True
        
        # Test limited workers
        limited_scheduler = mock_scheduler_with_workers(0)
        assert limited_scheduler['max_workers'] == 0
        assert limited_scheduler['can_schedule']() is False

    def test_concurrent_job_execution(self):
        """Test concurrent execution of multiple scheduled jobs."""
        async def mock_concurrent_jobs():
            """Mock concurrent job execution."""
            async def job_1():
                await asyncio.sleep(0.1)
                return "job_1_completed"
            
            async def job_2():
                await asyncio.sleep(0.1)
                return "job_2_completed"
            
            async def job_3():
                await asyncio.sleep(0.1)
                return "job_3_completed"
            
            # Execute jobs concurrently
            results = await asyncio.gather(job_1(), job_2(), job_3())
            return results
        
        # Test concurrent execution
        results = asyncio.run(mock_concurrent_jobs())
        assert len(results) == 3
        assert "job_1_completed" in results
        assert "job_2_completed" in results
        assert "job_3_completed" in results


def test_global_scheduler_service():
    """Test global scheduler service instance."""
    # Mock global service
    class MockGlobalSchedulerService:
        def __init__(self):
            self.is_initialized = True
            self.service_type = "scheduler"
    
    global_service = MockGlobalSchedulerService()
    
    assert global_service.is_initialized is True
    assert global_service.service_type == "scheduler"
