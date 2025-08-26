"""
Module to make API calls to User Portfolio service.
"""
import json
import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class UserPortfolio(ApiClient):
    """
    Class for making API calls to the User Portfolio Service.

    Args:
    user (str): The user for whom the API calls are being made.
    """

    def __init__(self, service_user: str):
        logger.info(f"Initializing UserPortfolio client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.USER_PORTFOLIO.value)
        self.name = Services.USER_PORTFOLIO.value
        self.urls = {
            "holding_transaction": "holding/transaction",
            "portfolio_rebalance": "userportfolio/portfolio/rebalance",
            "rebalance_transaction": "userportfolio/portfolio/rebalance/transaction",
            "user_instructions": "userportfolio/portfolio/rebalance/transaction/user-instruction",
            "user_inputs": "userportfolio/portfolio/rebalance",
            "user_portfolio_holdings": "holding/holdings",
            "user_holdings": "holding/user/holdings",
            "user_portfolios": "userportfolio/portfolio",
            "orders": "userportfolio/portfolio/rebalance/orders",
            "update_user_portfolio_rebalance": "userportfolio/portfolio/rebalance",
            "update_portfolio_transaction": "userportfolio/portfolio/rebalance/transactions",
            "complete_rebalance_transaction": "userportfolio/portfolio/rebalance/transactions/complete",
            "get_portfolio_rebalances": "userportfolio/portfolio/rebalance",
            "create_basket": "userportfolio/basket",
            "order_instructions": "userportfolio/order/instructions/",
            "retry": "userportfolio/order/retry/basket",
            "skip": "userportfolio/order/skip/basket",
            "create_order_instructions": "userportfolio/order/order-instruction",
            "basket_details": "userportfolio/basket",
            "broker_users_holdings": "holding/{}/users"
        }

    def create_holding_transaction(self, payload):
        """
        Make a holding transaction.

        Args:
        payload (str): The payload for the holding transaction.
        Returns:
        dict: Holding transaction data.
        """
        logger.info(f"In - holding_transaction {payload =}")
        data = self._post(url=self.base_url,
                          endpoint=self.urls.get("holding_transaction"),
                          data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def create_portfolio_rebalance(self, payload):
        """
        Perform a portfolio rebalance.

        Args:
        payload (str): The payload for the portfolio rebalance.

        Returns:
        dict: Portfolio rebalance data.
        """
        logger.info(f"In - portfolio_rebalance {payload =}")
        data = self._post(url=self.base_url,
                          endpoint=self.urls.get("portfolio_rebalance"),
                          data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def create_rebalance_transaction(self, payload):
        """
        Perform a rebalance transaction.

        Args:
        payload (str): The payload for the rebalance transaction.

        Returns:
        dict: Rebalance transaction data.
        """
        logger.info(f"In - rebalance_transaction {payload =}")
        data = self._post(url=self.base_url,
                          endpoint=self.urls.get("rebalance_transaction"),
                          data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def update_user_instructions(self, payload):
        """
        Provide user instructions.

        Args:
        payload (str): The payload for user instructions.

        """
        logger.info(f"In - user_instructions {payload =}")
        payload['filled_quantity'] = payload['quantity']
        payload = json.dumps(payload)
        data = self._put(url=self.base_url,
                         endpoint=self.urls.get("user_instructions"),
                         data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def get_user_inputs(self, params, user_portfolio_id):
        """
        Get user inputs for a specific user portfolio.

        Args:
        params (dict): Additional parameters for the request.
        user_portfolio_id (str): The ID of the user portfolio.

        Returns:
        dict: User inputs data.
        """
        logger.info(f"In - user_inputs {params =}, {user_portfolio_id =}")
        data = self._get(url=self.base_url,
                         endpoint=f'{self.urls.get("user_inputs")}/{user_portfolio_id}',
                         params=params)
        logger.info(f"{data =}")
        return data.get("data")

    def get_user_portfolio_holdings(self, user_portfolio_id):
        """
        Get user holdings for a specific user portfolio.

        Args:
        user_portfolio_id (str): The ID of the user portfolio.
        Returns:
        dict: User holdings data.
        """
        logger.info(f"In - user_holdings {user_portfolio_id =}")
        data = self._get(url=self.base_url,
                         endpoint=f'{self.urls.get("user_portfolio_holdings")}/{user_portfolio_id}')
        logger.info(f"{data =}")
        return data.get("data")

    def get_user_holdings(self, user_id, broker):
        """
        Get user holdings for a all user portfolios.

        Args:
        user_id (str): The ID of the user portfolio.
        broker (str): Broker of user

        Returns:
        dict: User holdings data.
        """
        logger.info(f"In - user_holdings {user_id = }, {broker = }")
        data = self._get(url=self.base_url,
                         endpoint=f'{self.urls.get("user_holdings")}/{user_id}',
                         params={"broker": broker})
        logger.info(f"{data =}")
        return data.get("data")

    def get_user_portfolio_by_id(self, user_portfolio_id):
        """
        Retrieves a user's portfolio data by the provided ID.

        Args:
        - user_portfolio_id (str): The ID of the user's portfolio.

        Returns:
        - dict: The data associated with the user's portfolio.
        """
        logger.info(f"In - user_holdings {user_portfolio_id =}")
        data = self._get(url=self.base_url,
                         endpoint=f'{self.urls.get("user_portfolios")}/{user_portfolio_id}')
        logger.info(f"{data =}")
        return data.get("data")

    def get_rebalance_orders(self, rebalance_type, user_portfolio_rebalance_id):
        """
        Fetches rebalance orders for a specific user portfolio rebalance.

        Args:
        - rebalance_type: Type of rebalance.
        - user_portfolio_rebalance_id: ID of the user's portfolio rebalance.

        Returns:
        - dict: Data related to rebalance orders.
        """
        logger.info(f"In - rebalance_orders {rebalance_type =}, {user_portfolio_rebalance_id =}")
        data = self._get(url=self.base_url,
                         endpoint=f'{self.urls.get("orders")}',
                         params={"type": rebalance_type,
                                 "user_portfolio_rebalance_id": user_portfolio_rebalance_id
                                 })
        logger.info(f"{data =}")
        return data.get("data")

    def update_user_portfolio_rebalance(self, payload, user_portfolio_rebalance_id):
        """
        Update a user's portfolio rebalance.

        Args:
        - payload (dict): The data payload to update the user's portfolio rebalance.
        - user_portfolio_rebalance_id (int): The ID of the user's portfolio rebalance to be updated.

        Returns:
        - dict: The updated data of the user's portfolio rebalance.
        """
        logger.info(f"In - update_user_portfolio_rebalance {payload =}, {user_portfolio_rebalance_id =}")
        data = self._put(url=self.base_url,
                         endpoint=f"{self.urls.get('update_user_portfolio_rebalance')}/{user_portfolio_rebalance_id}/",
                         data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def update_portfolio_transaction(self, payload, portfolio_rebalance_transaction_id):
        """
        Updates the portfolio transaction with the provided payload.

        Parameters:
        - payload (str): JSON-formatted payload containing information to update the portfolio transaction.
        - portfolio_rebalance_transaction_id (str): The ID of the portfolio rebalance transaction to be updated.

        Returns:
        str: The updated data from the portfolio transaction.

        Note:
        This method sends a PUT request to the specified endpoint to update the portfolio transaction.
        """
        logger.info(f"In - update_portfolio_transaction {payload =}, {portfolio_rebalance_transaction_id =}")
        data = self._put(url=self.base_url,
                         endpoint=f"{self.urls.get('update_portfolio_transaction')}/{portfolio_rebalance_transaction_id}",
                         data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def complete_rebalance_transaction(self, portfolio_rebalance_transaction_id, status=None):
        """
        Marks a portfolio rebalance as complete based on the provided data.

        Parameters:
        - item (RebalanceComplete): An instance of the RebalanceComplete class containing relevant information.
        - request (Request): An instance of the Request class representing the incoming request.

        Returns:
        dict:
        """
        logger.info(f"In - update_portfolio_transaction, {portfolio_rebalance_transaction_id =}")
        payload = {}
        if status:
            payload = json.dumps({
                "status": status
            })
        data = self._put(url=self.base_url,
                         endpoint=f"{self.urls.get('complete_rebalance_transaction')}/{portfolio_rebalance_transaction_id}",
                         data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def get_portfolio_rebalances(self, user_portfolio_id, current_state):
        """
        Retrieve portfolio rebalances data.

        This method retrieves portfolio rebalances data for a specific user portfolio and current state.

        Args:
            user_portfolio_id (int): The ID of the user portfolio.
            current_state (list): The current state of the portfolio.

        Returns:
            dict: Portfolio rebalances data.
        """
        logger.info(f"In - update_portfolio_transaction, {user_portfolio_id =}, {current_state =}")
        params = {
            'current_state': ','.join(current_state)
        }
        data = self._get(url=self.base_url,
                         endpoint=f"{self.urls.get('get_portfolio_rebalances')}/{user_portfolio_id}",
                         params=params)
        logger.info(f"{data =}")
        return data.get("data")

    def create_basket(self, basket_payload):
        """
        Creates a new basket by sending a POST request with the provided basket payload.

        This method sends a POST request to create a basket using the specified `basket_payload`.
        The response is logged and the data is returned.

        Args:
            basket_payload (json()): A dictionary containing the details for creating a new basket.
                It should include all necessary fields to create the basket, such as user ID, model ID,
                basket type, product type, and other relevant data.

        Returns:
            dict: A dictionary containing the response data, including the created basket details.
                It returns the value of the 'data' field from the response.

        Logs:
            Logs the request payload and the response data for debugging and traceability.
        """
        logger.info(f"In create_basket {basket_payload =}")
        data = self._post(url=self.base_url,
                          endpoint=self.urls.get('create_basket'),
                          data=basket_payload)
        logger.info(f"{data =}")
        return data.get('data')

    def update_order_instructions(self, payload):
        """
        Sends order instructions by updating the order details through a PUT request.

        This method takes the given `payload`, updates the filled quantity, converts it to a JSON string,
        and sends it via a PUT request to update the order instructions. The response is logged and returned.

        Args:
            payload (dict): A dictionary containing the order details, including the symbol,
                quantity, and other relevant order information. The 'filled_quantity' field is automatically
                set to the value of 'quantity' in the payload.

        Returns:
            dict: A dictionary containing the response data, which includes the updated order instructions.
                It returns the value of the 'data' field from the response.

        Logs:
            Logs the request payload and the response data for debugging and traceability.
        """
        logger.info(f"In - user_instructions {payload =}")
        payload['filled_quantity'] = payload['quantity']
        payload = json.dumps(payload)
        data = self._put(url=self.base_url,
                         endpoint=self.urls.get("order_instructions"),
                         data=payload)
        logger.info(f"{data =}")
        return data.get("data")

    def create_basket_orders(self, basket_id, action: str):
        """
        Processes basket orders based on the specified action (retry or skip).

        Args:
            basket_id (int): The ID of the user's basket.
            action (str): The action to perform, either 'retry' or 'skip'.

        Returns:
            dict: The response data containing information about the processed orders.
        """
        logger.info(f"Processing basket orders for {basket_id =} with action '{action}'")
        endpoint = f"{self.urls.get(action)}/{basket_id}"
        data = self._post(url=self.base_url, endpoint=endpoint, data={})

        logger.info(f"Response data: {data =}")
        return data.get('data')

    def create_instructions(self, payload: str) -> list:
        """
        Sends a request to create order instructions based on the provided payload.

        Args:
            payload (str): The JSON string payload containing the instructions data.

        Returns:
            list: A list of newly created instructions data from the response.
        """
        logger.info(f"In create_instructions: {payload =}")

        endpoint = self.urls.get('create_order_instructions')
        response = self._post(
            url=self.base_url,
            endpoint=endpoint,
            data=payload)
        return response.get('data')

    def get_basket_details(self, user_id, current_state):
        """
        Fetches basket details for a given user based on the current state.

        Parameters:
            user_id (str): The user identifier.
            current_state (str): The current state of the basket (e.g., 'uninvested', 'invested').

        Returns:
            Optional[Dict]: The basket details if available, otherwise None.
        """
        logger.info(f"In basket_details {user_id =}, {current_state =}")
        endpoint = self.urls.get('basket_details')
        params = {
            'user_id': user_id,
            'current_state': current_state
        }
        response = self._get(url=self.base_url,
                             endpoint=endpoint,
                             params=params)

        return response.get('data')

    def get_broker_users_holdings(self, broker):
        logger.info(f"In broker_user_holdings {broker =}")
        endpoint = self.urls.get('broker_users_holdings').format(broker)
        response = self._get(url=self.base_url, endpoint=endpoint)
        return response.get('data')
