"""
Email notification module.

This module provides functionality to send stock analysis reports
via email with HTML formatting and attachments.
"""

import logging
import os
import smtplib
import mimetypes
from datetime import datetime
import html2text
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape


logger = logging.getLogger(__name__)


class EmailSender:
    """
    Handles sending emails with reports and notifications.

    This class provides methods to send emails with HTML content
    and file attachments, specifically designed for sending
    stock analysis reports.
    """

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """
        Initialize the email sender with SMTP credentials.

        Args:
            smtp_server: SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port: SMTP server port (e.g., 465 for SSL)
            username: Email username for authentication
            password: Email password or app password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

        # Initialize template environment
        templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
        )
        self.template_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _create_message(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
        from_name: Optional[str] = None,
    ) -> MIMEMultipart:
        """
        Create a MIME message with optional HTML, text, and attachments.

        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text alternative (optional)
            attachments: List of file paths to attach
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to email address
            from_name: Display name for the sender

        Returns:
            MIMEMultipart: The constructed email message
        """
        # Convert single strings to lists
        if isinstance(to_email, str):
            to_email = [to_email]
        if isinstance(cc, str):
            cc = [cc]
        if isinstance(bcc, str):
            bcc = [bcc]

        # Create the root message
        msg = MIMEMultipart("mixed")

        # Set headers
        from_header = f'"{from_name}" <{self.username}>' if from_name else self.username
        msg["From"] = from_header
        msg["To"] = ", ".join(to_email)
        msg["Subject"] = subject

        if cc:
            msg["Cc"] = ", ".join(cc)
        if bcc:
            msg["Bcc"] = ", ".join(bcc)
        if reply_to:
            msg["Reply-To"] = reply_to

        # Create the alternative part for HTML and plain text
        msg_alternative = MIMEMultipart("alternative")
        msg.attach(msg_alternative)

        # Attach text part if provided
        if text_content:
            part1 = MIMEText(text_content, "plain")
            msg_alternative.attach(part1)

        # Attach HTML part
        part2 = MIMEText(html_content, "html")
        msg_alternative.attach(part2)

        # Attach files if any
        if attachments:
            for file_path in attachments:
                file_path = Path(file_path)
                if not file_path.exists():
                    logger.warning(f"Attachment not found: {file_path}")
                    continue

                # Guess content type
                ctype, encoding = mimetypes.guess_type(str(file_path))
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"

                maintype, subtype = ctype.split("/", 1)

                try:
                    with open(file_path, "rb") as fp:
                        if maintype == "text":
                            # Read text file as text
                            attachment = MIMEText(
                                fp.read().decode("utf-8"), _subtype=subtype
                            )
                        elif maintype == "image":
                            # Read image file
                            attachment = MIMEImage(fp.read(), _subtype=subtype)
                        elif maintype == "audio":
                            # Read audio file
                            attachment = MIMEAudio(fp.read(), _subtype=subtype)
                        else:
                            # Read binary file
                            attachment = MIMEBase(maintype, subtype)
                            attachment.set_payload(fp.read())
                            # Encode the payload using Base64
                            encoders.encode_base64(attachment)

                    # Add header for the attachment
                    filename = file_path.name
                    attachment.add_header(
                        "Content-Disposition", "attachment", filename=filename
                    )
                    msg.attach(attachment)

                except Exception as e:
                    logger.error(f"Failed to attach {file_path}: {e}")

        return msg

    def send_email(
        self,
        to_email: Union[str, List[str]],
        subject: str,
        template_name: str = "email_template.html",
        context: Optional[Dict[str, Any]] = None,
        text_content: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None,
        from_name: Optional[str] = "Stock Analysis Pro",
    ) -> bool:
        """Send an email using a template.

        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            template_name: Name of the template file (in templates/email/)
            context: Dictionary with template variables
            text_content: Plain text alternative
                (auto-generated from HTML if not provided)
            attachments: List of file paths to attach
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to email address
            from_name: Display name for the sender

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Prepare context
            context = context or {}
            context.update(
                {
                    "subject": subject,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "year": datetime.now().year,
                    "recipient": (
                        to_email[0] if isinstance(to_email, list) else to_email
                    ),
                    **context,
                }
            )

            # Load and render template
            template = self.template_env.get_template(template_name)
            html_content = template.render(**context)

            # If no text content provided, create a simple version from HTML
            if not text_content and html_content:
                # Simple HTML to text conversion
                text_content = html2text.html2text(html_content)

            # Create the message
            msg = self._create_message(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                from_name=from_name,
            )

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.username, self.password)

                # Prepare recipients list
                recipients = [to_email] if isinstance(to_email, str) else to_email
                if cc:
                    recipients.extend(cc if isinstance(cc, list) else [cc])
                if bcc:
                    recipients.extend(bcc if isinstance(bcc, list) else [bcc])

                # Send the email
                server.send_message(msg)

            logger.info(f"Email sent to {to_email} with subject: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}", exc_info=True)
            return False

    def send_report(
        self,
        to_email: Union[str, List[str]],
        report_path: Union[str, Path],
        report_type: str = "Stock Analysis Report",
        report_summary: Optional[str] = None,
        key_metrics: Optional[List[Dict[str, Any]]] = None,
        recommendations: Optional[List[str]] = None,
        subject: Optional[str] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        from_name: str = "Stock Analysis Pro",
    ) -> bool:
        """
        Send a report via email with a nicely formatted message.

        Args:
            to_email: Recipient email address(es)
            report_path: Path to the report file to attach
            report_type: Type of report
                (e.g., 'Stock Analysis', 'Sector Report')
            report_summary: Summary of the report (HTML supported)
            key_metrics: List of key metrics to highlight
            recommendations: List of recommendations
            subject: Email subject (auto-generated if None)
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            from_name: Display name for the sender

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            report_path = Path(report_path)
            if not report_path.exists():
                logger.error(f"Report file not found: {report_path}")
                return False

            # Generate subject if not provided
            if not subject:
                date_str = datetime.now().strftime("%Y-%m-%d")
                subject = f"{report_type} - {date_str}"

            # Read the report content
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()

            # Prepare context for the email template
            context = {
                "report_type": report_type,
                "report_summary": report_summary
                or f"Please find below your {report_type}.",
                "key_metrics": key_metrics or [],
                "recommendations": recommendations or [],
                # Include the full report content
                "message": report_content,
                # For "View in Browser" links
                "report_url": f"file://{report_path.absolute()}",
            }

            # Send the email with the report attached
            return self.send_email(
                to_email=to_email,
                subject=subject,
                template_name="email_template.html",
                context=context,
                attachments=[report_path],
                cc=cc,
                bcc=bcc,
                from_name=from_name,
            )

        except Exception as e:
            logger.error(f"Failed to send report email: {e}", exc_info=True)
            return False
