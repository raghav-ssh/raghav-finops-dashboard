"""
Notification Service for FinOps Reports
Sends reports and alerts via Email and Slack.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
import requests

from core.logger import setup_logger
from services.anomaly_detector import Anomaly


logger = setup_logger(__name__)


class NotificationService:
    """Handle email and Slack notifications."""
    
    def __init__(self):
        """Initialize notification service."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
    
    def send_email_report(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        attachments: List[Path] = None,
        html: bool = False
    ) -> bool:
        """
        Send email with report attachments.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            html: Whether body is HTML
            
        Returns:
            True if sent successfully
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Add body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if file_path.exists():
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read(), Name=file_path.name)
                            part['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {', '.join(to_emails)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_slack_message(
        self,
        message: str,
        blocks: List[dict] = None,
        webhook_url: str = None
    ) -> bool:
        """
        Send message to Slack.
        
        Args:
            message: Plain text message
            blocks: Slack block kit blocks for rich formatting
            webhook_url: Override default webhook URL
            
        Returns:
            True if sent successfully
        """
        webhook = webhook_url or self.slack_webhook
        
        if not webhook:
            logger.warning("Slack webhook not configured, skipping notification")
            return False
        
        try:
            payload = {"text": message}
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Slack message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False
    
    def send_anomaly_alert(
        self,
        anomalies: List[Anomaly],
        report_date: str
    ) -> bool:
        """Send Slack alert for detected anomalies."""
        if not anomalies:
            logger.info("No anomalies to report")
            return True
        
        critical_count = len([a for a in anomalies if a.severity == 'critical'])
        warning_count = len([a for a in anomalies if a.severity == 'warning'])
        
        # Build Slack blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Cost Anomaly Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Date:*\n{report_date}"},
                    {"type": "mrkdwn", "text": f"*Total Anomalies:*\n{len(anomalies)}"},
                    {"type": "mrkdwn", "text": f"*Critical:*\n{critical_count}"},
                    {"type": "mrkdwn", "text": f"*Warnings:*\n{warning_count}"}
                ]
            },
            {"type": "divider"}
        ]
        
        # Add critical anomalies
        if critical_count > 0:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Critical Issues:*"
                }
            })
            
            for anomaly in [a for a in anomalies if a.severity == 'critical'][:5]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔴 *{anomaly.environment}*: {anomaly.message}\n"
                               f"Current: ₹{anomaly.current_value:,.2f}"
                    }
                })
        
        # Add warnings
        if warning_count > 0:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Warnings:*"
                }
            })
            
            for anomaly in [a for a in anomalies if a.severity == 'warning'][:3]:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"⚠️ *{anomaly.environment}*: {anomaly.message}"
                    }
                })
        
        return self.send_slack_message(
            message=f"Cost Anomaly Alert: {critical_count} critical, {warning_count} warnings",
            blocks=blocks
        )
    
    def send_daily_summary(
        self,
        report_date: str,
        total_cost: float,
        env_summary: dict,
        anomaly_count: int,
        pdf_path: Path = None
    ) -> bool:
        """Send daily cost summary to Slack."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Daily FinOps Report"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Date:*\n{report_date}"},
                    {"type": "mrkdwn", "text": f"*Total Cost:*\n₹{total_cost:,.2f}"},
                    {"type": "mrkdwn", "text": f"*Environments:*\n{len(env_summary)}"},
                    {"type": "mrkdwn", "text": f"*Anomalies:*\n{anomaly_count}"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Environment Breakdown:*"
                }
            }
        ]
        
        # Add environment costs
        for env, cost in list(env_summary.items())[:5]:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• *{env}*: ₹{cost:,.2f}"
                }
            })
        
        if pdf_path and pdf_path.exists():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📄 Full report: `{pdf_path.name}`"
                }
            })
        
        return self.send_slack_message(
            message=f"Daily FinOps Report - {report_date}: ₹{total_cost:,.2f}",
            blocks=blocks
        )
