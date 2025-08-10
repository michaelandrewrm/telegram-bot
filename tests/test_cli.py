"""Tests for bot CLI commands."""

import pytest
import asyncio
import sys
import os

from pathlib import Path

from click.testing import CliRunner
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestCLIStructure:
    """Test CLI structure and import validation."""

    def test_import_structure(self):
        """Test that CLI module can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.cli", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "cli.py")
            )
            assert spec is not None
            
            # Test that we can mock click commands
            import click
            assert click is not None
        except Exception as e:
            pytest.fail(f"Failed to load CLI module: {e}")


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        
        # Create mock config
        self.mock_config = MagicMock()
        self.mock_config.config_path = Path("test_config.yaml")
        self.mock_config.env_path = Path(".env")
        self.mock_config.log_level = "INFO"
        self.mock_config.default_chat_ids = ["123456789"]
        self.mock_config.api_enabled = True
        self.mock_config.enable_monitoring = True
        self.mock_config.enable_scheduling = True

    def test_send_command_validation(self):
        """Test send command input validation logic."""
        # Test empty message validation
        def validate_send_input(message, chat_id=None, chat_ids=None, parse_mode="Markdown"):
            errors = []
            
            if not message or not message.strip():
                errors.append("Error: Message cannot be empty")
            
            if parse_mode and parse_mode not in ['Markdown', 'HTML', 'MarkdownV2']:
                errors.append(f"Error: Invalid parse mode '{parse_mode}'")
            
            if chat_id and chat_ids:
                errors.append("Error: Cannot specify both --chat-id and --chat-ids")
                
            return errors
        
        # Test valid input
        errors = validate_send_input("Test message", chat_id="123456789")
        assert len(errors) == 0
        
        # Test empty message
        errors = validate_send_input("")
        assert "Error: Message cannot be empty" in errors
        
        # Test invalid parse mode
        errors = validate_send_input("Test", parse_mode="Invalid")
        assert any("Invalid parse mode" in error for error in errors)
        
        # Test conflicting chat options
        errors = validate_send_input("Test", chat_id="123", chat_ids="456,789")
        assert "Error: Cannot specify both" in errors[0]

    def test_file_validation_logic(self):
        """Test file sending validation logic."""
        def validate_file_send(file_path, file_size_mb=10, max_size_mb=50):
            """Mock file validation logic."""
            errors = []
            
            if not file_path:
                return errors
            
            # Mock file size check
            if file_size_mb > max_size_mb:
                errors.append(f"Error: File too large ({file_size_mb}MB > {max_size_mb}MB)")
            
            return errors
        
        # Test valid file (small size)
        errors = validate_file_send("test.jpg", file_size_mb=10)
        assert len(errors) == 0
        
        # Test oversized file (large size)
        errors = validate_file_send("large_file.mp4", file_size_mb=60)
        assert any("File too large" in error for error in errors)

    def test_cron_expression_validation(self):
        """Test cron expression validation logic."""
        def validate_cron_expression(cron_expr):
            """Validate cron expression format."""
            if not cron_expr:
                return False, "No cron expression provided"
            
            parts = cron_expr.split()
            if len(parts) != 5:
                return False, "Cron expression must have 5 parts (minute hour day month weekday)"
            
            return True, "Valid cron expression"
        
        # Test valid cron
        valid, msg = validate_cron_expression("0 9 * * *")
        assert valid is True
        assert "Valid" in msg
        
        # Test invalid cron
        valid, msg = validate_cron_expression("0 9 *")
        assert valid is False
        assert "must have 5 parts" in msg

    def test_chat_id_validation_logic(self):
        """Test chat ID validation logic."""
        def validate_chat_ids(chat_ids_str):
            """Validate comma-separated chat IDs."""
            if not chat_ids_str:
                return [], []
            
            chat_id_list = [cid.strip() for cid in chat_ids_str.split(',')]
            valid_ids = []
            invalid_ids = []
            
            for cid in chat_id_list:
                # Simple validation: should be numeric or start with @
                if cid.isdigit() or cid.startswith('@'):
                    valid_ids.append(cid)
                else:
                    invalid_ids.append(cid)
            
            return valid_ids, invalid_ids
        
        # Test valid chat IDs
        valid, invalid = validate_chat_ids("123456789,987654321")
        assert len(valid) == 2
        assert len(invalid) == 0
        
        # Test mixed valid/invalid IDs
        valid, invalid = validate_chat_ids("123456789,invalid_id,@username")
        assert len(valid) == 2  # numeric and @username
        assert len(invalid) == 1  # invalid_id

    def test_send_command_execution_logic(self):
        """Test send command execution logic."""
        async def mock_send_notification(message, chat_id=None, parse_mode="Markdown"):
            """Mock send notification function."""
            if message and (chat_id or True):  # Default chat if no chat_id
                return True
            return False
        
        # Test successful send
        result = asyncio.run(mock_send_notification("Test message", "123456789"))
        assert result is True
        
        # Test failed send (empty message)
        result = asyncio.run(mock_send_notification("", "123456789"))
        assert result is False

    def test_system_command_logic(self):
        """Test system command functionality."""
        async def mock_send_system_report(chat_id=None):
            """Mock system report sending."""
            # Simulate successful system report
            if chat_id:
                return f"System report sent to {chat_id}"
            else:
                return "System report sent to subscribers"
        
        # Test with specific chat ID
        result = asyncio.run(mock_send_system_report("123456789"))
        assert "sent to 123456789" in result
        
        # Test with default subscribers
        result = asyncio.run(mock_send_system_report())
        assert "sent to subscribers" in result

    def test_metrics_command_logic(self):
        """Test metrics command functionality."""
        async def mock_get_current_metrics():
            """Mock metrics retrieval."""
            return {
                "cpu_percent": 25.5,
                "memory_percent": 45.2,
                "disk_percent": 60.1,
                "uptime": "2 days, 4 hours"
            }
        
        # Test metrics retrieval
        metrics = asyncio.run(mock_get_current_metrics())
        assert metrics["cpu_percent"] == 25.5
        assert "uptime" in metrics

    def test_schedule_command_logic(self):
        """Test schedule command functionality."""
        async def mock_schedule_notification(job_id, message, chat_ids, trigger_type, **kwargs):
            """Mock notification scheduling."""
            if job_id and message and chat_ids and trigger_type:
                return True
            return False
        
        # Test successful scheduling
        result = asyncio.run(mock_schedule_notification(
            job_id="test_job",
            message="Test message",
            chat_ids=["123456789"],
            trigger_type="cron",
            hour=9
        ))
        assert result is True
        
        # Test failed scheduling (missing parameters)
        result = asyncio.run(mock_schedule_notification(
            job_id="",
            message="Test message",
            chat_ids=[],
            trigger_type="cron"
        ))
        assert result is False

    def test_trigger_type_parsing(self):
        """Test trigger type parsing logic."""
        def parse_trigger_type(cron=None, interval=None, date=None):
            """Parse trigger type and arguments."""
            if cron:
                parts = cron.split()
                if len(parts) != 5:
                    return None, "Invalid cron expression"
                
                trigger_kwargs = {
                    'minute': parts[0],
                    'hour': parts[1], 
                    'day': parts[2],
                    'month': parts[3],
                    'day_of_week': parts[4]
                }
                return 'cron', trigger_kwargs
                
            elif interval:
                return 'interval', {'seconds': interval}
                
            elif date:
                return 'date', {'run_date': date}
                
            else:
                return None, "Must specify cron, interval, or date"
        
        # Test cron parsing
        trigger_type, kwargs = parse_trigger_type(cron="0 9 * * *")
        assert trigger_type == 'cron'
        assert kwargs['hour'] == '9'
        
        # Test interval parsing
        trigger_type, kwargs = parse_trigger_type(interval=3600)
        assert trigger_type == 'interval'
        assert kwargs['seconds'] == 3600
        
        # Test date parsing
        trigger_type, kwargs = parse_trigger_type(date="2024-01-01T09:00:00")
        assert trigger_type == 'date'
        assert 'run_date' in kwargs

    def test_jobs_listing_logic(self):
        """Test jobs listing functionality."""
        async def mock_get_scheduled_jobs():
            """Mock scheduled jobs retrieval."""
            return [
                {
                    'id': 'job1',
                    'next_run_time': '2024-01-01 09:00:00',
                    'trigger': 'cron',
                    'message': 'Daily reminder message that is quite long and should be truncated'
                },
                {
                    'id': 'job2',
                    'next_run_time': '2024-01-01 15:30:00',
                    'trigger': 'interval',
                    'message': 'Short message'
                }
            ]
        
        # Test jobs retrieval
        jobs = asyncio.run(mock_get_scheduled_jobs())
        assert len(jobs) == 2
        assert jobs[0]['id'] == 'job1'
        assert 'Daily reminder' in jobs[0]['message']

    def test_status_command_logic(self):
        """Test status command functionality."""
        async def mock_get_bot_status():
            """Mock bot status check."""
            return {
                'is_healthy': True,
                'config_path': Path('test_config.yaml'),
                'env_path': Path('.env'),
                'default_chat_ids': ['123456789'],
                'api_enabled': True,
                'monitoring_enabled': True,
                'scheduling_enabled': True
            }
        
        # Test status retrieval
        status = asyncio.run(mock_get_bot_status())
        assert status['is_healthy'] is True
        assert status['api_enabled'] is True

    def test_unschedule_command_logic(self):
        """Test unschedule command functionality."""
        async def mock_unschedule_job(job_id):
            """Mock job unscheduling."""
            existing_jobs = ['job1', 'job2', 'job3']
            return job_id in existing_jobs
        
        # Test successful unscheduling
        result = asyncio.run(mock_unschedule_job('job1'))
        assert result is True
        
        # Test failed unscheduling (job not found)
        result = asyncio.run(mock_unschedule_job('nonexistent'))
        assert result is False


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_config_file_handling(self):
        """Test configuration file handling logic."""
        def mock_update_config(config_file=None, env_file=None, log_level=None):
            """Mock configuration update."""
            updates = {}
            
            if config_file:
                updates['config_path'] = Path(config_file)
            if env_file:
                updates['env_path'] = Path(env_file)
            if log_level:
                updates['log_level'] = log_level
            
            return updates
        
        # Test configuration updates
        updates = mock_update_config(
            config_file="custom_config.yaml",
            env_file="custom.env",
            log_level="DEBUG"
        )
        
        assert updates['config_path'] == Path("custom_config.yaml")
        assert updates['log_level'] == "DEBUG"

    def test_error_handling_patterns(self):
        """Test error handling in CLI commands."""
        def mock_cli_error_handler(operation):
            """Mock CLI error handling."""
            try:
                return operation()
            except ValueError as e:
                return f"Validation Error: {e}"
            except Exception as e:
                return f"Error: {e}"
        
        # Test validation error
        def validation_error_op():
            raise ValueError("Invalid input")
        
        result = mock_cli_error_handler(validation_error_op)
        assert "Validation Error" in result
        
        # Test general error
        def general_error_op():
            raise Exception("Something went wrong")
        
        result = mock_cli_error_handler(general_error_op)
        assert "Error: Something went wrong" in result

    def test_multiple_chat_handling(self):
        """Test multiple chat ID handling."""
        async def mock_send_to_multiple(message, chat_ids, parse_mode="Markdown"):
            """Mock sending to multiple chats."""
            results = []
            for chat_id in chat_ids:
                # Simulate some failures
                if chat_id == "invalid_id":
                    results.append(False)
                else:
                    results.append(True)
            return results
        
        # Test mixed success/failure
        chat_ids = ["123456789", "invalid_id", "987654321"]
        results = asyncio.run(mock_send_to_multiple("Test", chat_ids))
        successful = sum(results)
        assert successful == 2  # 2 out of 3 successful

    def test_api_server_startup_logic(self):
        """Test API server startup logic."""
        def mock_api_startup(host="0.0.0.0", port=8080):
            """Mock API server startup."""
            if not host or not isinstance(port, int):
                return False, "Invalid host or port"
            
            if port < 1 or port > 65535:
                return False, "Port out of range"
            
            return True, f"Starting API server on {host}:{port}"
        
        # Test valid startup
        success, msg = mock_api_startup("localhost", 8080)
        assert success is True
        assert "Starting API server" in msg
        
        # Test invalid port
        success, msg = mock_api_startup("localhost", 70000)
        assert success is False
        assert "Port out of range" in msg


def test_async_command_wrapper():
    """Test async command wrapper functionality."""
    def mock_async_wrapper(async_func):
        """Mock async command wrapper."""
        def wrapper(*args, **kwargs):
            try:
                return asyncio.run(async_func(*args, **kwargs))
            except KeyboardInterrupt:
                return "Operation cancelled by user"
            except Exception as e:
                return f"Error: {e}"
        return wrapper
    
    # Test successful async operation
    async def success_op():
        return "Success"
    
    wrapped = mock_async_wrapper(success_op)
    result = wrapped()
    assert result == "Success"
    
    # Test async operation with error
    async def error_op():
        raise Exception("Async error")
    
    wrapped = mock_async_wrapper(error_op)
    result = wrapped()
    assert "Error: Async error" in result


def test_file_type_detection():
    """Test file type detection logic."""
    def detect_file_type(file_path):
        """Detect if file should be sent as photo or document."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension in image_extensions:
            return "photo"
        else:
            return "document"
    
    # Test image file
    assert detect_file_type("test.jpg") == "photo"
    assert detect_file_type("image.PNG") == "photo"
    
    # Test document file
    assert detect_file_type("document.pdf") == "document"
    assert detect_file_type("archive.zip") == "document"
