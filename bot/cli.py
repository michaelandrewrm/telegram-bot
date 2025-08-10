"""Command-line interface for the Telegram bot."""

import asyncio
import click
import json
from pathlib import Path
from typing import Optional
from .services.notification import send_notification
from .services.monitoring import monitoring_service
from .services.scheduler import scheduler_service
from .config import config
import structlog

logger = structlog.get_logger(__name__)


@click.group()
@click.option('--config-file', '-c', type=click.Path(exists=True), help='Path to config file')
@click.option('--env-file', '-e', type=click.Path(exists=True), help='Path to .env file')
@click.option('--log-level', '-l', default='INFO', help='Log level')
@click.pass_context
def cli(ctx, config_file, env_file, log_level):
    """Telegram Notification Bot CLI."""
    ctx.ensure_object(dict)
    
    # Update config if custom files provided
    if config_file:
        config.config_path = Path(config_file)
    if env_file:
        config.env_path = Path(env_file)
    if log_level:
        config.log_level = log_level


@cli.command()
@click.argument('message')
@click.option('--chat-id', '-i', help='Specific chat ID to send to')
@click.option('--chat-ids', '-I', help='Comma-separated list of chat IDs')
@click.option('--parse-mode', '-p', default='Markdown', help='Parse mode (Markdown, HTML)')
@click.option('--file', '-f', type=click.Path(exists=True), help='Send file instead of text')
@click.option('--caption', help='Caption for file')
def send(message, chat_id, chat_ids, parse_mode, file, caption):
    """Send a notification message."""
    async def _send():
        try:
            if file:
                # Send file
                from .services.notification import notification_service
                
                target_chat_id = chat_id or config.default_chat_ids[0] if config.default_chat_ids else None
                
                if not target_chat_id:
                    click.echo("Error: No chat ID specified and no defaults configured")
                    return
                
                file_path = Path(file)
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    success = await notification_service.send_photo(
                        chat_id=target_chat_id,
                        photo=file_path,
                        caption=caption or message,
                        parse_mode=parse_mode
                    )
                else:
                    success = await notification_service.send_document(
                        chat_id=target_chat_id,
                        document=file_path,
                        caption=caption or message,
                        parse_mode=parse_mode
                    )
                
                if success:
                    click.echo(f"File sent successfully to {target_chat_id}")
                else:
                    click.echo("Failed to send file")
            else:
                # Send text message
                if chat_ids:
                    # Send to multiple chats
                    chat_id_list = [cid.strip() for cid in chat_ids.split(',')]
                    from .services.notification import notification_service
                    results = await notification_service.send_to_multiple(
                        message, chat_id_list, parse_mode=parse_mode
                    )
                    successful = sum(results)
                    click.echo(f"Message sent to {successful}/{len(results)} chats")
                elif chat_id:
                    # Send to specific chat
                    success = await send_notification(
                        message, chat_id, parse_mode=parse_mode
                    )
                    if success:
                        click.echo(f"Message sent successfully to {chat_id}")
                    else:
                        click.echo("Failed to send message")
                else:
                    # Send to default chats
                    success = await send_notification(message, parse_mode=parse_mode)
                    if success:
                        click.echo("Message sent successfully to default chats")
                    else:
                        click.echo("Failed to send message")
        
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_send())


@cli.command()
@click.option('--chat-id', '-i', help='Specific chat ID to send to')
def system(chat_id):
    """Send system information."""
    async def _system():
        try:
            target_chat_id = int(chat_id) if chat_id else None
            await monitoring_service.send_system_report(target_chat_id)
            
            if chat_id:
                click.echo(f"System report sent to {chat_id}")
            else:
                click.echo("System report sent to subscribers")
                
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_system())


@cli.command()
def metrics():
    """Show current system metrics."""
    async def _metrics():
        try:
            metrics = await monitoring_service.get_current_metrics()
            
            if metrics:
                click.echo("\nCurrent System Metrics:")
                click.echo("-" * 30)
                for key, value in metrics.items():
                    if isinstance(value, float):
                        click.echo(f"{key}: {value:.2f}")
                    else:
                        click.echo(f"{key}: {value}")
            else:
                click.echo("Unable to retrieve metrics")
                
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_metrics())


