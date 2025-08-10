"""Message formatting utilities."""

import datetime
from typing import Dict, Any, Optional
import psutil


def format_message(
    title: str,
    message: str,
    timestamp: Optional[datetime.datetime] = None,
    level: str = "INFO",
    markdown: bool = True
) -> str:
    """Format a message with title and metadata.
    
    Args:
        title: Message title
        message: Message content
        timestamp: Message timestamp
        level: Log level (INFO, WARNING, ERROR)
        markdown: Whether to use Markdown formatting
        
    Returns:
        Formatted message string
    """
    if timestamp is None:
        timestamp = datetime.datetime.now()
    
    if markdown:
        # Escape special characters for Markdown
        title = title.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
        level_emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅',
            'DEBUG': '🔍'
        }.get(level.upper(), 'ℹ️')
        
        formatted = f"{level_emoji} *{title}*\n\n"
        formatted += f"{message}\n\n"
        formatted += f"🕒 {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
    else:
        formatted = f"[{level}] {title}\n\n"
        formatted += f"{message}\n\n"
        formatted += f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    return formatted


def format_system_info(markdown: bool = True) -> str:
    """Format system information.
    
    Args:
        markdown: Whether to use Markdown formatting
        
    Returns:
        Formatted system info string
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if markdown:
            info = "🖥️ *System Status*\n\n"
            info += f"**CPU Usage:** {cpu_percent:.1f}%\n"
            info += f"**Memory Usage:** {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)\n"
            info += f"**Disk Usage:** {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)\n"
            info += f"**Load Average:** {', '.join(map(str, psutil.getloadavg()))}\n"
        else:
            info = "System Status\n\n"
            info += f"CPU Usage: {cpu_percent:.1f}%\n"
            info += f"Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)\n"
            info += f"Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)\n"
            info += f"Load Average: {', '.join(map(str, psutil.getloadavg()))}\n"
        
        return info
        
    except Exception as e:
        return f"Error getting system info: {str(e)}"


def format_error(
    error: Exception,
    context: Optional[str] = None,
    markdown: bool = True
) -> str:
    """Format an error message.
    
    Args:
        error: Exception object
        context: Additional context
        markdown: Whether to use Markdown formatting
        
    Returns:
        Formatted error string
    """
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
    
    formatted += f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    return formatted


def format_alert(
    metric: str,
    value: float,
    threshold: float,
    unit: str = "%",
    markdown: bool = True
) -> str:
    """Format an alert message.
    
    Args:
        metric: Metric name
        value: Current value
        threshold: Threshold value
        unit: Unit of measurement
        markdown: Whether to use Markdown formatting
        
    Returns:
        Formatted alert string
    """
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
    
    formatted += f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    
    return formatted


def format_table(
    data: list,
    headers: list,
    markdown: bool = True
) -> str:
    """Format data as a table.
    
    Args:
        data: List of lists/tuples representing rows
        headers: List of column headers
        markdown: Whether to use Markdown formatting
        
    Returns:
        Formatted table string
    """
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
        # Plain text table
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
