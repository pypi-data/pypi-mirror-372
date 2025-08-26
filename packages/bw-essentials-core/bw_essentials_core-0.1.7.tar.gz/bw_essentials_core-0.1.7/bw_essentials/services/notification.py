"""
Module to make API calls to Notification Service
"""
import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class NotificationService(ApiClient):
    """
    Handles notifications through various channels.
    """
    PLATFORM = "PLATFORM"
    NOTIFICATION_API_KEY = 'NOTIFICATION_API_KEY'
    NOTIFICATION_SENDER_NUMBER = "NOTIFICATION_SENDER_NUMBER"

    def __init__(self):
        """
        Initializes the Notification object.

        Args:
        - user: The user associated with the notification.
        """
        super().__init__("notification")
        self.name = Services.NOTIFICATION.value
        self.base_url = self.get_base_url(self.name)
        self.urls = {
            "whatsapp": "whatsapp",
            "email": "email"
        }

    def _whatsapp(self, title, template, platform, params, to, user_id) -> None:
        """
        Sends a WhatsApp notification.

        Args:
        - user_id (str): The ID of the user receiving the notification.
        - number (str): The phone number for the recipient.
        - title (str): Title of the notification.
        - template (str): Template for the WhatsApp message.
        - platform (str): The platform used for sending
            (WhatsApp, in this case).
        - params: Parameters for the notification message.

        Returns:
        None
        """
        logger.info(f"In - whatsapp {user_id =}, {to =}, "
                    f"{title =}, {template =}, {platform =}, {params =}")
        payload = {
            "from": self._get_env_var(NotificationService.NOTIFICATION_SENDER_NUMBER),
            "to": to,
            "userId": user_id,
            "platform": platform,
            "title": title,
            "template": template,
            "params": params
        }
        logger.info(f"whatsapp {payload =}")
        headers = {
            'api-key': self._get_env_var(NotificationService.NOTIFICATION_API_KEY)
        }
        self.set_headers(headers)
        resp_data = self._post(url=self.base_url, endpoint=self.urls.get('whatsapp'), data=payload)
        logger.info(f"Whatsapp response {resp_data =}")

    def send_whatsapp(self, template, title, params, to, user_id) -> None:
        """

        Args:
            template (str): Template for the WhatsApp message.
            title (str): Title of the notification.
            params: Parameters for the notification message.
            to (str): Recipient's whatsapp number.
            user_id (str): The ID of the user receiving the notification.

        Returns:
            None
        """
        logger.info(f"In - send_whatsapp_notification {user_id =} {title = } {params = } {to = }")
        self._whatsapp(title=title,
                       template=template,
                       platform=self._get_env_var(NotificationService.PLATFORM),
                       params=params,
                       to=to,
                       user_id=user_id)

    def _email(self, title: str, content: str, platform: str, to: str, user_id: str) -> None:
        """
        Sends an email notification using the internal notification service.

        Args:
            title (str): The subject or title of the email.
            content (str): The HTML or plain text body of the email.
            platform (str): The platform identifier from which the email is sent (e.g., 'prometheus').
            to (str): Recipient's email address.
            user_id (str): The ID of the user for tracking or logging purposes.

        Returns:
            None

        """
        logger.info(f"In - email {user_id =}, {to =}, {title =}, {platform =}, {content =}")
        payload = {
            "to": to,
            "userId": user_id,
            "platform": platform,
            "title": title,
            "content": content
        }
        logger.info(f"email {payload =}")
        headers = {
            'api-key': self._get_env_var(NotificationService.NOTIFICATION_API_KEY),
            'Content-Type': 'application/json'
        }
        self.set_headers(headers)
        resp_data = self._post(url=self.base_url, endpoint=self.urls.get('email'), json=payload)
        logger.info(f"Email response {resp_data =}")

    def send_email(self, title: str, content: str, to: str, user_id: str) -> None:
        """
        Sends an email notification to the specified recipient.

        Args:
            title (str): The subject or title of the email.
            content (str): The HTML or plain text content of the email.
            to (str): The recipient's email address.
            user_id (str): The ID of the user associated with the notification.

        Returns:
            None
        """
        logger.info(f"In - send_email {user_id =}, {title =}, {to =}")
        self._email(
            title=title,
            content=content,
            platform=self._get_env_var(NotificationService.PLATFORM),
            to=to,
            user_id=user_id
        )
