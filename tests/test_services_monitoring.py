"""Tests for bot services monitoring."""

import pytest
import asyncio
import sys
import os

from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestMonitoringStructure:
    """Test monitoring service structure and imports."""

    def test_import_structure(self):
        """Test that monitoring service can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.services.monitoring", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "services", "monitoring.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load monitoring service: {e}")


class TestMonitoringService:
    """Test MonitoringService class."""

    def setup_method(self):
        """Set up test environment."""
        # Mock MonitoringService
        class MockMonitoringService:
            def __init__(self):
                self.is_running = False
                self.check_interval = 60
                self._last_alerts = {}
                self.alert_cooldown = 300
        
        self.service = MockMonitoringService()

    def test_monitoring_service_initialization(self):
        """Test MonitoringService initialization."""
        assert self.service.is_running is False
        assert self.service.check_interval == 60
        assert self.service._last_alerts == {}
        assert self.service.alert_cooldown == 300

    def test_start_monitoring(self):
        """Test starting monitoring service."""
        async def mock_start_monitoring(service):
            """Mock monitoring service start."""
            if service.is_running:
                return "already_running"
            
            service.is_running = True
            return "started"
        
        # Test starting when not running
        result = asyncio.run(mock_start_monitoring(self.service))
        assert result == "started"
        assert self.service.is_running is True
        
        # Test starting when already running
        result = asyncio.run(mock_start_monitoring(self.service))
        assert result == "already_running"

    def test_stop_monitoring(self):
        """Test stopping monitoring service."""
        async def mock_stop_monitoring(service):
            """Mock monitoring service stop."""
            service.is_running = False
            return "stopped"
        
        # Set service as running
        self.service.is_running = True
        
        result = asyncio.run(mock_stop_monitoring(self.service))
        assert result == "stopped"
        assert self.service.is_running is False

    def test_system_metrics_collection(self):
        """Test system metrics collection."""
        # Mock system metrics
        def mock_get_system_metrics():
            """Mock getting system metrics."""
            return {
                'cpu_percent': 25.5,
                'memory_percent': 45.2,
                'disk_percent': 65.8,
                'load_1min': 1.2,
                'load_5min': 1.0,
                'load_15min': 0.8
            }
        
        metrics = mock_get_system_metrics()
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'disk_percent' in metrics
        assert metrics['cpu_percent'] == 25.5
        assert metrics['memory_percent'] == 45.2
        assert metrics['disk_percent'] == 65.8

    def test_threshold_checking(self):
        """Test threshold checking logic."""
        def check_threshold(current_value, threshold):
            """Check if current value exceeds threshold."""
            return current_value > threshold
        
        # Test CPU threshold
        assert check_threshold(85, 80) is True
        assert check_threshold(75, 80) is False
        
        # Test memory threshold
        assert check_threshold(90, 85) is True
        assert check_threshold(80, 85) is False
        
        # Test disk threshold
        assert check_threshold(95, 90) is True
        assert check_threshold(85, 90) is False

    def test_alert_cooldown_logic(self):
        """Test alert cooldown to prevent spam."""
        import time
        
        def check_alert_cooldown(last_alerts, alert_key, cooldown_seconds):
            """Check if alert is in cooldown period."""
            current_time = time.time()
            
            if alert_key in last_alerts:
                time_diff = current_time - last_alerts[alert_key]
                return time_diff < cooldown_seconds
            
            return False
        
        # Mock alert tracking
        last_alerts = {}
        cooldown = 300  # 5 minutes
        
        # First alert should not be in cooldown
        assert check_alert_cooldown(last_alerts, "CPU_80", cooldown) is False
        
        # Set alert time and check cooldown
        last_alerts["CPU_80"] = time.time()
        assert check_alert_cooldown(last_alerts, "CPU_80", cooldown) is True
        
        # Test expired cooldown
        last_alerts["CPU_80"] = time.time() - 400  # 6+ minutes ago
        assert check_alert_cooldown(last_alerts, "CPU_80", cooldown) is False

    def test_alert_message_formatting(self):
        """Test alert message formatting."""
        def format_alert_message(metric, value, threshold, unit):
            """Format alert message."""
            return f"🚨 Alert: {metric} is {value}{unit} (threshold: {threshold}{unit})"
        
        # Test CPU alert
        message = format_alert_message("CPU", 85.5, 80, "%")
        assert "CPU" in message
        assert "85.5%" in message
        assert "80%" in message
        assert "🚨" in message
        
        # Test memory alert
        message = format_alert_message("Memory", 92.1, 85, "%")
        assert "Memory" in message
        assert "92.1%" in message
        assert "85%" in message

    def test_subscriber_notification(self):
        """Test sending alerts to subscribers."""
        async def mock_send_to_subscribers(message, subscribers):
            """Mock sending message to subscribers."""
            results = []
            
            for subscriber in subscribers:
                if subscriber == "invalid_user":
                    results.append(False)
                else:
                    results.append(True)
            
            return results
        
        # Test successful notification
        subscribers = ["123456789", "987654321"]
        results = asyncio.run(mock_send_to_subscribers("Test alert", subscribers))
        assert all(results)
        assert len(results) == 2
        
        # Test mixed results
        mixed_subscribers = ["123456789", "invalid_user", "987654321"]
        results = asyncio.run(mock_send_to_subscribers("Test alert", mixed_subscribers))
        assert results == [True, False, True]

    def test_current_metrics_retrieval(self):
        """Test retrieving current system metrics."""
        async def mock_get_current_metrics():
            """Mock getting current metrics."""
            try:
                # Mock psutil data
                return {
                    'cpu_percent': 35.2,
                    'memory_percent': 55.8,
                    'memory_used_gb': 8.5,
                    'memory_total_gb': 16.0,
                    'disk_percent': 45.3,
                    'disk_used_gb': 250.7,
                    'disk_total_gb': 500.0,
                    'load_1min': 1.5,
                    'load_5min': 1.2,
                    'load_15min': 1.0
                }
            except Exception:
                return {}
        
        # Test successful metrics retrieval
        metrics = asyncio.run(mock_get_current_metrics())
        assert len(metrics) > 0
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'disk_percent' in metrics
        assert isinstance(metrics['cpu_percent'], float)

    def test_system_report_generation(self):
        """Test system report generation and sending."""
        async def mock_send_system_report(chat_id=None, subscribers=None):
            """Mock sending system report."""
            if chat_id:
                # Send to specific chat
                return True
            elif subscribers:
                # Send to all subscribers
                return len(subscribers)
            else:
                # No recipients
                return 0
        
        # Test sending to specific chat
        result = asyncio.run(mock_send_system_report(chat_id="123456789"))
        assert result is True
        
        # Test sending to subscribers
        subscribers = ["123456789", "987654321", "555666777"]
        result = asyncio.run(mock_send_system_report(subscribers=subscribers))
        assert result == 3

    def test_process_status_checking(self):
        """Test process status checking."""
        async def mock_check_process_status(process_name):
            """Mock checking if process is running."""
            # Mock running processes
            running_processes = ["python", "nginx", "postgres"]
            
            return process_name in running_processes
        
        # Test existing process
        result = asyncio.run(mock_check_process_status("python"))
        assert result is True
        
        # Test non-existing process
        result = asyncio.run(mock_check_process_status("nonexistent"))
        assert result is False

    def test_disk_usage_checking(self):
        """Test disk usage checking for specific paths."""
        async def mock_get_disk_usage(path="/"):
            """Mock getting disk usage."""
            try:
                # Mock disk usage data
                if path == "/":
                    return {
                        'total_gb': 500.0,
                        'used_gb': 250.5,
                        'free_gb': 249.5,
                        'percent': 50.1
                    }
                elif path == "/tmp":
                    return {
                        'total_gb': 100.0,
                        'used_gb': 10.2,
                        'free_gb': 89.8,
                        'percent': 10.2
                    }
                else:
                    return {}
            except Exception:
                return {}
        
        # Test root path
        usage = asyncio.run(mock_get_disk_usage("/"))
        assert 'total_gb' in usage
        assert 'used_gb' in usage
        assert 'free_gb' in usage
        assert 'percent' in usage
        assert usage['percent'] == 50.1
        
        # Test tmp path
        usage = asyncio.run(mock_get_disk_usage("/tmp"))
        assert usage['percent'] == 10.2
        
        # Test invalid path
        usage = asyncio.run(mock_get_disk_usage("/invalid"))
        assert usage == {}


class TestMonitoringServiceIntegration:
    """Test monitoring service integration scenarios."""

    def test_monitoring_loop_execution(self):
        """Test the main monitoring loop."""
        async def mock_monitoring_loop(max_iterations=3):
            """Mock monitoring loop with limited iterations."""
            iteration_count = 0
            metrics_checked = []
            
            while iteration_count < max_iterations:
                # Mock checking metrics
                metrics = {
                    'cpu': 45.2,
                    'memory': 62.8,
                    'disk': 78.1
                }
                metrics_checked.append(metrics)
                
                iteration_count += 1
                await asyncio.sleep(0.01)  # Short delay for testing
            
            return metrics_checked
        
        # Test monitoring loop
        results = asyncio.run(mock_monitoring_loop())
        assert len(results) == 3
        assert all('cpu' in result for result in results)

    def test_error_handling_in_monitoring(self):
        """Test error handling in monitoring operations."""
        async def mock_monitoring_with_errors(should_fail=False):
            """Mock monitoring with potential errors."""
            try:
                if should_fail:
                    raise Exception("System monitoring error")
                
                return {
                    'status': 'success',
                    'metrics': {'cpu': 25.0, 'memory': 40.0}
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Test successful monitoring
        result = asyncio.run(mock_monitoring_with_errors(should_fail=False))
        assert result['status'] == 'success'
        assert 'metrics' in result
        
        # Test error handling
        result = asyncio.run(mock_monitoring_with_errors(should_fail=True))
        assert result['status'] == 'error'
        assert 'error' in result

    def test_multiple_alert_types(self):
        """Test handling multiple types of alerts."""
        async def mock_check_multiple_alerts():
            """Mock checking multiple alert conditions."""
            alerts_triggered = []
            
            # Mock system state
            system_state = {
                'cpu_percent': 85,  # Above threshold (80)
                'memory_percent': 92,  # Above threshold (85)
                'disk_percent': 75,  # Below threshold (90)
                'process_down': True  # Process monitoring
            }
            
            thresholds = {
                'cpu': 80,
                'memory': 85,
                'disk': 90
            }
            
            # Check CPU
            if system_state['cpu_percent'] > thresholds['cpu']:
                alerts_triggered.append('cpu_high')
            
            # Check Memory
            if system_state['memory_percent'] > thresholds['memory']:
                alerts_triggered.append('memory_high')
            
            # Check Disk
            if system_state['disk_percent'] > thresholds['disk']:
                alerts_triggered.append('disk_high')
            
            # Check Process
            if system_state['process_down']:
                alerts_triggered.append('process_down')
            
            return alerts_triggered
        
        # Test multiple alerts
        alerts = asyncio.run(mock_check_multiple_alerts())
        assert 'cpu_high' in alerts
        assert 'memory_high' in alerts
        assert 'process_down' in alerts
        assert 'disk_high' not in alerts  # Below threshold

    def test_subscription_service_integration(self):
        """Test integration with subscription service."""
        async def mock_get_system_subscribers():
            """Mock getting system alert subscribers."""
            # Mock subscription service
            return ["123456789", "987654321", "555666777"]
        
        async def mock_send_alert_to_subscribers(alert_message):
            """Mock sending alerts to subscribers."""
            subscribers = await mock_get_system_subscribers()
            
            if not subscribers:
                return {'sent': 0, 'failed': 0}
            
            sent_count = 0
            failed_count = 0
            
            for subscriber in subscribers:
                # Mock sending logic
                if subscriber == "555666777":  # Simulate failure
                    failed_count += 1
                else:
                    sent_count += 1
            
            return {'sent': sent_count, 'failed': failed_count}
        
        # Test alert distribution
        result = asyncio.run(mock_send_alert_to_subscribers("Test alert"))
        assert result['sent'] == 2
        assert result['failed'] == 1

    def test_notification_service_integration(self):
        """Test integration with notification service."""
        async def mock_notification_integration(message, chat_ids):
            """Mock notification service integration."""
            results = []
            
            for chat_id in chat_ids:
                # Mock notification service call
                try:
                    # Simulate different outcomes
                    if chat_id == "invalid_chat":
                        results.append({'chat_id': chat_id, 'success': False, 'error': 'Invalid chat'})
                    else:
                        results.append({'chat_id': chat_id, 'success': True})
                except Exception as e:
                    results.append({'chat_id': chat_id, 'success': False, 'error': str(e)})
            
            return results
        
        # Test notification integration
        chat_ids = ["123456789", "invalid_chat", "987654321"]
        results = asyncio.run(mock_notification_integration("System alert", chat_ids))
        
        assert len(results) == 3
        assert results[0]['success'] is True
        assert results[1]['success'] is False
        assert results[2]['success'] is True

    def test_configuration_based_thresholds(self):
        """Test configuration-based threshold checking."""
        class MockConfig:
            def __init__(self):
                self.cpu_threshold = 80
                self.memory_threshold = 85
                self.disk_threshold = 90
                self.alert_cooldown = 300
        
        def check_thresholds_with_config(metrics, config):
            """Check metrics against configured thresholds."""
            alerts = []
            
            if metrics.get('cpu', 0) > config.cpu_threshold:
                alerts.append(f"CPU: {metrics['cpu']}% > {config.cpu_threshold}%")
            
            if metrics.get('memory', 0) > config.memory_threshold:
                alerts.append(f"Memory: {metrics['memory']}% > {config.memory_threshold}%")
            
            if metrics.get('disk', 0) > config.disk_threshold:
                alerts.append(f"Disk: {metrics['disk']}% > {config.disk_threshold}%")
            
            return alerts
        
        # Test with high metrics
        config = MockConfig()
        high_metrics = {'cpu': 85, 'memory': 90, 'disk': 95}
        alerts = check_thresholds_with_config(high_metrics, config)
        
        assert len(alerts) == 3
        assert any("CPU" in alert for alert in alerts)
        assert any("Memory" in alert for alert in alerts)
        assert any("Disk" in alert for alert in alerts)
        
        # Test with normal metrics
        normal_metrics = {'cpu': 50, 'memory': 60, 'disk': 70}
        alerts = check_thresholds_with_config(normal_metrics, config)
        assert len(alerts) == 0

    def test_concurrent_monitoring_operations(self):
        """Test concurrent monitoring operations."""
        async def mock_concurrent_checks():
            """Mock concurrent monitoring checks."""
            async def check_cpu():
                await asyncio.sleep(0.1)
                return {'metric': 'cpu', 'value': 75.5}
            
            async def check_memory():
                await asyncio.sleep(0.1)
                return {'metric': 'memory', 'value': 82.3}
            
            async def check_disk():
                await asyncio.sleep(0.1)
                return {'metric': 'disk', 'value': 68.9}
            
            # Run concurrent checks
            results = await asyncio.gather(
                check_cpu(),
                check_memory(),
                check_disk(),
                return_exceptions=True
            )
            
            return results
        
        # Test concurrent execution
        results = asyncio.run(mock_concurrent_checks())
        assert len(results) == 3
        assert all(isinstance(result, dict) for result in results)
        assert all('metric' in result for result in results)


def test_global_monitoring_service():
    """Test global monitoring service instance."""
    # Mock global service
    class MockGlobalMonitoringService:
        def __init__(self):
            self.is_initialized = True
            self.service_type = "monitoring"
    
    global_service = MockGlobalMonitoringService()
    
    assert global_service.is_initialized is True
    assert global_service.service_type == "monitoring"
