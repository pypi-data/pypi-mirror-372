import logging
import time
from typing import Any
from typing import Dict
from urllib.parse import urljoin

from pypply.utils import ENVS
import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout

logger = logging.getLogger(__name__)


class API:
    """Creates an Upply API object."""

    API_URLS = {
        "prod": "https://api.upply.com/v1/",
        "sandbox": "https://api.sandbox.upply.com/v1/",
    }

    def __init__(
        self,
        access_token: str,
        env: str,
        product: str,
        timeout: int = 5,
        sleep_time: float = 0.2,
        retries: int = 0,
    ):
        """Initializes an API object with authentication and request settings.

        Args:
            access_token (str): Authentication token required to access the API.
            env (str): API environment. Allowed values: prod, sandbox.
            product (str): API product. Allowed values: smart, geography.
            timeout (int): Maximum time (in seconds) to wait for a response.
            sleep_time (float): Delay (in seconds) between retry attempts.
            retries (int): Number of retry attempts in case of a failed request.
        """
        if env not in ENVS:
            raise ValueError(
                f"env: expected value from {', '.join(ENVS)} but got {env}"
            )
        self.access_token = "Bearer " + access_token
        self._session = requests.Session()
        self._session.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": self.access_token,
        }
        self.url = urljoin(self.API_URLS[env], product + "/")
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.retries = retries

    def __del__(self):
        """Closes session when the object is destroyed"""
        if hasattr(self, "_session"):
            self._session.close()

    def _make_request(
        self, endpoint: str, method: str = "POST", **kwargs
    ) -> Dict[str, Any]:
        """Makes a request to Upply's API.

        Args:
            endpoint (str): Endpoint URL.
            method (str): Request type. Allowed values: POST, GET.

        Returns:
            Dict[str, Any]: Result of the request.
        """
        url = urljoin(self.url, endpoint)
        response = None
        tries = 0
        while response is None and tries <= self.retries:
            tries += 1
            response = self._session.request(method=method, url=url, **kwargs)
            try:
                response.raise_for_status()
            except HTTPError as http_err:
                try:
                    error_details = response.json()
                except ValueError:
                    error_details = response.text
                if http_err.response.status_code < 500 or tries > self.retries:
                    logger.error(
                        f"HTTP error on try {tries}: {http_err}. Details:"
                        f" {error_details}"
                    )
                    raise HTTPError(
                        f"{http_err}. Response error details: {error_details}"
                    ) from None
            except ConnectionError as conn_err:
                logger.error(f"Connection error on try {tries}: {conn_err}")
            except Timeout as timeout_err:
                logger.error(f"Timeout error on try {tries}: {timeout_err}")
            except Exception as err:
                logger.error(f"Unexpected error on try {tries}: {err}")
                raise err
            time.sleep(self.sleep_time)

        if response:
            try:
                return response.json()
            except ValueError:
                raise ValueError("Failed to decode JSON response")
