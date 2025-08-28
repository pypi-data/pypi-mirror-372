import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Try to import the module directly first
try:
    from src.reporting.email_sender import EmailSender
except ImportError:
    # If that fails, add the project root to the Python path and try again
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.reporting.email_sender import EmailSender


class TestEmailSender(unittest.TestCase):
    """Test cases for the EmailSender class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use environment variables or test credentials
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))
        self.username = os.getenv("TEST_EMAIL_USER")
        self.password = os.getenv("TEST_EMAIL_PASSWORD")
        self.recipient = os.getenv("TEST_RECIPIENT_EMAIL", "test@example.com")

        if not self.username or not self.password:
            self.skipTest("Email credentials not provided in environment variables")

        self.sender = EmailSender(
            smtp_server=self.smtp_server,
            smtp_port=self.smtp_port,
            username=self.username,
            password=self.password,
        )

        # Create a test report file
        self.test_report_path = Path("test_report.html")
        with open(self.test_report_path, "w") as f:
            f.write("<html><body><h1>Test Report</h1></body></html>")

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Remove test report file if it exists
        if self.test_report_path.exists():
            self.test_report_path.unlink()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_success(self, mock_smtp: MagicMock) -> None:
        """Test sending a basic email successfully."""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Test data
        subject = "Test Email"
        html_content = "<h1>Test Email</h1><p>This is a test email.</p>"

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient, subject=subject, html_content=html_content
        )

        # Assertions
        assert result
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_server.login.assert_called_once_with(self.username, self.password)
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_report_success(self, mock_smtp: MagicMock) -> None:
        """Test sending a report email successfully."""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Test data
        report_type = "Test Report"

        # Call the method
        result = self.sender.send_report(
            to_email=self.recipient,
            report_path=self.test_report_path,
            report_type=report_type,
        )

        # Assertions
        assert result
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_server.login.assert_called_once_with(self.username, self.password)
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_with_attachments(self, mock_smtp: MagicMock) -> None:
        """Test sending an email with attachments."""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Test data
        subject = "Test Email with Attachment"
        html_content = "<h1>Test Email</h1><p>This email has an attachment.</p>"

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient,
            subject=subject,
            html_content=html_content,
            attachments=[self.test_report_path],
        )

        # Assertions
        assert result
        mock_smtp.assert_called_once_with(self.smtp_server, self.smtp_port)
        mock_server.login.assert_called_once_with(self.username, self.password)
        mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_with_template(self, mock_smtp: MagicMock) -> None:
        """Test sending an email using a template."""
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        # Create a test template
        template_dir = Path("src/reporting/templates")
        template_dir.mkdir(parents=True, exist_ok=True)
        test_template = template_dir / "test_template.html"
        test_template.write_text(
            """
        <h1>{{ subject }}</h1>
        <p>Hello, {{ recipient }}!</p>
        <p>{{ message }}</p>
        """
        )

        try:
            # Test data
            context = {
                "message": "This is a test message from template.",
                "additional_data": "Some additional data",
            }

            # Call the method
            result = self.sender.send_email(
                to_email=self.recipient,
                subject="Test Template Email",
                template_name="test_template.html",
                context=context,
            )

            # Assertions
            assert result
            mock_server.send_message.assert_called_once()

        finally:
            # Clean up test template
            if test_template.exists():
                test_template.unlink()

    @patch("smtplib.SMTP_SSL")
    def test_send_email_failure(self, mock_smtp: MagicMock) -> None:
        """Test handling of email sending failure."""
        # Setup mock to raise an exception
        mock_smtp.side_effect = Exception("SMTP Connection Error")

        # Call the method
        result = self.sender.send_email(
            to_email=self.recipient,
            subject="Test Failure",
            html_content="<p>This should fail</p>",
        )

        # Assertions
        assert not result


if __name__ == "__main__":
    unittest.main()
