"""
Module to make structured API calls to the Master Data Service.

This module extends the generic ApiClient to provide typed, reusable
endpoints for accessing Master Data APIs like holidays, security details,
broker configurations, and constants.
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import pytz

from bw_essentials.constants.services import Services
from bw_essentials.services.api_client import ApiClient

logger = logging.getLogger(__name__)


class MasterData(ApiClient):
    """
    API wrapper for Master Data Service.

    Inherits from ApiClient and provides domain-specific methods to fetch
    holidays, constants, company details, and broker configurations.

    Args:
        service_user (str): The user initiating the request (e.g., system/username).
    """
    TEST = 'test'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'

    def __init__(self, service_user: str):
        logger.info(f"Initializing MasterData client for user: {service_user}")
        super().__init__(user=service_user)
        self.base_url = self.get_base_url(Services.MASTER_DATA.value)
        self.name = Services.MASTER_DATA.value
        self.urls = {
            "holidays": "holidays",
            "securities": "securities",
            "details": "company/details",
            "constant": "constants",
            "broker_config": "broker/config/keys",
            "broker_details": "securities/{}/details",
            "isin_details": "company/details/isin",
            "shorten_url": "shorten-url",
            "broker_partner_mapping_details": "partner/{}/broker/{}/"
        }

    def get_security_details(self, securities: List[str]) -> Optional[Dict[str, Any]]:
        """
        Fetches company security details by symbols.

        Args:
            securities (List[str]): List of security symbols.
        Returns:
            Optional[Dict[str, Any]]: Security detail data or None.
        """
        logger.info(f"Fetching security details for: {securities}")
        securities = ','.join(securities)
        response = self._get(url=self.base_url,
                             endpoint=self.urls["details"],
                             params={"symbols": securities})
        return response.get("data")

    def get_constants_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Fetches constants from master data using a key.

        Args:
            key (str): Constant key to query.

        Returns:
            Optional[Dict[str, Any]]: Constant values or None.
        """
        logger.info(f"Fetching constants data for key: {key}")
        response = self._get(url=self.base_url,
                             endpoint=self.urls["constant"],
                             params={"key": key})
        return response.get("data")

    def get_trading_holidays(self, year: int) -> Optional[List[Dict[str, Any]]]:
        """
        Gets trading holidays for a specific year.

        Args:
            year (int): Year for which holidays are to be fetched.
        Returns:
            Optional[List[Dict[str, Any]]]: List of holiday data.
        """
        logger.info(f"Fetching trading holidays for year: {year}")
        response = self._get(url=self.base_url,
                             endpoint=self.urls["holidays"],
                             params={"year": year})
        return response.get("data")

    def get_broker_config_keys(self, broker: str,
                               product_type: Optional[str] = None,
                               category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves broker configuration keys based on filters.

        Args:
            broker (str): Broker name.
            product_type (Optional[str]): Type of product (e.g., equity, MTF).
            category (Optional[str]): Optional configuration category.
        Returns:
            Optional[Dict[str, Any]]: Configuration key data or None.
        """
        logger.info(
            f"Fetching broker config keys for broker={broker}, product_type={product_type}, category={category}")
        params = {k: v for k, v in {'broker': broker, 'product': product_type, 'category': category}.items() if v}
        response = self._get(url=self.base_url,
                             endpoint=self.urls["broker_config"],
                             params=params)
        return response.get("data")

    def get_broker_security_details(self, securities: List[str], broker: str) -> Dict[str, Any]:
        """
        Retrieves broker-specific security details.

        Args:
            securities (List[str]): List of security symbols.
            broker (str): Broker name.

        Returns:
            Dict[str, Any]: Security detail data.
        """
        logger.info(f"Fetching broker security details for securities={securities}, broker={broker}")
        endpoint = self.urls["broker_details"].format(broker)
        params = {"symbols": securities}
        response = self._get(url=self.base_url,
                             endpoint=endpoint,
                             params=params)
        return response.get("data", {})

    def get_company_details(self, isin_data: List[str]) -> Dict[str, Any]:
        """
        Fetches company details using ISIN codes.

        Args:
            isin_data (List[str]): List of ISIN codes.

        Returns:
            Dict[str, Any]: Company detail data.
        """
        logger.info(f"Fetching company details for ISINs: {isin_data}")
        response = self._get(url=self.base_url,
                             endpoint=self.urls["isin_details"],
                             params={"isin": isin_data})
        return response.get("data", {})

    def get_active_securities(self) -> List[Dict[str, Any]]:
        """
        Retrieves all available active securities.

        Returns:
            List[Dict[str, Any]]: List of securities.
        """
        logger.info("Fetching list of all securities")
        response = self._get(url=self.base_url,
                             endpoint=self.urls["securities"])
        return response.get("data", [])

    def is_trading_hours(self, open_time: str, close_time: str, timezone: str) -> bool:
        """
        Determines if the current time is within the specified trading hours.

        Args:
            open_time (str): Trading start time in HH:MM format (e.g., "09:15").
            close_time (str): Trading end time in HH:MM format (e.g., "15:30").
            timezone (str): Timezone string (e.g., "Asia/Kolkata").

        Returns:
            bool: True if current time is within trading hours, False otherwise.
        """
        logger.info(f"In - is_trading_hours | open_time={open_time}, close_time={close_time}, timezone={timezone}")

        current_time = datetime.now(pytz.timezone(timezone))
        logger.info(f"Current time in {timezone} = {current_time}")

        open_time_obj = datetime.strptime(open_time, "%H:%M").time()
        close_time_obj = datetime.strptime(close_time, "%H:%M").time()

        if open_time_obj <= current_time.time() <= close_time_obj:
            logger.info("Market is open for trading.")
            return True

        logger.info("Market is closed for trading.")
        return False

    def is_trading_holiday(self, current_date: datetime.date) -> bool:
        """
        Determines whether the given date is a trading holiday or weekend.

        Args:
            current_date (datetime.date): The date to check for trading holiday.

        Returns:
            bool: True if it's a trading holiday or weekend, False otherwise.
        """
        logger.info("In - is_trading_holiday")
        logger.info(f"Get holidays list for year={current_date.year}")

        master_data_holidays = self.get_trading_holidays(current_date.year)
        logger.info(f"Fetched trading holidays: {master_data_holidays}")

        current_date_str = current_date.strftime('%Y-%m-%d')
        is_current_date_in_list = any(item['date'] == current_date_str for item in master_data_holidays)
        logger.info(f"Is current date in holiday list: {is_current_date_in_list}")

        is_current_day_weekend = current_date.strftime("%A") in [self.SATURDAY, self.SUNDAY]
        logger.info(f"Is current date a weekend: {is_current_day_weekend}")

        is_holiday = is_current_date_in_list or is_current_day_weekend
        logger.info(f"Final holiday check result: {is_holiday}")

        return is_holiday

    def is_market_open(self, domain: str, broker: str) -> bool:
        """
        Checks if the market is open based on the trading hours, holidays, and broker type.

        Args:
            domain (str): The domain name or identifier to fetch configuration data.
            broker (str): The broker identifier to determine if it's a test broker.

        Returns:
            bool: True if market is open, False otherwise.
        """
        logger.info(f"In - is_market_open | domain={domain}, broker={broker}")

        constants_data = self.get_constants_data(domain)
        logger.info(f"Retrieved constants data: {constants_data}")

        open_time = constants_data.get("market_hours", {}).get("start")
        close_time = constants_data.get("market_hours", {}).get("end")
        timezone = constants_data.get("timezone")
        brokers = constants_data.get("broker", {})
        broker_type = brokers.get(broker, {}).get('type')

        logger.info(f"Broker type for {broker}: {broker_type}")
        if broker_type == self.TEST:
            logger.info("Broker type is TEST. Market is considered open.")
            return True

        current_date = datetime.now().date()
        logger.info(f"Evaluating trading hours and holiday for date: {current_date}")

        is_open = self.is_trading_hours(open_time, close_time, timezone)
        is_holiday = self.is_trading_holiday(current_date)

        if is_open and not is_holiday:
            logger.info("Market is open based on hours and holiday check.")
            return True

        logger.info("Market is closed based on hours and/or holiday check.")
        return False

    def shorten_url(self, long_url: str) -> Dict[str, Any]:
        """Shorten a long URL using the configured URL-shortening service.

        Args:
            long_url (str): The long URL to shorten.

        Returns:
            dict: A dictionary containing the shortened URL or any error data.

        Logs:
            Information about the long_url being shortened.

        """
        logger.info(f"Shortening URL: {long_url}")
        response = self._post(url=self.base_url,
                              endpoint=self.urls["shorten_url"],
                              data={"long_url": long_url})
        logger.info(f"Shortening URL {response =}")
        return response.get("data", {})

    def get_or_create_broker_partner_mapping(self, broker_partner: str, broker: str) -> Dict[str, Any]:
        """
        Fetches or creates a broker-partner mapping from master data constants table.

        This method sends a GET request to retrieve the mapping details for a given
        broker and broker partner. If the mapping does not exist, the API
        is expected to create it automatically (based on implementation).

        Parameters:
        - broker_partner (str): The identifier of the broker partner.
        - broker (str): The identifier of the broker.

        Returns:
        - Dict[str, Any]: The mapping data returned from the service, or an empty
          dictionary if no data is available.
        """
        logger.info(f"In - get_or_create_broker_partner_mapping | broker_partner={broker_partner} broker={broker}")
        response = self._get(url=self.base_url, endpoint=self.urls["broker_partner_mapping_details"].format(broker_partner, broker))
        logger.info(f"Broker partner mapping {response =}")
        return response.get('data', {})
