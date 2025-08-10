"""Example: Using the CLI to send notifications."""

import subprocess
import os


def run_cli_command(command):
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Command executed: {command}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e.stderr.strip()}")
        return False


def example_cli_text_notifications():
    """Example: Sending text notifications via CLI."""
    
    print("=== Text Notifications ===")
    
    # Simple message to default chats
    run_cli_command('python -m bot.cli send "Hello from CLI! 👋"')
    
    # Message to specific chat
    run_cli_command('python -m bot.cli send "Private message" --chat-id YOUR_CHAT_ID')
    
    # Message to multiple chats
    run_cli_command('python -m bot.cli send "Broadcast message" --chat-ids "CHAT_ID_1,CHAT_ID_2"')
    
    # Message with HTML formatting
    run_cli_command('python -m bot.cli send "<b>Bold</b> and <i>italic</i> text" --parse-mode HTML')
    
    # Markdown message
    run_cli_command('python -m bot.cli send "*Bold* and _italic_ text with `code`" --parse-mode Markdown')


def example_cli_file_notifications():
    """Example: Sending files via CLI."""
    
    print("\n=== File Notifications ===")
    
    # Send an image
    run_cli_command('python -m bot.cli send "Check out this image!" --file ./path/to/image.jpg --caption "My awesome screenshot"')
    
    # Send a document
    run_cli_command('python -m bot.cli send "Here\'s the report" --file ./path/to/report.pdf --caption "Monthly Report"')
    
    # Send a log file
    run_cli_command('python -m bot.cli send "Latest logs" --file ./app.log --caption "Application logs from today"')


def example_cli_system_monitoring():
    """Example: System monitoring via CLI."""
    
    print("\n=== System Monitoring ===")
    
    # Get current system metrics
    run_cli_command('python -m bot.cli metrics')
    
    # Send system report to default subscribers
    run_cli_command('python -m bot.cli system')
    
    # Send system report to specific chat
    run_cli_command('python -m bot.cli system --chat-id YOUR_CHAT_ID')


def example_cli_scheduling():
    """Example: Scheduling notifications via CLI."""
    
    print("\n=== Scheduling Notifications ===")
    
    # Schedule daily notification at 9 AM
    run_cli_command('python -m bot.cli schedule daily_reminder "Good morning! Start your day strong! 💪" --chat-ids "YOUR_CHAT_ID" --cron "0 9 * * *"')
    
    # Schedule notification every 30 minutes
    run_cli_command('python -m bot.cli schedule health_check "System health check completed ✅" --chat-ids "YOUR_CHAT_ID" --interval 1800')
    
    # Schedule one-time notification
    run_cli_command('python -m bot.cli schedule meeting_reminder "Meeting in 10 minutes! 📅" --chat-ids "YOUR_CHAT_ID" --date "2024-01-10T14:50:00"')
    
    # List scheduled jobs
    run_cli_command('python -m bot.cli jobs')
    
    # Remove a scheduled job
    run_cli_command('python -m bot.cli unschedule daily_reminder')


def example_cli_status_management():
    """Example: Status and management via CLI."""
    
    print("\n=== Status and Management ===")
    
    # Check bot status
    run_cli_command('python -m bot.cli status')
    
    # Run the bot (this would start the bot - comment out for examples)
    # run_cli_command('python -m bot.cli run')
    
    # Start API server (this would start the server - comment out for examples)  
    # run_cli_command('python -m bot.cli api --host 0.0.0.0 --port 8080')


def create_example_scripts():
    """Create example shell scripts for common use cases."""
    
    scripts = {
        "notify_deployment.sh": """#!/bin/bash
# Deployment notification script

APP_NAME="$1"
VERSION="$2"
STATUS="$3"

if [ "$STATUS" = "success" ]; then
    MESSAGE="🚀 *Deployment Successful*

**Application:** $APP_NAME
**Version:** $VERSION
**Status:** ✅ Success
**Time:** $(date)"
else
    MESSAGE="❌ *Deployment Failed*

**Application:** $APP_NAME  
**Version:** $VERSION
**Status:** ❌ Failed
**Time:** $(date)

Please check deployment logs."
fi

python -m bot.cli send "$MESSAGE" --parse-mode Markdown
""",

        "notify_backup.sh": """#!/bin/bash
# Backup notification script

BACKUP_TYPE="$1"
SIZE="$2"
DURATION="$3"

MESSAGE="💾 *Backup Completed*

**Type:** $BACKUP_TYPE
**Size:** $SIZE
**Duration:** $DURATION
**Status:** ✅ Success
**Time:** $(date)"

python -m bot.cli send "$MESSAGE" --parse-mode Markdown
""",

        "notify_error.sh": """#!/bin/bash
# Error notification script

SERVICE="$1"
ERROR_MSG="$2"
SEVERITY="$3"

if [ "$SEVERITY" = "critical" ]; then
    EMOJI="🚨"
else
    EMOJI="⚠️"
fi

MESSAGE="$EMOJI *Error Alert*

**Service:** $SERVICE
**Severity:** $SEVERITY
**Error:** $ERROR_MSG
**Time:** $(date)

Please investigate immediately."

python -m bot.cli send "$MESSAGE" --parse-mode Markdown
""",

        "daily_report.sh": """#!/bin/bash
# Daily report script

UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')
DISK_USAGE=$(df -h / | awk 'NR==2{print $5}')
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')

MESSAGE="📊 *Daily System Report*

**Date:** $(date '+%Y-%m-%d')
**Uptime:** $UPTIME
**Disk Usage:** $DISK_USAGE
**Memory Usage:** $MEMORY_USAGE

System is running smoothly! ✅"

python -m bot.cli send "$MESSAGE" --parse-mode Markdown
"""
    }
    
    print("\n=== Creating Example Scripts ===")
    
    for filename, content in scripts.items():
        try:
            with open(f"examples/{filename}", "w") as f:
                f.write(content)
            os.chmod(f"examples/{filename}", 0o755)
            print(f"✅ Created {filename}")
        except Exception as e:
            print(f"❌ Failed to create {filename}: {str(e)}")


if __name__ == "__main__":
    print("Telegram Bot CLI Examples")
    print("=" * 40)
    print("Note: Replace 'YOUR_CHAT_ID' with actual chat IDs")
    print("Note: Ensure the bot is properly configured with .env file")
    print()
    
    # Run examples
    example_cli_text_notifications()
    example_cli_file_notifications()
    example_cli_system_monitoring() 
    example_cli_scheduling()
    example_cli_status_management()
    
    # Create example scripts
    create_example_scripts()
    
    print("\nAll CLI examples completed!")
    print("\nUseful CLI commands to remember:")
    print("  python -m bot.cli send 'Your message'")
    print("  python -m bot.cli system")
    print("  python -m bot.cli metrics") 
    print("  python -m bot.cli status")
    print("  python -m bot.cli schedule job_id 'message' --chat-ids 'ID' --cron '0 9 * * *'")
    print("  python -m bot.cli run")
    print("  python -m bot.cli api")
