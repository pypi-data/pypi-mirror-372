"""
prometheus_user_app.py

Module to interact with the Prometheus User App Service API.

This module provides a high-level client wrapper around the Prometheus User App Service,
enabling secure, structured, and logged communication with its endpoints. It includes:

- Type-safe interfaces
- Detailed request and response logging
- Validated endpoint routing
- Clear, maintainable service integration points
"""

from typing import Optional, Dict, Any
import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class PrometheusUserApp(ApiClient):
    """
    Client for interacting with the Prometheus User App Service API.

    This class handles API communication with Prometheus User App endpoints. It abstracts
    request handling, URL construction, and logging while ensuring robust error management.

    Attributes:
        base_url (str): Base URL derived from tenant configuration
        name (str): Service identifier
        urls (Dict[str, str]): A dictionary of endpoint path templates
    """

    def __init__(self, service_user: str):
        """
        Initialize the PrometheusUserApp client with the given service user.

        Args:
            service_user (str): Username or service identifier for authentication.
        """
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.PROMETHEUS_USER_APP.value)
        self.name = Services.PROMETHEUS_USER_APP.value
        self.urls = {
            "user_details": "user/details",
            "profile": "user/profile",
            "get_profile": "user/profile/",
            "login": "user/login",
            "register_user": "user/register",
            "update_dealer_disclaimer": "user/{}/dealer/disclaimer/",
            "dealer_users": "user/{}/dealer/users",
            "user_disclaimer": "user/{}/disclaimer/",
            "dealer_login": "user/{}/login/dealer",
            "send_otp": "user/{}/otp/send",
            "verify_otp": "user/{}/otp/verify",
            "register_dealer_user": "user/{}/register/dealer",
            "sso": "user/{}/sso"
        }

    def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed user information by user ID.

        Args:
            user_id (str): Unique identifier of the user.

        Returns:
            Optional[Dict[str, Any]]: Parsed user data if found, else None.
        """
        logger.info("Fetching user details for user_id=%s", user_id)
        response = self._get(
            endpoint=self.urls["user_details"],
            url=self.base_url,
            params={'user_id': user_id}
        )
        return response.get('data')

    def update_user_profile(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update the user profile with provided data.

        Args:
            data (Dict[str, Any]): Dictionary containing user profile updates.

        Returns:
            Optional[Dict[str, Any]]: Updated profile data if successful, else None.
        """
        logger.info("Updating user profile with data: %s", data)
        response = self._put(
            endpoint=self.urls["profile"],
            url=self.base_url,
            data=data
        )
        return response.get('data')

    def login(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user using credentials.

        Args:
            user_id (str): User identifier (e.g., username).
            password (str): User password.

        Returns:
            Optional[Dict[str, Any]]: Auth token or login response if successful.
        """
        logger.info("Logging in user %s", user_id)
        response = self._post(
            endpoint=self.urls["login"],
            url=self.base_url,
            json={'username': user_id, 'password': password}
        )
        return response.get('data')

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve profile details of a user.

        Args:
            user_id (str): Unique user identifier.

        Returns:
            Optional[Dict[str, Any]]: User profile information if successful.
        """
        logger.info("Fetching profile for user %s", user_id)
        response = self._get(
            endpoint=self.urls["get_profile"],
            url=self.base_url
        )
        return response.get('data')

    def register_user(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Register a new user with the service.

        Args:
            data (Dict[str, Any]): Registration details including user information.

        Returns:
            Optional[Dict[str, Any]]: Registration confirmation or created user details.
        """
        logger.info("Registering new user with data: %s", data)
        response = self._post(
            endpoint=self.urls["register_user"],
            url=self.base_url,
            json=data
        )
        return response

    def update_dealer_disclaimer(self, broker: str, user_id: str, disclaimer_accepted: bool) -> Optional[Dict[str, Any]]:
        """
        Update a user's dealer disclaimer status.

        Args:
            broker (str): Broker identifier.
            user_id (str): User ID whose disclaimer is being updated.
            disclaimer_accepted (bool): Whether disclaimer is accepted.

        Returns:
            Optional[Dict[str, Any]]: Updated disclaimer status if successful.
        """
        logger.info("Updating dealer disclaimer for user_id=%s, broker=%s", user_id, broker)
        response = self._put(
            endpoint=self.urls["update_dealer_disclaimer"].format(broker),
            url=self.base_url,
            json={'disclaimer_accepted': disclaimer_accepted, 'user_id': user_id}
        )
        return response.get('data')

    def dealer_users(self, broker: str, dealer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get users associated with a specific dealer.

        Args:
            broker (str): Broker name.
            dealer_id (str): Dealer identifier.

        Returns:
            Optional[Dict[str, Any]]: List of users or None if failed.
        """
        logger.info("Fetching dealer users for broker=%s, dealer_id=%s", broker, dealer_id)
        response = self._post(
            endpoint=self.urls["dealer_users"].format(broker),
            url=self.base_url,
            json={'dealer_id': dealer_id}
        )
        return response.get('data')

    def user_disclaimer(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Fetch disclaimer details for a user under a specific broker.

        Args:
            broker (str): Broker name.
            data (Dict[str, Any]): Payload for disclaimer lookup.

        Returns:
            Optional[Dict[str, Any]]: Disclaimer information if available.
        """
        logger.info("Fetching user disclaimer for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["user_disclaimer"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def dealer_login(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform login for a dealer under the specified broker.

        Args:
            broker (str): Broker identifier.
            data (Dict[str, Any]): Login payload.

        Returns:
            Optional[Dict[str, Any]]: Login response if successful.
        """
        logger.info("Dealer login request for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["dealer_login"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def send_otp(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send OTP to user for verification under a broker.

        Args:
            broker (str): Broker name.
            data (Dict[str, Any]): Payload including mobile/email.

        Returns:
            Optional[Dict[str, Any]]: Response with OTP status.
        """
        logger.info("Sending OTP for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["send_otp"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def verify_otp(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Verify user OTP under a broker.

        Args:
            broker (str): Broker name.
            data (Dict[str, Any]): OTP verification data.

        Returns:
            Optional[Dict[str, Any]]: Verification status.
        """
        logger.info("Verifying OTP for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["verify_otp"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def register_dealer_user(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Register a new dealer user.

        Args:
            broker (str): Broker name.
            data (Dict[str, Any]): Dealer user details.

        Returns:
            Optional[Dict[str, Any]]: Registration status or dealer user details.
        """
        logger.info("Registering dealer user for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["register_dealer_user"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def update_dealer_user(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing dealer user's information.

        Args:
            broker (str): Broker name.
            data (Dict[str, Any]): Dealer user update payload.

        Returns:
            Optional[Dict[str, Any]]: Updated dealer user data.
        """
        logger.info("Updating dealer user for broker=%s, data=%s", broker, data)
        response = self._put(
            endpoint=self.urls["register_dealer_user"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')

    def sso(self, broker: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform Single Sign-On (SSO) operation.

        Args:
            broker (str): Broker identifier.
            data (Dict[str, Any]): SSO payload.

        Returns:
            Optional[Dict[str, Any]]: SSO token or user session.
        """
        logger.info("Performing SSO for broker=%s, data=%s", broker, data)
        response = self._post(
            endpoint=self.urls["sso"].format(broker),
            url=self.base_url,
            json=data
        )
        return response.get('data')
