"""
Generic API client module for making external HTTP requests with structured logging and tracing.

This wrapper provides reusable methods to send GET, POST, and PUT requests with consistent headers,
request tracing via `x-request-id`, and tenant context for multitenant systems.

It logs key information such as:
- Service and endpoint URLs
- Request headers and payloads
- Response status and body
- Request duration in milliseconds
- Exceptions, if any
"""
import logging
import os
import sys
import time
from importlib.util import spec_from_file_location, module_from_spec
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class ApiClient:
    """
    A reusable API client for external service calls with contextual logging and tracing support.

    Args:
        user (str): The user or system initiating the request.
    """
    SERVICE_NAME = 'Bw-Essentials'

    def __init__(self, user: str):
        logger.info(f"Initializing ApiClient with user={user}")
        self.name = self.SERVICE_NAME
        self.user = user
        self.headers = {}
        self._update_headers()
        logger.info("ApiClient initialized")

    def _get_env_var(self, key: str) -> str:
        """
        Fetch a required variable from bw_config.py located in the root directory.

        Raises:
            FileNotFoundError: If bw_config.py is not found.
            AttributeError: If the requested key is not defined in the config.

        Returns:
            str: The value of the config variable.
        """
        config_path = os.path.join(os.getcwd(), "bw_config.py")

        if not os.path.exists(config_path):
            raise FileNotFoundError("`bw_config.py` file not found in the root directory. "
                                    "Please ensure the config file exists.")

        spec = spec_from_file_location("bw_config", config_path)
        bw_config = module_from_spec(spec)
        sys.modules["bw_config"] = bw_config
        spec.loader.exec_module(bw_config)

        if not hasattr(bw_config, key):
            raise AttributeError(f"`{key}` not found in bw_config.py. Please define it in the config.")

        return getattr(bw_config, key)

    def get_base_url(self, service_name: str) -> str:
        """
        Resolve the base URL for a given service name using environment variables.

        Args:
            service_name (str): The logical name of the service.

        Returns:
            str: The resolved base URL from the environment.
        """
        env_key = f"{service_name.upper()}_BASE_URL"
        return self._get_env_var(env_key)

    def set_tenant_id(self, tenant_id: str) -> None:
        """
        Set the tenant ID in the request headers.

        Args:
            tenant_id (str): The tenant identifier to include in the headers.
        """
        logger.info(f"Setting tenant ID: {tenant_id}")
        self._update_headers({"X-Tenant-ID": tenant_id})
        logger.info(f"Updated headers: {self.headers}")

    def set_headers(self, headers: dict) -> None:
        """
        Merge provided headers into the client's request headers.

        Args:
            headers (dict): Dictionary of headers to add or update.
        """
        logger.info(f"Updating headers with: {headers}")
        self._update_headers(headers)
        logger.info(f"Headers after update: {self.headers}")

    def _update_headers(self, new_headers: dict = None) -> None:
        """
        Update the client's headers with new entries and tracing information.
        """
        new_headers = new_headers or {}

        try:
            from asgi_correlation_id import correlation_id
            request_id = correlation_id.get()
        except ImportError:
            request_id = None

        if not request_id:
            try:
                from log_request_id import local
                request_id = getattr(local, 'request_id', None)
            except ImportError:
                request_id = None

        if request_id:
            new_headers["x-request-id"] = request_id
            logger.info(f"Using request ID: {request_id}")
        else:
            logger.info("No request ID found to add to headers")

        self.headers.update(new_headers)

    def _log_response(self, method: str, url: str, status_code: int, elapsed_time_ms: float, response_body: Any):
        logger.info(
            f"{method.upper()} {url} | Status: {status_code} | Time: {elapsed_time_ms:.2f}ms "
            f"| Response: {response_body}"
        )

    def _request(self, method: str, url: str, endpoint: str, **kwargs) -> Any:
        """
        Generic method to send HTTP requests and log key metrics.

        Args:
            method (str): HTTP method - GET, POST, PUT, etc.
            url (str): Base service URL.
            endpoint (str): API endpoint path.
            kwargs: Additional keyword arguments for `requests.request`.

        Returns:
            Any: Parsed JSON response.

        Raises:
            Exception: If request fails or response is not valid.
        """
        formatted_url = f"{url.rstrip('/')}/{endpoint.lstrip('/')}"
        logger.info(f"{method.upper()} {formatted_url} | Headers: {self.headers} | Params: {kwargs.get('params')}")

        start = time.time()
        try:
            response = requests.request(method, formatted_url, headers=self.headers, **kwargs)
            elapsed_time_ms = (time.time() - start) * 1000
            json_data = response.json()
            self._log_response(method, formatted_url, response.status_code, elapsed_time_ms, json_data)
            response.raise_for_status()
            return json_data
        except Exception as exc:
            elapsed_time_ms = (time.time() - start) * 1000
            logger.error(f"{method.upper()} {formatted_url} failed after {elapsed_time_ms:.2f}ms")
            logger.exception(exc)
            raise

    def _get(self, url: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Send a GET request to the given endpoint.

        Args:
            url (str): Base URL.
            endpoint (str): API path.
            params (Optional[Dict[str, Any]]): Query parameters.

        Returns:
            Any: JSON response.
        """
        return self._request("get", url, endpoint, params=params)

    def _post(
        self,
        url: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a POST request to the given endpoint.

        Args:
            url (str): Base URL.
            endpoint (str): API path.
            data (Optional[Dict[str, Any]]): Form-encoded body.
            json (Optional[Dict[str, Any]]): JSON body.
            params (Optional[Dict[str, Any]]): Query parameters.

        Returns:
            Any: JSON response.
        """
        return self._request("post", url, endpoint, data=data, json=json, params=params)

    def _put(
        self,
        url: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Send a PUT request to the given endpoint.

        Args:
            url (str): Base URL.
            endpoint (str): API path.
            data (Optional[Dict[str, Any]]): Form-encoded body.
            json (Optional[Dict[str, Any]]): JSON body.
            params (Optional[Dict[str, Any]]): Query parameters.

        Returns:
            Any: JSON response.
        """
        return self._request("put", url, endpoint, data=data, json=json, params=params)
