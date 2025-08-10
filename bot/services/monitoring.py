"""System monitoring service for sending alerts."""

import asyncio
import psutil
from typing import Dict, List, Optional
from ..config import config
from ..services.notification import notification_service
from ..services.subscription import subscription_service
from ..utils.formatters import format_alert, format_system_info
from ..constants import SUBSCRIPTION_TYPES
import structlog

logger = structlog.get_logger(__name__)


class MonitoringService:
    """Service for monitoring system metrics and sending alerts."""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = 60  # seconds
        self._last_alerts: Dict[str, float] = {}
        self.alert_cooldown = 300  # 5 minutes
    
    async def start_monitoring(self):
        """Start the monitoring service."""
        if self.is_running:
            logger.warning("Monitoring service already running")
            return
        
        self.is_running = True
        logger.info("Starting monitoring service")
        
        while self.is_running:
            try:
                await self._check_system_metrics()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(self.check_interval)
    
    async def stop_monitoring(self):
        """Stop the monitoring service."""
        logger.info("Stopping monitoring service")
        self.is_running = False
    
    async def _check_system_metrics(self):
        """Check system metrics and send alerts if thresholds are exceeded."""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check CPU
            if cpu_percent > config.cpu_threshold:
                await self._send_alert(
                    'CPU',
                    cpu_percent,
                    config.cpu_threshold,
                    '%'
                )
            
            # Check Memory
            if memory.percent > config.memory_threshold:
                await self._send_alert(
                    'Memory',
                    memory.percent,
                    config.memory_threshold,
                    '%'
                )
            
            # Check Disk
            if disk.percent > config.disk_threshold:
                await self._send_alert(
                    'Disk',
                    disk.percent,
                    config.disk_threshold,
                    '%'
                )
            
            logger.debug("System metrics checked",
                        cpu=cpu_percent,
                        memory=memory.percent,
                        disk=disk.percent)
                        
        except Exception as e:
            logger.error("Error checking system metrics", error=str(e))
    
    async def _send_alert(
        self, 
        metric: str, 
        value: float, 
        threshold: float, 
        unit: str
    ):
        """Send an alert for a metric threshold breach.
        
        Args:
            metric: Metric name
            value: Current value
            threshold: Threshold value
            unit: Unit of measurement
        """
        # Check cooldown to avoid spam
        alert_key = f"{metric}_{threshold}"
        current_time = asyncio.get_event_loop().time()
        
        if (alert_key in self._last_alerts and 
            current_time - self._last_alerts[alert_key] < self.alert_cooldown):
            logger.debug("Alert skipped due to cooldown", metric=metric)
            return
        
        self._last_alerts[alert_key] = current_time
        
        # Format alert message
        message = format_alert(metric, value, threshold, unit, markdown=True)
        
        # Get subscribers to system alerts
        subscribers = await subscription_service.get_subscribers(
            SUBSCRIPTION_TYPES['SYSTEM']
        )
        
        if not subscribers:
            logger.warning("No subscribers for system alerts")
            return
        
        # Send alert to subscribers
        for user_id in subscribers:
            try:
                success = await notification_service.send_notification(
                    message=message,
                    chat_id=user_id,
                    parse_mode='Markdown'
                )
                
                if success:
                    logger.info("Alert sent",
                               metric=metric,
                               user_id=user_id,
                               value=value,
                               threshold=threshold)
                else:
                    logger.warning("Failed to send alert",
                                 metric=metric,
                                 user_id=user_id)
                    
            except Exception as e:
                logger.error("Error sending alert to user",
                           metric=metric,
                           user_id=user_id,
                           error=str(e))
    
    async def get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics.
        
        Returns:
            Dictionary of current metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            load_avg = psutil.getloadavg()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'load_1min': load_avg[0],
                'load_5min': load_avg[1],
                'load_15min': load_avg[2]
            }
            
        except Exception as e:
            logger.error("Error getting current metrics", error=str(e))
            return {}
    
    async def send_system_report(self, chat_id: Optional[int] = None):
        """Send a system status report.
        
        Args:
            chat_id: Specific chat ID to send to. If None, sends to system subscribers.
        """
        try:
            # Get system info
            message = format_system_info(markdown=True)
            
            if chat_id:
                # Send to specific chat
                await notification_service.send_notification(
                    message=message,
                    chat_id=chat_id,
                    parse_mode='Markdown'
                )
            else:
                # Send to system subscribers
                subscribers = await subscription_service.get_subscribers(
                    SUBSCRIPTION_TYPES['SYSTEM']
                )
                
                for user_id in subscribers:
                    await notification_service.send_notification(
                        message=message,
                        chat_id=user_id,
                        parse_mode='Markdown'
                    )
            
            logger.info("System report sent", chat_id=chat_id)
            
        except Exception as e:
            logger.error("Error sending system report", error=str(e))
    
    async def check_process_status(self, process_name: str) -> bool:
        """Check if a process is running.
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if process is running, False otherwise
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    return True
            return False
            
        except Exception as e:
            logger.error("Error checking process status", 
                        process=process_name, 
                        error=str(e))
            return False
    
    async def get_disk_usage(self, path: str = '/') -> Dict[str, float]:
        """Get disk usage for a specific path.
        
        Args:
            path: Path to check disk usage for
            
        Returns:
            Dictionary with disk usage information
        """
        try:
            disk = psutil.disk_usage(path)
            return {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3),
                'percent': (disk.used / disk.total) * 100
            }
            
        except Exception as e:
            logger.error("Error getting disk usage", path=path, error=str(e))
            return {}


# Global monitoring service instance
monitoring_service = MonitoringService()
