"""
notifications.py

This module provides a `Notifications` class for sending structured messages and alerts
to external communication tools such as Microsoft Teams and Zenduty. It is used to
inform stakeholders or developers about system events, including errors and general logs.
"""

import json
import logging
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec

import requests

from bw_essentials.notifications.teams_notification_schemas import get_notification_schema, get_error_schema

logger = logging.getLogger(__name__)


class Notifications:
    """
    Notification module to send alerts and warnings via Microsoft Teams and Zenduty.

    Args:
        title (str): The title or service name triggering the notification.
        summary (str, optional): A brief summary of the message or error.
        message (str, optional): The main body of the message.
        alert (bool, optional): If True, it's treated as an error; otherwise as a log. Defaults to False.
        trace (str, optional): Optional traceback or detailed error string.
        request_id (str, optional): Optional correlation ID for tracing logs.
        webhook_url(str, Optional): Optional webhook url for teams channel.
    """

    def __init__(self,
                 title,
                 summary=None,
                 message=None,
                 alert=False,
                 trace=None,
                 request_id=None,
                 webhook_url=None):
        self.message = message
        self.title = title
        self.summary = summary
        self.alert = alert
        self.trace = trace
        self.request_id = request_id
        self.notify_on_teams = self._get_env_var("NOTIFY_ON_TEAMS")
        self.notify_on_calls = self._get_env_var("NOTIFY_ON_CALLS")
        self.webhook_url = self._get_env_var("TEAMS_WEBHOOK_URL", webhook_url)
        self.zenduty_url = self._get_env_var("ZENDUTY_URL")
        self.api_timeout = self._get_env_var("API_TIMEOUT")

    def _get_env_var(self, key: str, webhook_url: str = None) -> str:
        """
        Fetch a required variable from bw_config.py located in the root directory.
        Args:
            webhook_url(Optional[str]): Optional Teams webhook url at the time of initialisation.
        Raises:
            FileNotFoundError: If bw_config.py is not found.
            AttributeError: If the requested key is not defined in the config.

        Returns:
            str: The value of the config variable.
        """
        if webhook_url:
            return webhook_url

        config_path = os.path.join(os.getcwd(), "bw_config.py")

        if not os.path.exists(config_path):
            raise FileNotFoundError("`bw_config.py` file not found in the root directory. "
                                    "Please ensure the config file exists.")

        spec = spec_from_file_location("bw_config", config_path)
        bw_config = module_from_spec(spec)
        sys.modules["bw_config"] = bw_config
        spec.loader.exec_module(bw_config)

        if not hasattr(bw_config, key):
            raise AttributeError(f"`{key}` not found in bw_config.py. Please either define it in the config or"
                                 f"pass it during Notifications init")

        return getattr(bw_config, key)

    def __notify_teams_workflow(self):
        """
        Sends a notification to Microsoft Teams using Adaptive Cards.

        Uses either the error schema or the log schema based on whether the notification
        is an alert or not. This function posts the generated card payload to the configured
        Teams webhook URL.

        Returns:
            None
        """
        logger.info("In __notify_teams_workflow")
        try:
            if self.notify_on_teams:
                workflow_schema = get_notification_schema(self.title, self.message)
                if self.alert:
                    workflow_schema = get_error_schema(
                        service_url=self.title,
                        message=self.message,
                        summary=self.summary,
                        error_trace=self.trace,
                        request_id=self.request_id
                    )

                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(workflow_schema),
                    headers=headers
                )
                logger.info(f"{response =}")
            else:
                logger.info(f"Notification for teams is {self.notify_on_teams}. Message: {self.message}")
        except Exception as exc:
            logger.info("Error while notifying error to teams.")
            logger.exception(exc)

    def __notify_zenduty(self):
        """
        Sends a critical alert to Zenduty via its API endpoint.

        Posts a payload including alert type, message, and summary. Primarily used for error alerts.

        Returns:
            None
        """
        if self.notify_on_calls:
            payload = {
                "alert_type": "critical",
                "message": self.message,
                "summary": self.summary
            }
            payload_json = json.dumps(payload)
            response = requests.post(
                self.zenduty_url,
                data=payload_json,
                timeout=float(self.api_timeout)
            )
            logger.info(response)
            logger.info("Response from Zenduty Call API: An incident has been created")

    def notify_message(self, message=None, summary=None, alert=False):
        """
        Sends a general log or information notification.

        Args:
            message (str, optional): The content of the message. Overrides initial message if provided.
            summary (str, optional): Optional summary for the message.
            alert (bool, optional): If True, message is sent as an alert.

        Returns:
            None
        """
        try:
            self.alert = alert
            if message:
                self.message = message
            if summary:
                self.summary = summary
            self.__notify_teams_workflow()
        except Exception as exc:
            logger.info("Error while notifying message to teams")
            logger.exception(exc)

    def notify_error(self, message=None, summary=None, alert=True, trace=None, request_id=None):
        """
        Sends an error notification to Microsoft Teams and Zenduty.

        Args:
            message (str, optional): Error message to be sent.
            summary (str, optional): Summary or context for the error.
            alert (bool, optional): Flag to indicate it's an error. Defaults to True.
            trace (str, optional): Detailed traceback or stack trace of the error.
            request_id (str, optional): Optional request ID for tracking.

        Returns:
            None
        """
        self.alert = alert
        if summary:
            self.summary = summary
        if message:
            self.message = message
        if trace:
            self.trace = trace
        if request_id:
            self.request_id = request_id
        self.__notify_zenduty()
        self.__notify_teams_workflow()
