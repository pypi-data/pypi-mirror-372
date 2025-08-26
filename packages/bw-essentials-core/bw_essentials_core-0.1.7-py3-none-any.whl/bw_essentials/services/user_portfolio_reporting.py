"""
Module to interact with the User Reporting service.

This module provides a Python client interface for making API calls to the User Reporting
microservice. It supports operations such as:

- Submitting user instructions (buy/sell orders) for portfolios
- Retrieving overall portfolio performance metrics
- Retrieving a detailed breakdown of portfolio performance

The `UserReporting` class inherits from a generic `ApiClient` and uses shared service
constants from `bw_essentials`. It is initialized with user-level and request-level
payloads and handle responses from the service.

Typical use cases include:
- Sending trade execution data from the frontend/backend to the reporting service
- Fetching user portfolio performance data for dashboards or reports

Dependencies:
- bw_essentials.constants.services.Services
- bw_essentials.services.api_client.ApiClient

Example usage:
    reporting_client = UserReporting(
        service_user="portfolio_service"
    )

    # Submit instructions
    reporting_client.add_instructions(request_data)

    # Fetch performance
    performance = reporting_client.get_portfolio_performance(user_id, portfolio_id)

    # Fetch breakdown
    breakdown = reporting_client.get_portfolio_performance_breakdown(user_id, portfolio_id)
"""

import json
import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class UserReporting(ApiClient):
    SELL = 'sell'
    BUY = 'buy'
    MTF = 'mtf'
    INTRADAY = 'intraday'
    EQUITY = 'equity'

    def __init__(self,
                 service_user: str):
        """
        Initializes the UserReporting client with user, base URL, request ID, tenant ID..

        :param service_user: Service name or username initiating the request
        """
        logger.info(f"Initializing UserReporting client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.USER_REPORTING.value)
        self.name = Services.USER_REPORTING.value
        self.urls = {
            "instructions": "reporting/instructions/",
            "portfolio_performance": "reporting/user/%s/userportfolio/%s/performance/",
            "portfolio_performance_breakdown": "reporting/user/%s/userportfolio/%s/performance/breakdown/",
            'portfolio_stock_performance': "reporting/user/%s/userportfolio/%s/stock/performance/"
        }

    def _get_integer_quantity(self, qty, side):
        """
        Returns quantity as a negative value if side is 'sell', otherwise returns it as-is.

        :param qty: Quantity of the asset
        :param side: Trade side, either 'buy' or 'sell'
        :return: Signed quantity based on trade side
        """
        quantity = -1 * qty if side == self.SELL else qty
        return quantity

    def _build_instructions_data(self, request_data):
        """
        Builds the payload for submitting trade instructions.

        :param request_data: Request payload containing metadata and trade details
        :return: Formatted instruction payload as a dictionary
        """
        meta_data = request_data.get('metadata')
        product_type = request_data.get('product_type')
        instructions = {
            "user_id": meta_data.get("user_id"),
            "user_portfolio_id": meta_data.get("basket_id") if product_type == self.MTF
            else meta_data.get('user_portfolio_id'),
            "instruction_id": meta_data.get("instruction_id"),
            "symbol": request_data.get("symbol"),
            "qty": self._get_integer_quantity(qty=request_data.get("quantity"),
                                              side=request_data.get("side")),
            "execution_price": request_data.get("price"),
            "date": meta_data.get("date"),
            "product": product_type if product_type == self.MTF else self.EQUITY
        }
        instruction_data = {
            "instructions": [
                instructions
            ]
        }
        return instruction_data

    def add_instructions(self, request_data):
        """
        Sends trade instructions to the User Reporting service.

        :param request_data: Request payload containing instruction metadata and trade details
        """
        logger.info(f"In - add_instructions {request_data =}")
        instruction_data = self._build_instructions_data(request_data)
        user_instructions_response = self._post(url=self.base_url,
                                                endpoint=self.urls.get("instructions"),
                                                data=json.dumps(instruction_data))
        logger.info(f"{user_instructions_response =}")

    def get_portfolio_performance(self, user_id, user_portfolio_id, product='equity'):
        """
        Retrieves portfolio performance data for a specific user and portfolio.

        :param user_id: ID of the user
        :param user_portfolio_id: ID of the user portfolio
        :param product: Product type (default: 'equity')
        :return: Performance data from the response
        """
        endpoint = self.urls.get('portfolio_performance') % (user_id, user_portfolio_id)
        data = self._get(url=self.base_url,
                         endpoint=endpoint,
                         params={
                             "product": product
                         })
        logger.info(f"{data =}")
        return data.get("data")

    def get_portfolio_performance_breakdown(self, user_id, user_portfolio_id):
        """
        Retrieves a detailed breakdown of portfolio performance for a specific user and portfolio.

        :param user_id: ID of the user
        :param user_portfolio_id: ID of the user portfolio
        :return: Performance breakdown data from the response
        """
        endpoint = self.urls.get('portfolio_performance') % (user_id, user_portfolio_id)
        data = self._get(url=self.base_url,
                         endpoint=endpoint)
        logger.info(f"{data =}")
        return data.get("data")

    def get_portfolio_stock_performance(self, user_id, user_portfolio_id):
        """
        Retrieves a detailed breakdown of portfolio pnl

        :param user_id: ID of the user
        :param user_portfolio_id: ID of the user portfolio
        :return: Performance breakdown data from the response
        """
        logger.info(f"In get_portfolio_stock_performance {user_id=}, {user_portfolio_id=}")
        endpoint = self.urls.get('portfolio_stock_performance') % (
            user_id, user_portfolio_id)
        data = self._get(url=self.base_url,
                         endpoint=endpoint)
        logger.info(f"{data=}")
        return data.get("data")
