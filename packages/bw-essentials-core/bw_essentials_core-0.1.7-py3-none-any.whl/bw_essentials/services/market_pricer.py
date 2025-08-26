"""
market_pricer.py

This module provides a `MarketPricer` client class to interact with the Market Pricer service APIs.

It supports retrieval of:
- Live market prices for specified securities on a given exchange.
- End-of-day (EOD) prices for individual or multiple securities on a given date.

The `MarketPricer` class extends `ApiClient` from `bw_essentials` and utilizes its built-in
HTTP communication methods to interact with the external service.

Typical use cases include fetching live or historical prices for dashboards, analytics, or
backtesting systems.

Example:
    market_pricer = MarketPricer(
        service_user="system"
    )

    live_prices = market_pricer.get_live_prices(securities="TCS,RELIANCE", exchange="NSE")
    eod_price = market_pricer.get_eod_prices(ticker="TCS", date="2023-10-03")
    bulk_prices = market_pricer.get_bulk_eod_prices(tickers=["TCS", "RELIANCE"], date="2023-10-03")
"""

import logging

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class MarketPricer(ApiClient):
    """
    This class represents a MarketPricer, which is used to retrieve live and end-of-day (EOD) market prices for
    securities.

    Attributes:
        name (str): The name of the MarketPricer instance.
        urls (dict): A dictionary containing the endpoint URLs for live and EOD prices.

    Methods:
        __init__(self, user):
            Initializes a new MarketPricer instance.

            Args:
                user (User): The user object representing the authenticated user.

        get_live_prices(self, securities, exchange):
            Retrieves live market prices for a list of securities on a specific exchange.

            Returns:
                list: A list of live market price data for the specified securities.

            Example:
                market_pricer = MarketPricer(user)
                securities = "TCS,RELIANCE"
                exchange = "NSE"
                live_prices = market_pricer.get_live_prices(securities, exchange)
    """

    def __init__(self, service_user: str):
        logger.info(f"Initializing MarketPricer client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.MARKET_PRICER.value)
        self.name = Services.MARKET_PRICER.value
        self.urls = {
            "live": "live",
            "eod": "eod",
            "index_performance": "index/{}/performance",
        }

    def get_live_prices(self, securities, exchange):
        """
        Retrieves live market prices for a list of securities on a specific exchange.

        Args:
            securities (str): A list of security symbols for which live prices are requested.
            exchange (str): The exchange on which the securities are traded.
        Returns:
            list: A list of live market price data for the specified securities.

        Example:
            market_pricer = MarketPricer(user)
            securities = "TCS,RELIANCE"
            exchange = "NSE"
            live_prices = market_pricer.get_live_prices(securities, exchange)

        API Endpoint:
            GET /pricing/live_prices

        API Parameters:
            - symbols (str): Comma-separated list of security symbols.
            - exchange (str): The exchange on which the securities are traded.

        API Response:
            {
                "data": [
                    {
                        "symbol": "TCS",
                        "price": 150.25,
                        "timestamp": "2023-10-04T10:30:00Z",
                        "exchange": "NSE"
                    },
                    {
                        "symbol": "RELIANCE",
                        "price": 2750.75,
                        "timestamp": "2023-10-04T10:30:00Z",
                        "exchange": "NSE"
                    }
                ]
            }
        """
        logger.info(f"In - get_live_prices {securities =}, {exchange =}")
        securities = ','.join(securities)
        market_pricing_live_response = self._get(url=self.base_url,
                                                 endpoint=self.urls.get("live"),
                                                 params={"symbols": securities,
                                                         "exchange": exchange})

        logger.info(f"{market_pricing_live_response =}")
        return market_pricing_live_response.get("data")

    def get_eod_prices(self, ticker, date):
        """
        Retrieves end-of-day (EOD) market prices for a specific security on a given date.

        Args:
            ticker (str): The symbol or identifier of the security for which EOD prices are requested.
            date (str): The date for which EOD prices are requested in the format 'YYYY-MM-DD'.
        Returns:
            dict: A dictionary containing the EOD market price data for the specified security on the given date.

        Example:
            market_pricer = MarketPricer(user)
            security_ticker = "TCS"
            eod_date = "2023-10-03"
            eod_prices = market_pricer.get_eod_prices(security_ticker, eod_date)

        API Endpoint:
            GET /pricing/eod_prices

        API Parameters:
            - ticker (str): The symbol or identifier of the security.
            - date (str): The date for which EOD prices are requested in the format 'YYYY-MM-DD'.

        API Response:
            {
                "data": {
                    "symbol": "TCS",
                    "date": "2023-10-03",
                    "open_price": 148.5,
                    "close_price": 150.25,
                    "high_price": 151.0,
                    "low_price": 147.75,
                    "volume": 5000000,
                    "ri": 12
                }
            }
        """
        logger.info(f"In - get_eod_prices {ticker =}, {date =}")
        market_pricing_eod_response = self._get(url=self.base_url,
                                                endpoint=self.urls.get("eod"),
                                                params={"ticker": ticker,
                                                        "date": date})
        logger.info(f"{market_pricing_eod_response =}")
        return market_pricing_eod_response.get("data")

    def get_bulk_eod_prices(self, tickers, date):
        """
        Retrieves end-of-day (EOD) market prices for multiple securities on a given date.

        Args:
            tickers (list or str): List of ticker symbols or comma-separated string of
                ticker symbols.
            date (str): The date for which EOD prices are requested in the format
                'YYYY-MM-DD'.
        Returns:
            list: A list of dictionaries containing the EOD market price data for each
                security.

        Example:
            market_pricer = MarketPricer(user)
            security_tickers = ["TCS", "RELIANCE"] # or "TCS,RELIANCE"
            eod_date = "2023-10-03"
            eod_prices = market_pricer.get_bulk_eod_prices(security_tickers, eod_date)

        API Endpoint:
            GET /pricing/bulk-eod

        API Parameters:
            - tickers (str): Comma-separated list of ticker symbols.
            - date (str): The date for which EOD prices are requested in the format
                'YYYY-MM-DD'.

        API Response:
            {
                "data": [
                    {
                        "symbol": "TCS",
                        "date": "2023-10-03",
                        "open_price": 148.5,
                        "close_price": 150.25,
                        "high_price": 151.0,
                        "low_price": 147.75,
                        "volume": 5000000,
                        "ri": 12
                    },
                    {
                        "symbol": "RELIANCE",
                        "date": "2023-10-03",
                        "open_price": 2740.0,
                        "close_price": 2750.75,
                        "high_price": 2755.0,
                        "low_price": 2735.0,
                        "volume": 3000000,
                        "ri": 15
                    }
                ]
            }
        """
        logger.info(f"In - get_bulk_eod_prices {tickers=}, {date=}")
        if isinstance(tickers, list):
            tickers = ",".join(tickers)

        market_pricing_eod_response = self._get(
            url=self.base_url,
            endpoint="bulk-eod",
            params={"tickers": tickers, "date": date}
        )

        logger.info(f"{market_pricing_eod_response=}")
        return market_pricing_eod_response.get("data")

    def get_index_performance_by_dates(self, index_name, start_date, end_date):
        """
        Fetches index performance metrics over a given date range.

        Args:
            index_name (str): The index name (e.g., "NIFTY50").
            start_date (str): The start date for performance metrics in 'YYYY-MM-DD' format.
            end_date (str): The end date for performance metrics in 'YYYY-MM-DD' format.

        Returns:
            dict: A dictionary containing cumulative return, volatility, drawdown, and a list
                  of daily return data.
                  Example:
                    {
                      "data": {
                        "cumulative_return": 2.332968692796598,
                        "volatility": 6.378354401960588,
                        "drawdown": 0,
                        "daily_returns": [
                          {
                            "date": "2025-06-05",
                            "close": 22934.5,
                            "daily_return": 0.5552912703301827,
                            "current_weight": 100.55529127033019
                          },
                          {
                            "date": "2025-06-06",
                            "close": 23165.1,
                            "daily_return": 1.0054721053434745,
                            "current_weight": 101.56634667450024
                          },
                          {
                            "date": "2025-06-09",
                            "close": 23329.4,
                            "daily_return": 0.7092565972087517,
                            "current_weight": 102.28671268883305
                          },
                          {
                            "date": "2025-06-10",
                            "close": 23339.95,
                            "daily_return": 0.04522190883606836,
                            "current_weight": 102.3329686927966
                          }
                        ]
                      },
                      "success": true
                    }
        Raises:
            ValueError: If input parameters are missing or invalid.
        """
        logger.info(f"In - get_index_performance_by_dates | {index_name=}, {start_date=}, {end_date=}")

        if not all([index_name, start_date, end_date]):
            logger.error("Missing required parameters for index performance fetch")
            raise ValueError("index_name, start_date, and end_date are required")

        endpoint = self.urls['index_performance'].format(index_name)
        params = {"start_date": start_date, "end_date": end_date}
        response = self._get(
            url=self.base_url,
            endpoint=endpoint,
            params=params
        )
        logger.debug(f"Raw response from MarketPricer index API: {response}")
        data = response.get("data")
        logger.info("Out - get_index_performance_by_dates success")
        return data