@cli.command()
@click.argument('job_id')
@click.argument('message')
@click.option('--chat-ids', '-I', required=True, help='Comma-separated list of chat IDs')
@click.option('--cron', help='Cron expression (e.g., "0 9 * * *" for daily at 9 AM)')
@click.option('--interval', type=int, help='Interval in seconds')
@click.option('--date', help='Specific date/time (ISO format)')
def schedule(job_id, message, chat_ids, cron, interval, date):
    """Schedule a notification."""
    async def _schedule():
        try:
            chat_id_list = [cid.strip() for cid in chat_ids.split(',')]
            
            # Determine trigger type and kwargs
            if cron:
                # Parse cron expression
                parts = cron.split()
                if len(parts) != 5:
                    click.echo("Error: Cron expression must have 5 parts (minute hour day month weekday)")
                    return
                
                trigger_kwargs = {
                    'minute': parts[0],
                    'hour': parts[1], 
                    'day': parts[2],
                    'month': parts[3],
                    'day_of_week': parts[4]
                }
                trigger_type = 'cron'
                
            elif interval:
                trigger_kwargs = {'seconds': interval}
                trigger_type = 'interval'
                
            elif date:
                from datetime import datetime
                run_date = datetime.fromisoformat(date)
                trigger_kwargs = {'run_date': run_date}
                trigger_type = 'date'
                
            else:
                click.echo("Error: Must specify --cron, --interval, or --date")
                return
            
            # Schedule the notification
            success = await scheduler_service.schedule_notification(
                job_id=job_id,
                message=message,
                chat_ids=chat_id_list,
                trigger_type=trigger_type,
                **trigger_kwargs
            )
            
            if success:
                click.echo(f"Notification scheduled successfully with ID: {job_id}")
            else:
                click.echo("Failed to schedule notification")
                
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_schedule())


@cli.command()
@click.argument('job_id')
def unschedule(job_id):
    """Remove a scheduled notification."""
    async def _unschedule():
        try:
            success = await scheduler_service.unschedule_job(job_id)
            
            if success:
                click.echo(f"Job {job_id} unscheduled successfully")
            else:
                click.echo(f"Job {job_id} not found")
                
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_unschedule())


@cli.command()
def jobs():
    """List scheduled jobs."""
    async def _jobs():
        try:
            jobs = await scheduler_service.get_scheduled_jobs()
            
            if jobs:
                click.echo("\nScheduled Jobs:")
                click.echo("-" * 50)
                for job in jobs:
                    click.echo(f"ID: {job['id']}")
                    click.echo(f"Next Run: {job['next_run_time']}")
                    click.echo(f"Trigger: {job['trigger']}")
                    if 'message' in job:
                        preview = job['message'][:50] + "..." if len(job['message']) > 50 else job['message']
                        click.echo(f"Message: {preview}")
                    click.echo("-" * 30)
            else:
                click.echo("No scheduled jobs found")
                
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_jobs())


@cli.command()
def status():
    """Check bot status."""
    async def _status():
        try:
            from .services.notification import notification_service
            
            # Test connection
            is_healthy = await notification_service.test_connection()
            
            click.echo(f"Bot Status: {'✅ Online' if is_healthy else '❌ Offline'}")
            click.echo(f"Config File: {config.config_path}")
            click.echo(f"Env File: {config.env_path}")
            click.echo(f"Default Chat IDs: {config.default_chat_ids}")
            click.echo(f"API Enabled: {config.api_enabled}")
            click.echo(f"Monitoring Enabled: {config.enable_monitoring}")
            click.echo(f"Scheduling Enabled: {config.enable_scheduling}")
            
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_status())


@cli.command()
def run():
    """Run the bot."""
    async def _run():
        try:
            from .main import main
            await main()
        except KeyboardInterrupt:
            click.echo("\nBot stopped by user")
        except Exception as e:
            click.echo(f"Error: {str(e)}")
    
    asyncio.run(_run())


@cli.command()
@click.option('--host', default='0.0.0.0', help='API server host')
@click.option('--port', default=8080, type=int, help='API server port')
def api(host, port):
    """Run the API server."""
    try:
        import uvicorn
        from .api import app
        
        click.echo(f"Starting API server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}")


if __name__ == '__main__':
    cli()
