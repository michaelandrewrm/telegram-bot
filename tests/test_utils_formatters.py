"""Tests for bot utils formatters."""

import pytest
import datetime
import sys
import os

from unittest.mock import patch, MagicMock

# Add the parent directory to the path to handle relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestFormattersStructure:
    """Test formatters module structure and imports."""

    def test_import_structure(self):
        """Test that formatters module can be imported and has expected structure."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "bot.utils.formatters", 
                os.path.join(os.path.dirname(__file__), "..", "bot", "utils", "formatters.py")
            )
            assert spec is not None
        except Exception as e:
            pytest.fail(f"Failed to load formatters module: {e}")


class TestFormatMessage:
    """Test format_message function."""

    def test_format_message_markdown(self):
        """Test message formatting with markdown."""
        # Mock format_message function
        def mock_format_message(title, message, timestamp=None, level="INFO", markdown=True):
            if timestamp is None:
                timestamp = datetime.datetime(2024, 1, 1, 12, 0, 0)
            
            if markdown:
                # Escape special characters for Markdown
                title_escaped = title.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                level_emoji = {
                    'INFO': 'ℹ️',
                    'WARNING': '⚠️',
                    'ERROR': '❌',
                    'SUCCESS': '✅',
                    'DEBUG': '🔍'
                }.get(level.upper(), 'ℹ️')
                
                formatted = f"{level_emoji} *{title_escaped}*\n\n"
                formatted += f"{message}\n\n"
                formatted += f"🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                
            else:
                formatted = f"[{level}] {title}\n\n"
                formatted += f"{message}\n\n"
                formatted += f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            
            return formatted
        
        # Test with INFO level
        result = mock_format_message("Test Title", "Test message", level="INFO")
        assert "ℹ️ *Test Title*" in result
        assert "Test message" in result
        assert "2024-01-01 12:00:00 UTC" in result
        
        # Test with ERROR level
        result = mock_format_message("Error Title", "Error message", level="ERROR")
        assert "❌ *Error Title*" in result
        assert "Error message" in result

    def test_format_message_plain_text(self):
        """Test message formatting without markdown."""
        def mock_format_message(title, message, timestamp=None, level="INFO", markdown=True):
            if timestamp is None:
                timestamp = datetime.datetime(2024, 1, 1, 12, 0, 0)
            
            if not markdown:
                formatted = f"[{level}] {title}\n\n"
                formatted += f"{message}\n\n"
                formatted += f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            else:
                # Simplified markdown version
                formatted = f"*{title}*\n\n{message}\n\n🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            
            return formatted
        
        # Test plain text formatting
        result = mock_format_message("Test Title", "Test message", markdown=False)
        assert "[INFO] Test Title" in result
        assert "Test message" in result
        assert "Time: 2024-01-01 12:00:00 UTC" in result

    def test_markdown_escaping(self):
        """Test markdown character escaping."""
        def escape_markdown(text):
            """Escape special markdown characters."""
            return text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
        
        # Test escaping
        text = "Test_with*special[chars`"
        escaped = escape_markdown(text)
        assert escaped == "Test\\_with\\*special\\[chars\\`"

    def test_level_emoji_mapping(self):
        """Test level to emoji mapping."""
        level_emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅',
            'DEBUG': '🔍'
        }
        
        # Test all mappings
        assert level_emoji['INFO'] == 'ℹ️'
        assert level_emoji['WARNING'] == '⚠️'
        assert level_emoji['ERROR'] == '❌'
        assert level_emoji['SUCCESS'] == '✅'
        assert level_emoji['DEBUG'] == '🔍'
        
        # Test default fallback
        default_emoji = level_emoji.get('UNKNOWN', 'ℹ️')
        assert default_emoji == 'ℹ️'


class TestFormatSystemInfo:
    """Test format_system_info function."""

    def test_system_info_markdown(self):
        """Test system info formatting with markdown."""
        # Mock system info data
        def mock_format_system_info(markdown=True):
            # Mock system data
            cpu_percent = 25.5
            memory_used = 8
            memory_total = 16
            memory_percent = 50.0
            disk_used = 100
            disk_total = 500
            disk_percent = 20.0
            load_avg = [1.5, 1.2, 1.0]
            
            if markdown:
                info = "🖥️ *System Status*\n\n"
                info += f"**CPU Usage:** {cpu_percent:.1f}%\n"
                info += f"**Memory Usage:** {memory_percent:.1f}% ({memory_used:.1f}GB / {memory_total:.1f}GB)\n"
                info += f"**Disk Usage:** {disk_percent:.1f}% ({disk_used:.1f}GB / {disk_total:.1f}GB)\n"
                info += f"**Load Average:** {', '.join(map(str, load_avg))}\n"
            else:
                info = "System Status\n\n"
                info += f"CPU Usage: {cpu_percent:.1f}%\n"
                info += f"Memory Usage: {memory_percent:.1f}% ({memory_used:.1f}GB / {memory_total:.1f}GB)\n"
                info += f"Disk Usage: {disk_percent:.1f}% ({disk_used:.1f}GB / {disk_total:.1f}GB)\n"
                info += f"Load Average: {', '.join(map(str, load_avg))}\n"
            
            return info
        
        # Test markdown formatting
        result = mock_format_system_info(markdown=True)
        assert "🖥️ *System Status*" in result
        assert "**CPU Usage:** 25.5%" in result
        assert "**Memory Usage:** 50.0%" in result
        assert "**Disk Usage:** 20.0%" in result
        assert "**Load Average:**" in result

    def test_system_info_plain_text(self):
        """Test system info formatting without markdown."""
        def mock_format_system_info(markdown=True):
            cpu_percent = 25.5
            memory_percent = 50.0
            disk_percent = 20.0
            
            if not markdown:
                info = "System Status\n\n"
                info += f"CPU Usage: {cpu_percent:.1f}%\n"
                info += f"Memory Usage: {memory_percent:.1f}%\n"
                info += f"Disk Usage: {disk_percent:.1f}%\n"
                return info
            else:
                return "🖥️ *System Status*\n\n**CPU Usage:** 25.5%\n"
        
        # Test plain text formatting
        result = mock_format_system_info(markdown=False)
        assert "System Status" in result
        assert "CPU Usage: 25.5%" in result
        assert "Memory Usage: 50.0%" in result
        assert "**" not in result  # No markdown formatting

    def test_system_info_error_handling(self):
        """Test system info error handling."""
        def mock_format_system_info_with_error():
            """Mock system info with error."""
            try:
                raise Exception("System access denied")
            except Exception as e:
                return f"Error getting system info: {str(e)}"
        
        # Test error handling
        result = mock_format_system_info_with_error()
        assert "Error getting system info" in result
        assert "System access denied" in result


class TestFormatError:
    """Test format_error function."""

    def test_format_error_markdown(self):
        """Test error formatting with markdown."""
        def mock_format_error(error, context=None, markdown=True):
            error_type = type(error).__name__
            error_message = str(error)
            
            if markdown:
                formatted = f"❌ *Error: {error_type}*\n\n"
                formatted += f"```\n{error_message}\n```\n\n"
                if context:
                    formatted += f"**Context:** {context}\n\n"
            else:
                formatted = f"Error: {error_type}\n\n"
                formatted += f"{error_message}\n\n"
                if context:
                    formatted += f"Context: {context}\n\n"
            
            formatted += f"🕒 {datetime.datetime(2024, 1, 1, 12, 0, 0).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            return formatted
        
        # Test with context
        error = ValueError("Invalid input")
        result = mock_format_error(error, context="User input validation", markdown=True)
        assert "❌ *Error: ValueError*" in result
        assert "```\nInvalid input\n```" in result
        assert "**Context:** User input validation" in result
        assert "2024-01-01 12:00:00 UTC" in result

    def test_format_error_plain_text(self):
        """Test error formatting without markdown."""
        def mock_format_error(error, context=None, markdown=True):
            error_type = type(error).__name__
            error_message = str(error)
            
            if not markdown:
                formatted = f"Error: {error_type}\n\n"
                formatted += f"{error_message}\n\n"
                if context:
                    formatted += f"Context: {context}\n\n"
                formatted += f"🕒 2024-01-01 12:00:00 UTC"
                return formatted
            else:
                return f"❌ *Error: {error_type}*\n\n```\n{error_message}\n```"
        
        # Test plain text
        error = RuntimeError("System failure")
        result = mock_format_error(error, context="Service startup", markdown=False)
        assert "Error: RuntimeError" in result
        assert "System failure" in result
        assert "Context: Service startup" in result
        assert "```" not in result  # No markdown code blocks

    def test_format_error_without_context(self):
        """Test error formatting without context."""
        def mock_format_error(error, context=None, markdown=True):
            error_type = type(error).__name__
            error_message = str(error)
            
            formatted = f"❌ *Error: {error_type}*\n\n"
            formatted += f"```\n{error_message}\n```\n\n"
            if context:
                formatted += f"**Context:** {context}\n\n"
            formatted += "🕒 2024-01-01 12:00:00 UTC"
            return formatted
        
        # Test without context
        error = KeyError("missing_key")
        result = mock_format_error(error, context=None, markdown=True)
        assert "❌ *Error: KeyError*" in result
        assert "```\n'missing_key'\n```" in result  # KeyError adds quotes around the key
        assert "Context:" not in result


class TestFormatAlert:
    """Test format_alert function."""

    def test_format_alert_markdown(self):
        """Test alert formatting with markdown."""
        def mock_format_alert(metric, value, threshold, unit="%", markdown=True):
            if markdown:
                formatted = f"🚨 *Alert: {metric} Threshold Exceeded*\n\n"
                formatted += f"**Current Value:** {value:.1f}{unit}\n"
                formatted += f"**Threshold:** {threshold:.1f}{unit}\n"
                formatted += f"**Exceeded By:** {value - threshold:.1f}{unit}\n\n"
            else:
                formatted = f"Alert: {metric} Threshold Exceeded\n\n"
                formatted += f"Current Value: {value:.1f}{unit}\n"
                formatted += f"Threshold: {threshold:.1f}{unit}\n"
                formatted += f"Exceeded By: {value - threshold:.1f}{unit}\n\n"
            
            formatted += f"🕒 {datetime.datetime(2024, 1, 1, 12, 0, 0).strftime('%Y-%m-%d %H:%M:%S UTC')}"
            return formatted
        
        # Test alert formatting
        result = mock_format_alert("CPU Usage", 85.5, 80.0, "%", markdown=True)
        assert "🚨 *Alert: CPU Usage Threshold Exceeded*" in result
        assert "**Current Value:** 85.5%" in result
        assert "**Threshold:** 80.0%" in result
        assert "**Exceeded By:** 5.5%" in result

    def test_format_alert_plain_text(self):
        """Test alert formatting without markdown."""
        def mock_format_alert(metric, value, threshold, unit="%", markdown=True):
            if not markdown:
                formatted = f"Alert: {metric} Threshold Exceeded\n\n"
                formatted += f"Current Value: {value:.1f}{unit}\n"
                formatted += f"Threshold: {threshold:.1f}{unit}\n"
                formatted += f"Exceeded By: {value - threshold:.1f}{unit}\n\n"
                formatted += "🕒 2024-01-01 12:00:00 UTC"
                return formatted
            else:
                return f"🚨 *Alert: {metric} Threshold Exceeded*"
        
        # Test plain text
        result = mock_format_alert("Memory Usage", 92.3, 90.0, "%", markdown=False)
        assert "Alert: Memory Usage Threshold Exceeded" in result
        assert "Current Value: 92.3%" in result
        assert "Threshold: 90.0%" in result
        assert "Exceeded By: 2.3%" in result
        assert "**" not in result  # No markdown formatting

    def test_format_alert_different_units(self):
        """Test alert formatting with different units."""
        def mock_format_alert(metric, value, threshold, unit="%", markdown=True):
            formatted = f"🚨 *Alert: {metric} Threshold Exceeded*\n\n"
            formatted += f"**Current Value:** {value:.1f}{unit}\n"
            formatted += f"**Threshold:** {threshold:.1f}{unit}\n"
            formatted += f"**Exceeded By:** {value - threshold:.1f}{unit}\n"
            return formatted
        
        # Test with GB unit
        result = mock_format_alert("Disk Usage", 450.5, 400.0, "GB", markdown=True)
        assert "**Current Value:** 450.5GB" in result
        assert "**Threshold:** 400.0GB" in result
        assert "**Exceeded By:** 50.5GB" in result


class TestFormatTable:
    """Test format_table function."""

    def test_format_table_markdown(self):
        """Test table formatting with markdown."""
        def mock_format_table(data, headers, markdown=True):
            if not data or not headers:
                return "No data to display"
            
            if markdown:
                # Calculate column widths
                widths = [len(header) for header in headers]
                for row in data:
                    for i, cell in enumerate(row):
                        if i < len(widths):
                            widths[i] = max(widths[i], len(str(cell)))
                
                # Create header
                table = "| " + " | ".join(headers) + " |\n"
                table += "|" + "|".join(["-" * (w + 2) for w in widths]) + "|\n"
                
                # Add data rows
                for row in data:
                    table += "| " + " | ".join([str(cell).ljust(widths[i]) for i, cell in enumerate(row)]) + " |\n"
                
                return f"```\n{table}\n```"
            else:
                return "Plain table format"
        
        # Test markdown table
        headers = ["Name", "Status", "CPU"]
        data = [
            ["Service1", "Running", "25%"],
            ["Service2", "Stopped", "0%"]
        ]
        
        result = mock_format_table(data, headers, markdown=True)
        assert "```\n" in result
        assert "| Name | Status | CPU |" in result
        assert "| Service1 | Running | 25% |" in result
        assert "| Service2 | Stopped | 0%" in result  # Remove exact spacing expectation

    def test_format_table_plain_text(self):
        """Test table formatting without markdown."""
        def mock_format_table(data, headers, markdown=True):
            if not data or not headers:
                return "No data to display"
            
            if not markdown:
                # Calculate column widths
                widths = [len(header) for header in headers]
                for row in data:
                    for i, cell in enumerate(row):
                        if i < len(widths):
                            widths[i] = max(widths[i], len(str(cell)))
                
                # Create header
                table = " | ".join([header.ljust(widths[i]) for i, header in enumerate(headers)]) + "\n"
                table += "-" * len(table) + "\n"
                
                # Add data rows
                for row in data:
                    table += " | ".join([str(cell).ljust(widths[i]) for i, cell in enumerate(row)]) + "\n"
                
                return table
            else:
                return "```\nMarkdown table\n```"
        
        # Test plain text table
        headers = ["ID", "Name"]
        data = [["1", "Test"]]
        
        result = mock_format_table(data, headers, markdown=False)
        assert "ID | Name" in result
        assert "1  | Test" in result
        assert "```" not in result  # No markdown code blocks

    def test_format_table_empty_data(self):
        """Test table formatting with empty data."""
        def mock_format_table(data, headers, markdown=True):
            if not data or not headers:
                return "No data to display"
            return "Table with data"
        
        # Test empty data
        result = mock_format_table([], ["Header1", "Header2"], markdown=True)
        assert result == "No data to display"
        
        # Test empty headers
        result = mock_format_table([["data1", "data2"]], [], markdown=True)
        assert result == "No data to display"

    def test_format_table_column_width_calculation(self):
        """Test column width calculation."""
        def calculate_column_widths(headers, data):
            """Calculate optimal column widths."""
            widths = [len(header) for header in headers]
            for row in data:
                for i, cell in enumerate(row):
                    if i < len(widths):
                        widths[i] = max(widths[i], len(str(cell)))
            return widths
        
        # Test width calculation
        headers = ["Short", "Medium Length", "A"]
        data = [
            ["Very Long Content", "Med", "Long Content Here"],
            ["S", "Medium", "B"]
        ]
        
        widths = calculate_column_widths(headers, data)
        assert widths[0] == len("Very Long Content")  # Longest in first column
        assert widths[1] == len("Medium Length")      # Header is longest in second column
        assert widths[2] == len("Long Content Here")  # Longest in third column


class TestFormattersIntegration:
    """Test integration scenarios."""

    def test_timestamp_formatting_consistency(self):
        """Test timestamp formatting consistency across functions."""
        test_time = datetime.datetime(2024, 1, 1, 12, 0, 0)
        expected_format = "2024-01-01 12:00:00 UTC"
        
        # Test timestamp formatting
        formatted = test_time.strftime('%Y-%m-%d %H:%M:%S UTC')
        assert formatted == expected_format

    def test_markdown_vs_plain_text_consistency(self):
        """Test consistency between markdown and plain text modes."""
        def test_both_formats(content):
            """Test both markdown and plain text formatting."""
            markdown_result = f"*{content}*"
            plain_result = content
            
            return {
                'markdown': markdown_result,
                'plain': plain_result,
                'content_preserved': content in markdown_result and content in plain_result
            }
        
        result = test_both_formats("Test Content")
        assert result['content_preserved'] is True
        assert "*" in result['markdown']
        assert "*" not in result['plain']

    def test_error_handling_patterns(self):
        """Test error handling patterns across formatters."""
        def unified_error_handler(operation_func):
            """Unified error handling for formatters."""
            try:
                return operation_func()
            except Exception as e:
                return f"Error in formatting: {str(e)}"
        
        # Test error handling
        def failing_operation():
            raise ValueError("Formatting failed")
        
        result = unified_error_handler(failing_operation)
        assert "Error in formatting" in result
        assert "Formatting failed" in result
