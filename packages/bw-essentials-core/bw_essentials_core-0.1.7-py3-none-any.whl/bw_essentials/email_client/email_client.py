"""
email_client.py

This module defines the EmailClient class for sending emails using SMTP. It provides
methods to send emails with or without file attachments and supports multiple recipients
and CC addresses. The email body can be plain text or HTML.

Usage:
    client = EmailClient(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user",
        smtp_password="pass",
        sender_email="from@example.com",
        sender_name="My Service"
    )

    client.send_email_without_attachment(
        to_addresses=["to@example.com"],
        cc_addresses=["cc@example.com"],
        subject="Test Email",
        body="Hello, this is a test email!"
    )

    client.send_email_with_attachment(
        to_addresses="to@example.com",
        cc_addresses=None,
        subject="Report",
        body="<h1>Monthly Report</h1>",
        attachment_path="/path/to/report.csv"
    )
"""

import logging
import os
import smtplib
import sys
from importlib.util import spec_from_file_location, module_from_spec
from typing import Optional, List, Union
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


class EmailClient:
    """
    A reusable and configurable email client for sending emails using SMTP.

    Attributes:
        smtp_host (str): SMTP server hostname or IP address.
        smtp_port (int): SMTP server port (commonly 587 for TLS).
        smtp_username (str): SMTP username for authentication.
        smtp_password (str): SMTP password for authentication.
        sender_email (str): Email address used as the sender.
        sender_name (str): Display name for the sender.
    """

    def __init__(
        self,
        sender_email: str,
        sender_name: str,
    ):
        """
        Initialize the EmailClient with SMTP server credentials.

        Args:
            sender_email (str): Sender's email address.
            sender_name (str): Display name to show in "From" field.
        """
        self.smtp_host = self._get_env_var("SMTP_HOST")
        self.smtp_port = self._get_env_var("SMTP_PORT")
        self.smtp_username = self._get_env_var("SMTP_USERNAME")
        self.smtp_password = self._get_env_var("SMTP_PASSWORD")
        self.sender_email = sender_email
        self.sender_name = sender_name
        logger.info("EmailClient initialized with SMTP host: %s", self.smtp_host)

    def _get_env_var(self, key: str) -> str:
        """
        Fetch a required variable from bw_config.py located in the root directory.

        Raises:
            FileNotFoundError: If bw_config.py is not found.
            AttributeError: If the requested key is not defined in the config.

        Returns:
            str: The value of the config variable.
        """
        config_path = os.path.join(os.getcwd(), "bw_config.py")

        if not os.path.exists(config_path):
            raise FileNotFoundError("`bw_config.py` file not found in the root directory. "
                                    "Please ensure the config file exists.")

        spec = spec_from_file_location("bw_config", config_path)
        bw_config = module_from_spec(spec)
        sys.modules["bw_config"] = bw_config
        spec.loader.exec_module(bw_config)

        if not hasattr(bw_config, key):
            raise AttributeError(f"`{key}` not found in bw_config.py. Please define it in the config.")

        return getattr(bw_config, key)

    def send_email_without_attachment(
        self,
        to_addresses: Union[str, List[str]],
        cc_addresses: Union[str, List[str], None],
        subject: str,
        body: str,
        is_html: bool = True,
    ):
        """
        Send an email without any attachments.

        Args:
            to_addresses (Union[str, List[str]]): One or more recipient email addresses.
            cc_addresses (Union[str, List[str], None]): One or more CC addresses (optional).
            subject (str): Email subject line.
            body (str): Email body content.
            is_html (bool): If True, body is interpreted as HTML; otherwise, plain text.
        """
        logger.info("Preparing to send email without attachment | Subject: %s", subject)
        self._send_email(to_addresses, cc_addresses, subject, body, None, is_html)

    def send_email_with_attachment(
        self,
        to_addresses: Union[str, List[str]],
        cc_addresses: Union[str, List[str], None],
        subject: str,
        body: str,
        attachment_path: str,
        is_html: bool = True,
    ):
        """
        Send an email with a file attachment.

        Args:
            to_addresses (Union[str, List[str]]): One or more recipient email addresses.
            cc_addresses (Union[str, List[str], None]): One or more CC addresses (optional).
            subject (str): Email subject line.
            body (str): Email body content.
            attachment_path (str): Full path to the file to attach.
            is_html (bool): If True, body is interpreted as HTML; otherwise, plain text.
        """
        logger.info(
            "Preparing to send email with attachment | Subject: %s | Attachment: %s",
            subject, attachment_path
        )
        self._send_email(to_addresses, cc_addresses, subject, body, attachment_path, is_html)

    def _send_email(
        self,
        to_addresses: Union[str, List[str]],
        cc_addresses: Union[str, List[str], None],
        subject: str,
        body: str,
        attachment_path: Optional[str],
        is_html: bool,
    ):
        """
        Internal helper method to construct and send email messages.

        Args:
            to_addresses (Union[str, List[str]]): One or more recipient email addresses.
            cc_addresses (Union[str, List[str], None]): CC addresses.
            subject (str): Subject of the email.
            body (str): Email body content.
            attachment_path (Optional[str]): File path for the attachment, if any.
            is_html (bool): True if the body is HTML-formatted.
        """
        msg = MIMEMultipart()
        msg['From'] = f'"{self.sender_name}" <{self.sender_email}>'
        msg['To'] = self._format_addresses(to_addresses)
        msg['Cc'] = self._format_addresses(cc_addresses) if cc_addresses else ""
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        logger.debug("Email headers and body constructed")

        if attachment_path:
            if not os.path.exists(attachment_path):
                logger.warning("Attachment file not found: %s", attachment_path)
            else:
                try:
                    with open(attachment_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment',
                                        filename=os.path.basename(attachment_path))
                        msg.attach(part)
                        logger.info("Attachment added: %s", os.path.basename(attachment_path))
                except Exception as e:
                    logger.exception("Failed to read attachment file")
                    raise e

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                recipients = self._get_recipient_list(to_addresses, cc_addresses)
                server.sendmail(self.sender_email, recipients, msg.as_string())
                logger.info("Email sent to %s with CC %s", to_addresses, cc_addresses)
        except Exception as e:
            logger.exception("Failed to send email")
            raise e

    def _format_addresses(self, addresses: Union[str, List[str]]) -> str:
        """
        Convert a string or list of email addresses to a comma-separated string.

        Args:
            addresses (Union[str, List[str]]): Email addresses.

        Returns:
            str: Comma-separated email addresses.
        """
        if isinstance(addresses, list):
            return ", ".join(addresses)
        return addresses

    def _get_recipient_list(
        self,
        to_addresses: Union[str, List[str]],
        cc_addresses: Union[str, List[str], None]
    ) -> List[str]:
        """
        Merge TO and CC addresses into a single list for email sending.

        Args:
            to_addresses (Union[str, List[str]]): Main recipients.
            cc_addresses (Union[str, List[str], None]): CC recipients.

        Returns:
            List[str]: List of all email recipients.
        """
        to_list = to_addresses if isinstance(to_addresses, list) else [to_addresses]
        cc_list = cc_addresses if isinstance(cc_addresses, list) else [cc_addresses] if cc_addresses else []
        return to_list + cc_list
