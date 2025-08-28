"""
Email destination handler.

This handler provides email notification capabilities with support for
HTML formatting, attachments, and SMTP configuration.
"""

import os
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any, Dict, List, Optional

from ....config.settings import BroadieSettings
from ..models import DestinationConfig, NotificationContext
from .base import BaseDestinationHandler


class EmailDestinationHandler(BaseDestinationHandler):
    """Handler for email destinations."""

    def __init__(self, config: DestinationConfig):
        super().__init__(config)
        self.settings = BroadieSettings()

        # SMTP configuration from environment or settings
        self.smtp_host = os.getenv("EMAIL_SMTP_HOST", self.settings.email_smtp_host)
        self.smtp_port = int(
            os.getenv("EMAIL_SMTP_PORT", str(self.settings.email_smtp_port or 587))
        )
        self.smtp_user = os.getenv("EMAIL_SMTP_USER", self.settings.email_smtp_user)
        self.smtp_password = os.getenv(
            "EMAIL_SMTP_PASSWORD", self.settings.email_smtp_password
        )
        self.from_email = os.getenv(
            "EMAIL_FROM_ADDRESS", self.settings.email_from_address or self.smtp_user
        )
        self.from_name = os.getenv(
            "EMAIL_FROM_NAME", self.settings.email_from_name or "Broadie Agent"
        )

        # Validate required configuration
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            raise ValueError(
                "Email handler requires SMTP configuration. Please set EMAIL_SMTP_HOST, "
                "EMAIL_SMTP_USER, and EMAIL_SMTP_PASSWORD environment variables."
            )

    async def send_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Send email message."""
        target_email = self.config.target
        settings = self.config.settings

        # Format the message
        formatted_message = self.format_message(message, context)

        try:
            # Create message
            msg = MIMEMultipart("alternative")

            # Email headers
            msg["Subject"] = formatted_message["subject"]
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = target_email

            # Add Reply-To if specified
            if settings.get("reply_to"):
                msg["Reply-To"] = settings["reply_to"]

            # Add custom headers
            if settings.get("headers"):
                for header_name, header_value in settings["headers"].items():
                    msg[header_name] = header_value

            # Plain text part
            text_part = MIMEText(formatted_message["text_content"], "plain", "utf-8")
            msg.attach(text_part)

            # HTML part if enabled
            if formatted_message.get("html_content"):
                html_part = MIMEText(formatted_message["html_content"], "html", "utf-8")
                msg.attach(html_part)

            # Add attachments if specified
            if settings.get("attachments"):
                for attachment_path in settings["attachments"]:
                    self._add_attachment(msg, attachment_path)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # Enable TLS if specified (default: True)
                if settings.get("use_tls", True):
                    context = ssl.create_default_context()
                    server.starttls(context=context)

                # Login
                server.login(self.smtp_user, self.smtp_password)

                # Send message
                text = msg.as_string()
                server.sendmail(self.from_email, [target_email], text)

            return {
                "status": "success",
                "recipient": target_email,
                "subject": formatted_message["subject"],
                "smtp_host": self.smtp_host,
                "message_size": len(text),
            }

        except Exception as e:
            raise Exception(f"Failed to send email to {target_email}: {str(e)}")

    async def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.config.settings.get("use_tls", True):
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                return True
        except Exception:
            return False

    def format_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Format message for email."""
        settings = self.config.settings

        # Generate subject
        subject = self._generate_subject(message, context, settings)

        # Generate text content
        text_content = self._generate_text_content(message, context, settings)

        # Generate HTML content if enabled
        html_content = None
        if settings.get("use_html", True):
            html_content = self._generate_html_content(message, context, settings)

        return {
            "subject": subject,
            "text_content": text_content,
            "html_content": html_content,
        }

    def _generate_subject(
        self, message: str, context: NotificationContext, settings: Dict[str, Any]
    ) -> str:
        """Generate email subject line."""
        # Use custom subject if provided
        if settings.get("subject"):
            return settings["subject"]

        # Use subject prefix if provided
        prefix = settings.get("subject_prefix", "")

        # Generate subject based on context
        subject_parts = []

        if prefix:
            subject_parts.append(prefix)

        if context.severity:
            subject_parts.append(f"[{context.severity.upper()}]")

        if context.agent_name:
            subject_parts.append(f"From {context.agent_name}")

        # Use first line of message as subject if no custom subject
        first_line = message.split("\n")[0]
        if len(first_line) > 50:
            first_line = first_line[:47] + "..."

        subject_parts.append(first_line)

        return " ".join(subject_parts)

    def _generate_text_content(
        self, message: str, context: NotificationContext, settings: Dict[str, Any]
    ) -> str:
        """Generate plain text email content."""
        content_parts = [message]

        # Add context information
        if settings.get("include_context", True):
            content_parts.append("\n" + "=" * 50)

            if context.agent_name:
                content_parts.append(f"Agent: {context.agent_name}")

            if context.severity:
                content_parts.append(f"Severity: {context.severity}")

            if context.tags:
                content_parts.append(f"Tags: {', '.join(context.tags)}")

            if context.timestamp:
                content_parts.append(f"Time: {context.timestamp}")

            # Add metadata
            if context.metadata:
                content_parts.append("\nAdditional Information:")
                for key, value in context.metadata.items():
                    content_parts.append(f"  {key}: {value}")

        # Add footer
        footer = settings.get("footer", "This message was sent by Broadie Agent System")
        content_parts.append(f"\n\n--\n{footer}")

        return "\n".join(content_parts)

    def _generate_html_content(
        self, message: str, context: NotificationContext, settings: Dict[str, Any]
    ) -> str:
        """Generate HTML email content."""
        # Convert message to HTML (basic markdown-like formatting)
        html_message = message.replace("\n\n", "</p><p>").replace("\n", "<br>")
        html_message = f"<p>{html_message}</p>"

        # Severity styling
        severity_colors = {
            "low": "#2196F3",  # Blue
            "medium": "#FF9800",  # Orange
            "high": "#FF5722",  # Deep Orange
            "critical": "#F44336",  # Red
        }

        severity_color = (
            severity_colors.get(context.severity, "#666666")
            if context.severity
            else "#666666"
        )

        # Build HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Broadie Agent Notification</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <!-- Header -->
            <div style="border-left: 4px solid {severity_color}; padding-left: 20px; margin-bottom: 30px;">
                <h2 style="color: {severity_color}; margin: 0;">
                    {context.severity.title() if context.severity else 'Agent'} Notification
                </h2>
                {f'<p style="margin: 5px 0; color: #666;">From: <strong>{context.agent_name}</strong></p>' if context.agent_name else ''}
            </div>
            
            <!-- Message Content -->
            <div style="background: #f9f9f9; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                {html_message}
            </div>
            
            <!-- Context Information -->
            {self._generate_context_html(context) if settings.get('include_context', True) else ''}
            
            <!-- Footer -->
            <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 30px; color: #666; font-size: 12px;">
                {settings.get('footer', 'This message was sent by Broadie Agent System')}
            </div>
            
        </body>
        </html>
        """

        return html_template.strip()

    def _generate_context_html(self, context: NotificationContext) -> str:
        """Generate HTML for context information."""
        context_items = []

        if context.tags:
            tags_html = " ".join(
                [
                    f'<span style="background: #e1f5fe; color: #01579b; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{tag}</span>'
                    for tag in context.tags
                ]
            )
            context_items.append(f"<p><strong>Tags:</strong> {tags_html}</p>")

        if context.timestamp:
            context_items.append(f"<p><strong>Time:</strong> {context.timestamp}</p>")

        if context.metadata:
            metadata_html = '<ul style="margin: 5px 0;">'
            for key, value in context.metadata.items():
                metadata_html += f"<li><strong>{key}:</strong> {value}</li>"
            metadata_html += "</ul>"
            context_items.append(
                f"<p><strong>Additional Information:</strong>{metadata_html}</p>"
            )

        if not context_items:
            return ""

        return f"""
        <div style="background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px;">
            <h4 style="margin: 0 0 10px 0; color: #555;">Context Information</h4>
            {''.join(context_items)}
        </div>
        """

    def _add_attachment(self, msg: MIMEMultipart, attachment_path: str):
        """Add file attachment to email."""
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)

            filename = os.path.basename(attachment_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")

            msg.attach(part)

        except Exception as e:
            self.logger.warning(f"Failed to attach file {attachment_path}: {e}")

    def get_handler_info(self) -> Dict[str, Any]:
        """Get email-specific handler information."""
        info = super().get_handler_info()
        info.update(
            {
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port,
                "from_email": self.from_email,
                "supports_html": True,
                "supports_attachments": True,
                "configured": bool(
                    self.smtp_host and self.smtp_user and self.smtp_password
                ),
            }
        )
        return info
