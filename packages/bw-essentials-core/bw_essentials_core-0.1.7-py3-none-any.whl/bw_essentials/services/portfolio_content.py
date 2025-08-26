"""portfolio_content.py

Client wrapper for the Portfolio-Content Service API.

This module exposes :class:`PortfolioContent`, a light-weight abstraction
around :class:`bw_essentials.services.api_client.ApiClient` that
centralises endpoint definitions and adds structured logging when
querying portfolio content (e.g. constituent list, metadata).

Example
-------
>>> from bw_essentials.services.portfolio_content import PortfolioContent
>>> client = PortfolioContent(service_user="system")
>>> details = client.get_portfolio_details("BASKE_e3f7fc")
>>> print(details)
"""

import logging
from typing import Optional, Dict, Any

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class PortfolioContent(ApiClient):
    """High-level client for the Portfolio-Content Service.

    Attributes
    ----------
    base_url : str
        Resolved base URL of the Portfolio-Content micro-service.
    name : str
        Canonical service identifier for logging/telemetry.
    urls : dict[str, str]
        Mapping of friendly names to relative endpoint paths.
    """

    def __init__(self, service_user: str):
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.PORTFOLIO_CONTENT.value)
        self.name = Services.PORTFOLIO_CONTENT.value
        self.urls = {
            "portfolio": "portfolio",
        }

    def get_portfolio_details(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details of a portfolio.

        Parameters
        ----------
        portfolio_id : str
            Unique identifier of the portfolio whose details should be
            fetched.

        Returns
        -------
        Optional[dict]
            Parsed JSON response if the request succeeds, otherwise
            ``None``.
        """
        logger.info("In - get_portfolio_details %s", portfolio_id)
        data = self._get(
            url=self.base_url,
            endpoint=f"{self.urls['portfolio']}/{portfolio_id}"
        )
        logger.info("%s", data)
        return data
