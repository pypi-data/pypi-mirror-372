from typing import Union
from urllib.parse import urlencode

from .api import API
from .utils import GEO_ENDPOINT
from .utils import LOCATION_TYPES


class Geography(API):
    """Creates a Geography object to request geography endpoint."""

    def __init__(
        self,
        access_token: str,
        env: str = "prod",
        timeout: int = 5,
        sleep_time: float = 0.2,
        retries: int = 0,
    ):
        """Initializes a Geography object with authentication and request settings.

        Args:
            access_token (str): Authentication token required to access the API.
            env (str): API environment. Allowed values: prod, sandbox.
            timeout (int): Maximum time (in seconds) to wait for a response.
            sleep_time (float): Delay (in seconds) between retry attempts.
            retries (int): Number of retry attempts in case of a failed request.
        """
        super().__init__(
            access_token=access_token,
            env=env,
            product="geography",
            timeout=timeout,
            sleep_time=sleep_time,
            retries=retries,
        )

    def get_lat_long(
        self, query: str, location_type: str, country_code: str
    ) -> dict[str, Union[float, int]]:
        """Retrieves the latitude and longitude for a given location (city, airport, or seaport).

        Args:
            query (str): Search string.
            location_type (str): Location type. Allowed values: city, airport, seaport.
            country_code (str): Country code ISO Alpha 2.

        Returns:
            dict[str, Union[float, int]]: Dictionary corresponding to latitude and longitude.
        """
        # --- Validate input parameters ---
        if location_type not in LOCATION_TYPES:
            raise ValueError(
                "location_type: expected value from"
                f" {', '.join(LOCATION_TYPES)} but got {location_type}"
            )
        if not query.strip():
            raise ValueError("query parameter is required and cannot be empty")

        # --- Build the request URL ---
        params = {
            "query": query,
            "type": location_type,
            "countryCode": country_code,
        }
        endpoint_request = GEO_ENDPOINT + "?" + urlencode(params)

        # --- Execute the API request ---
        res = self._make_request(endpoint=endpoint_request, method="GET")

        # --- Process and return the response data ---
        data = res.get("data")
        if data:
            lat_long = {
                k: v
                for k, v in res["data"].items()
                if k in ["latitude", "longitude"]
            }
            return lat_long
        else:
            raise ValueError(
                f"No result found for query = {query}, location_type ="
                f" {location_type} and country_code = {country_code}"
            )
