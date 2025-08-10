"""Example: Using webhooks to send notifications."""

import requests
import json
from datetime import datetime


def send_webhook_notification(
    message: str,
    level: str = "INFO",
    source: str = "External System",
    webhook_url: str = "http://localhost:8080/webhook/notify",
    webhook_token: str = "your_webhook_token_here"
):
    """Send a notification via webhook.
    
    Args:
        message: Message to send
        level: Message level (INFO, WARNING, ERROR)
        source: Source of the message
        webhook_url: Webhook endpoint URL
        webhook_token: Webhook authentication token
    """
    
    payload = {
        "message": message,
        "level": level,
        "source": source,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "version": "1.0",
            "environment": "production"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Token": webhook_token
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook notification sent successfully")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook request failed: {str(e)}")
        return False


def example_ci_cd_webhook():
    """Example: CI/CD pipeline notifications."""
    
    # Build started
    send_webhook_notification(
        message="Build #123 started for branch 'main'",
        level="INFO",
        source="CI/CD Pipeline"
    )
    
    # Build completed successfully
    send_webhook_notification(
        message="Build #123 completed successfully! 🎉\n\nDuration: 3m 45s\nTests passed: 127/127",
        level="INFO",
        source="CI/CD Pipeline"
    )
    
    # Build failed
    send_webhook_notification(
        message="Build #124 failed ❌\n\nError: Unit tests failed\nFailed tests: 3/127\nBranch: feature/new-api",
        level="ERROR",
        source="CI/CD Pipeline"
    )
    
    # Deployment completed
    send_webhook_notification(
        message="Deployment to production completed successfully! 🚀\n\nVersion: v2.1.0\nDeployment time: 2m 15s",
        level="INFO", 
        source="Deployment System"
    )


def example_monitoring_webhook():
    """Example: Monitoring system notifications."""
    
    # Service down alert
    send_webhook_notification(
        message="🚨 Service 'api-server' is DOWN!\n\nLast check: 2024-01-10 15:30:00\nResponse time: Timeout\nStatus code: N/A",
        level="ERROR",
        source="Monitoring System"
    )
    
    # Service recovered
    send_webhook_notification(
        message="✅ Service 'api-server' is back UP!\n\nDowntime: 5m 32s\nCurrent response time: 150ms",
        level="INFO",
        source="Monitoring System"
    )
    
    # High resource usage
    send_webhook_notification(
        message="⚠️ High memory usage detected\n\nCurrent usage: 87%\nThreshold: 85%\nServer: prod-web-01",
        level="WARNING",
        source="Resource Monitor"
    )


def example_application_webhook():
    """Example: Application event notifications."""
    
    # User registration
    send_webhook_notification(
        message="📝 New user registered\n\nUser ID: 12345\nEmail: user@example.com\nRegistration source: Website",
        level="INFO",
        source="User Management"
    )
    
    # Payment processed
    send_webhook_notification(
        message="💳 Payment processed successfully\n\nAmount: $99.99\nCustomer: John Doe\nTransaction ID: TXN123456",
        level="INFO",
        source="Payment System"
    )
    
    # Critical error
    send_webhook_notification(
        message="🔥 Critical error in payment processing!\n\nError: Database connection timeout\nAffected transactions: 15\nAction required: Immediate",
        level="ERROR",
        source="Payment System"
    )


def example_scheduled_webhook():
    """Example: Scheduled task notifications."""
    
    # Daily backup
    send_webhook_notification(
        message="💾 Daily backup completed\n\nBackup size: 2.1GB\nDuration: 45 minutes\nStatus: Success",
        level="INFO",
        source="Backup System"
    )
    
    # Weekly report
    send_webhook_notification(
        message="📊 Weekly performance report\n\n• Total users: 1,247 (+23)\n• Revenue: $12,450 (+8%)\n• Uptime: 99.8%\n• Support tickets: 45 (-12%)",
        level="INFO",
        source="Analytics System"
    )


if __name__ == "__main__":
    print("Running webhook notification examples...")
    print("Note: Make sure the bot API server is running on localhost:8080")
    print("Update the webhook_token in the send_webhook_notification function")
    print()
    
    # Run examples
    print("1. CI/CD Pipeline notifications:")
    example_ci_cd_webhook()
    print()
    
    print("2. Monitoring system notifications:")
    example_monitoring_webhook()
    print()
    
    print("3. Application event notifications:")
    example_application_webhook()
    print()
    
    print("4. Scheduled task notifications:")
    example_scheduled_webhook()
    print()
    
    print("All webhook examples completed!")
