"""
broker.py

This module provides a `Broker` client class for interacting with the Broker Service API.
It is designed to handle key operations such as authentication, retrieving user balances and holdings,
authorizing holdings, validating broker users, handling user trading instructions, and acknowledging
surveillance orders.

The client is initialized with contextual information such as `service_user`, `request_id`, and
`tenant_id`, which are common to all requests. However, parameters like `broker_name`, `user_id`,
and `entity_id` are passed at the method level for better flexibility and multi-user support.

The `Broker` class extends the `ApiClient` class from `bw_essentials` and relies on its
HTTP request methods (`_get`, `_post`) for communication with the Broker Service.

Typical usage example:
    broker = Broker(
        service_user="system"
    )

    balance = broker.get_balance(broker_name="kite", user_id="U123")

APIs supported:
- Authenticate with the broker
- Get user balance and holdings
- Validate authentication for a broker user
- Fetch CDSL redirect link for holdings authorization
- Send user trading instructions
- Post trade details
- Acknowledge surveillance orders
"""
import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class Broker(ApiClient):
    """
    Class for making API calls to the Broker Service.
    """

    def __init__(self,
                 service_user: str):
        """
        Initialize the Broker API client.

        Args:
            service_user (str): Service user identifier.
        """
        logger.info(f"Initializing Broker client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.BROKER.value)
        self.name = Services.BROKER.value

        self.urls = {
            "balance": "brokers/{}/balance",
            "holdings": "brokers/{}/holdings",
            "validate_auth": "brokers/{}/auth/validate",
            "authorised_holdings": "brokers/{}/holdings/authorise",
            "user_instructions": "brokers/{}/user/instructions",
            "details": "brokers/{}/trade/details",
            "surveillance_orders": "brokers/{}/surveillance/orders"
        }

    def authenticate(self, broker_name: str, user_id: str, entity_id: str,
                     access_token: str = None, group_id: str = None,
                     session_id: str = None, session_key: str = None,
                     participant_id: str = None, client_order_number: str = None):
        """
        Authenticate the user with the broker service.

        Args:
            broker_name (str): Name of the broker.
            user_id (str): User identifier.
            entity_id (str): Entity identifier.
            access_token (str, optional): Broker access token.
            group_id (str, optional): Group ID for session.
            session_id (str, optional): Broker session ID.
            session_key (str, optional): Session key.
            participant_id (str, optional): Participant ID.
            client_order_number (str, optional): Client order reference number.
        """
        data = {
            "user_id": user_id,
            "entity_id": entity_id,
            "access_token": access_token,
            "group_id": group_id,
            "session_id": session_id,
            "session_key": session_key,
            "participant_id": participant_id,
            "client_order_number": client_order_number
        }
        logger.info(f"In - authenticate {data =}")
        filtered_data = {k: v for k, v in data.items() if v is not None}
        endpoint = f"brokers/{broker_name}/auth"
        self._post(url=self.base_url, endpoint=endpoint, json=filtered_data)

    def get_balance(self, broker_name: str, user_id: str) -> float:
        """
        Fetch user balance from the broker service.

        Args:
            broker_name (str): Broker name.
            user_id (str): User ID.

        Returns:
            float: Account balance.
        """
        logger.info(f"In - get_balance {user_id =}")
        response = self._get(
            url=self.base_url,
            endpoint=self.urls["balance"].format(broker_name),
            params={"user_id": user_id}
        )
        logger.info(f"{response =}")
        return response["data"]["balance"]

    def get_holdings(self, broker_name: str, user_id: str) -> list:
        """
        Fetch user holdings from the broker service.

        Args:
            broker_name (str): Broker name.
            user_id (str): User ID.

        Returns:
            list: List of user holdings.
        """
        logger.info(f"In - get_holdings {user_id =}")
        response = self._get(
            url=self.base_url,
            endpoint=self.urls["holdings"].format(broker_name),
            params={"user_id": user_id}
        )
        logger.info(f"{response =}")
        return response["data"]["holdings"]

    def validate_auth(self, broker_name: str, broker_user_id: str) -> bool:
        """
        Validate a broker user's authentication.

        Args:
            broker_name (str): Broker name.
            broker_user_id (str): Broker-specific user ID.

        Returns:
            bool: Authentication validity status.
        """
        payload = {
            "user_id": broker_user_id,
            "broker": broker_name
        }
        logger.info(f"In - validate_auth {payload =}")
        response = self._get(
            url=self.base_url,
            endpoint=self.urls["validate_auth"].format(broker_name),
            params=payload
        )
        logger.info(f"{response =}")
        return response["data"]["auth_valid"]

    def get_cdsl_redirect(self, broker_name: str, user_id: str, holdings_to_authorize: list, request_url: str = None) -> dict:
        """
        Generate a CDSL redirect for authorizing holdings.

        Args:
            broker_name (str): Broker name.
            user_id (str): User ID.
            holdings_to_authorize (list): Holdings to authorize.
            request_url (str, optional): Redirect return URL.

        Returns:
            dict: Redirect information from the broker.
        """
        payload = {
            "user_id": user_id,
            "request_url": request_url,
            "authorise_holdings": holdings_to_authorize
        }
        logger.info(f"In - get_cdsl_redirect {payload =}")
        response = self._post(
            url=self.base_url,
            endpoint=self.urls["authorised_holdings"].format(broker_name),
            json=payload
        )
        logger.info(f"{response =}")
        return response["data"]

    def user_instructions(self, broker_name: str, instructions: dict) -> dict:
        """
        Send user instructions to the broker.

        Args:
            broker_name (str): Broker name.
            instructions (dict): User instructions payload.

        Returns:
            dict: Response data from broker service.
        """
        logger.info(f"In - user_instructions {instructions =}")
        response = self._post(
            url=self.base_url,
            endpoint=self.urls["user_instructions"].format(broker_name),
            json=instructions
        )
        logger.info(f"{response =}")
        return response["data"]

    def trade_details(self, broker_name: str, details: dict) -> list:
        """
        Send trade details to the broker.

        Args:
            broker_name (str): Broker name.
            details (dict): Trade details payload.

        Returns:
            list: Broker response data.
        """
        logger.info(f"In - trade_details {details =}")
        response = self._post(
            url=self.base_url,
            endpoint=self.urls["details"].format(broker_name),
            json=details
        )
        logger.info(f"{response =}")
        return response["data"]

    def acknowledge_for_surveillance_orders(self, broker_name: str, surveillance_orders: list) -> None:
        """
        Acknowledge surveillance orders to the broker.

        Args:
            broker_name (str): Broker name.
            surveillance_orders (list): List of validated surveillance orders.

        Returns:
            None
        """
        logger.info(f"In - acknowledge_for_surveillance_orders {surveillance_orders =}")
        payload = {"surveillance_orders": surveillance_orders}
        response = self._post(
            url=self.base_url,
            endpoint=self.urls["surveillance_orders"].format(broker_name),
            json=payload
        )
        logger.info(f"{response =}")
