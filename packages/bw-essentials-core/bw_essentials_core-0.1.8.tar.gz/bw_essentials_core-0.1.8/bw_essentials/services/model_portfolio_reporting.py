"""
Module: model_portfolio_reporting.py

Provides a client for interacting with the Model Portfolio microservice.
Inherits from the reusable ApiClient to enable consistent request handling,
header management, tracing, and logging for service-to-service communication.
"""

import logging
from typing import Optional, Any, Dict

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class ModelPortfolioReporting(ApiClient):
    """
    API client for the Model Portfolio Reporting microservice.

    This class provides methods to interact with portfolio rebalance and
    performance endpoints. It uses the shared ApiClient base for consistent
    HTTP request handling, correlation ID injection, and logging.

    Args:
        service_user (str): Name of the system or user initiating the requests.
    """

    def __init__(self, service_user: str):
        logger.info(f"Initializing ModelPortfolioReporting client for user: {service_user}")
        super().__init__(user=service_user)
        self.object = None
        self.urls = {
            "portfolio": "portfolio",
            "portfolio_performance": "portfolio/%s/performance"
        }
        self.name = Services.MODEL_PORTFOLIO.value
        self.base_url = self.get_base_url(Services.MODEL_PORTFOLIO.value)
        logger.info(f"ModelPortfolioReporting initialized with base_url: {self.base_url}")

    def get_active_rebalance(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the active rebalance data for a given portfolio ID.

        Args:
            portfolio_id (str): The unique identifier of the portfolio.

        Returns:
            dict | None: The rebalance data if found, else None.
        """
        logger.info(f"In - get_active_rebalance with portfolio_id={portfolio_id}")
        data = self._get(
            url=self.base_url,
            endpoint=f"{self.urls['portfolio']}/{portfolio_id}/rebalance/active/"
        )
        logger.info(f"Received response from get_active_rebalance: {data}")
        return data.get("data")

    def get_portfolio_performance_by_dates(self, portfolio_id: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        Fetch portfolio performance for a given date range.

        Args:
            portfolio_id (str): The portfolio identifier.
            start_date (str): The start date for performance metrics (format: YYYY-MM-DD).
            end_date (str): The end date for performance metrics (format: YYYY-MM-DD).

        Returns:
            dict | None: The performance data within the date range.
        """
        logger.info(f"In - get_portfolio_performance_by_dates with portfolio_id={portfolio_id}, start_date={start_date}, end_date={end_date}")
        endpoint = self.urls['portfolio_performance'] % portfolio_id
        params = {"start_date": start_date, "end_date": end_date}
        performance = self._get(
            url=self.base_url,
            endpoint=endpoint,
            params=params
        )
        logger.info(f"Received response from get_portfolio_performance_by_dates: {performance}")
        return performance.get("data")
