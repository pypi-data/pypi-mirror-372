from datetime import datetime
import itertools
import logging
from typing import Any
from typing import Iterator
from typing import Type
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urljoin

from dateutil.relativedelta import relativedelta
from pydantic import ValidationError

from .api import API
from .mode_types.air import PayloadAir
from .mode_types.road_emea import PayloadRoademea
from .mode_types.road_na import PayloadRoadna
from .mode_types.sea_longterm import PayloadSeaLongterm
from .utils import ALL_DEFAULT_PAYLOADS
from .utils import BENCHMARK_ENDPOINT
from .utils import DATE_DEBUT
from .utils import DATE_TODAY_STR
from .utils import EMISSION_TYPES
from .utils import generate_weekly_dates
from .utils import GEO_KEYS
from .utils import HISTORICAL_TYPES
from .utils import LABEL_KEYS
from .utils import LAT_LON_KEYS
from .utils import MODES
from .utils import process_rate_range
from .utils import SMART_PRODUCTS
from .utils import UFI_ENDPOINT
from .utils import UFI_FORECAST_ENDPOINT
from .utils import UFI_HISTORICAL_ENDPOINT
from .utils import UFI_LANGUAGES
from .utils import UFI_MARKETS
from .utils import UFI_NB_WEEKS_MAX

# --- Configure logging ---
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def _check_structure(expected: dict, payload: dict, path: str = "") -> None:
    """Checks recursively that payload has the same keys as expected.

    Args:
        expected (dict): Expected payload.
        payload (dict): Client payload.
        path (str): Key path to print if error.
    """
    for key, value in payload.items():
        # Construct the full key path for error messages
        current_path = f"{path}.{key}" if path else key
        # Check if the key exists in the expected structure
        if key not in expected:
            raise ValueError(f"Expected key in the payload : '{current_path}'")
        # If the expected value is a dictionary, then the payload value must also be a dictionary
        if isinstance(expected[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f"'{current_path}' must be a dictionary")
            # Recursively check the structure for the nested dictionary
            _check_structure(expected[key], value, current_path)


def _check_value_in_set(
    feature: str, value: str, correct_set: Union[list, dict]
) -> None:
    """Raises a ValueError if value is not in the correct set.

    Args:
        feature (str): Feature that is checked.
        value (str): Value of the feature that is checked.
        correct_set (Union[list, dict]): Set of correct values.
    """
    if value and (value not in correct_set):
        raise ValueError(
            f"{feature}: expected value from {', '.join(correct_set)} but got"
            f" {value}"
        )


def _check_payload_structure(mode: str, payload: dict) -> None:
    """Checks that the payload has the mode expected payload structure (payload can be incomplete).

    Args:
        mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
        payload (dict): Benchmark payload.
    """
    # --- Validate that the provided mode is valid ---
    _check_value_in_set(feature="mode", value=mode, correct_set=MODES)

    # --- Exclude pickup and delivery from the payload before structure check ---
    payload_to_check = {
        k: v for k, v in payload.items() if k not in ["pickup", "delivery"]
    }
    expected_payload = ALL_DEFAULT_PAYLOADS[mode]

    # --- Check the structure recursively ---
    _check_structure(expected=expected_payload, payload=payload_to_check)


def _check_complete_payload(mode: str, payload: dict) -> None:
    """Checks if the payload has the expected mode payload structure and right values / types.

    Args:
        mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
        payload (dict): Benchmark payload.
    """
    # --- Validate that the provided mode is valid ---
    _check_value_in_set(feature="mode", value=mode, correct_set=MODES)

    # --- Map mode to its corresponding Pydantic schema ---
    mode_to_schema: dict[str, Type] = {
        "air": PayloadAir,
        "road_emea": PayloadRoademea,
        "road_na": PayloadRoadna,
        "sea_longterm": PayloadSeaLongterm,
    }
    schema = mode_to_schema[mode]

    # --- Validate the payload using the Pydantic model ---
    schema(**payload)


def _deep_merge_dicts(
    dict1: dict[str, Any], dict2: dict[str, Any]
) -> dict[str, Any]:
    """Merges two dictionaries recursively, giving priority to dict2 values over dict1 ones.

    Args:
        dict1 (dict[str, Any]): Base dictionary.
        dict2 (dict[str, Any]): Priority dictionary.

    Returns:
        dict[str, Any]: Merged dictionary.
    """
    # --- Create a copy of dict1 to avoid modifying the original ---
    merged = dict1.copy()

    # --- Iterate over each key in dict2 and merge recursively if both values are dictionaries ---
    for key, value in dict2.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = value

    return merged


def _check_pickup_delivery(payload: dict[str, Any]):
    """Checks pickup and delivery formats in payload.

    Args:
        payload (dict[str, Any]): Benchmark payload.
    """
    # --- Check that payload contains required keys and that they are dictionaries ---
    if any(
        ((key not in payload) or (type(payload[key]) != dict))
        for key in GEO_KEYS
    ):
        raise ValueError(
            "payload must contains following dictionaries:"
            f" {', '.join(GEO_KEYS)}"
        )

    # --- Check that the keys in pickup/delivery match one of the allowed formats ---
    correct_formats = [set(LAT_LON_KEYS), set(LABEL_KEYS)]
    if any(payload[key].keys() not in correct_formats for key in GEO_KEYS):
        raise ValueError(
            f"{', '.join(GEO_KEYS)} must be dictionaries with either"
            f" {', '.join(LAT_LON_KEYS)} keys or {', '.join(LABEL_KEYS)} keys"
        )


def _process_payload(mode: str, payload_client: dict) -> dict[str, Any]:
    """Merges payload with default payload and checks if the payload has the expected mode payload structure.

    First, checks pickup and delivery formats.
    Second, checks that payload_client matches with mode typical payload.
    Then, merges payload_client with default payload to manage case when payload_client is incomplete.
    Finally, checks that the merged payload has the right structure, types and values.

    Args:
        mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
        payload_client (dict): Benchmark payload.

    Returns:
        dict[str, Any]: Dictionary corresponding to processed payload.
    """
    # --- Validate that the provided mode is valid ---
    _check_value_in_set(feature="mode", value=mode, correct_set=MODES)

    # --- Process pickup and delivery sections ---
    _check_pickup_delivery(payload=payload_client)

    # --- Validate that the client payload (excluding geo sections) matches the expected structure ---
    try:
        _check_payload_structure(mode, payload_client)
    except Exception as e:
        raise ValueError(f"Validation error for payload for mode {mode}: {e}")

    # --- Merge the client payload with the default payload to fill in missing values ---
    merged_payload = _deep_merge_dicts(
        ALL_DEFAULT_PAYLOADS[mode], payload_client
    )

    # --- Validate the merged payload using Pydantic for complete structure, types, and constraints ---
    try:
        _check_complete_payload(mode=mode, payload=merged_payload)
    except ValidationError as e:
        raise e

    return merged_payload


def _check_date(date_to_test: str, date_min: str, date_max: str) -> bool:
    """Checks that date_to_test is between date_min and date_max.

    Args:
        date_to_test (str): Date to test.
        date_min (str): Date min.
        date_max (str): Date max.

    Returns:
        bool: True if date_to_test is between date_min and date_max, False otherwise.
    """
    return date_min <= date_to_test <= date_max


def _check_date_start_end(date_start: str, date_end: str, product: str) -> None:
    """Checks that the dates are correct.

    Args:
        date_start (str): Start date.
        date_end (str): End date.
        product (str): Smart product. Allowed values: benchmark, ufi.
    """
    # --- Validate that the product parameter is one of the expected values ---
    _check_value_in_set(
        feature="product", value=product, correct_set=SMART_PRODUCTS
    )

    # --- Check the ordering of dates ---
    dates_order = _check_date(date_start, DATE_DEBUT, date_end) & _check_date(
        date_end, date_start, DATE_TODAY_STR
    )

    # --- Check duration conditions ---
    start_end = (
        datetime.strptime(date_end, "%Y-%m-%d")
        - datetime.strptime(date_start, "%Y-%m-%d")
    ).days >= 7
    start_today = (
        datetime.strptime(DATE_TODAY_STR, "%Y-%m-%d")
        - datetime.strptime(date_start, "%Y-%m-%d")
    ).days >= 7

    # --- Define conditions based on product type ---
    conditions_benchmark = (product == "benchmark") & dates_order
    conditions_ufi = (product == "ufi") & dates_order & start_end & start_today

    # --- Validate the conditions and raise an error if they are not met ---
    try:
        if not (conditions_benchmark | conditions_ufi):
            if product == "benchmark":
                raise ValueError(
                    "Dates must respect following conditions for historical"
                    f" benchmark: {DATE_DEBUT} <= date_start <= date_end <="
                    f" {DATE_TODAY_STR}"
                )
            else:
                raise ValueError(
                    "Dates must respect following conditions for historical"
                    f" UFI:\n- {DATE_DEBUT} <= date_start <= date_end <="
                    f" {DATE_TODAY_STR}\n- date_end must be at least one week"
                    " later than date_start\n- date_start must be at least one"
                    " week sooner than today"
                )
    except ValueError as e:
        raise e


def _datetime_to_date(date_time: str) -> str:
    """Transforms a datetime string ('%Y-%m-%dT%H:%M:%SZ') into date string ('%Y-%m-%d').

    Args:
        date_time (str): Datetime string in '%Y-%m-%dT%H:%M:%SZ' format.

    Returns:
        str: Date in '%Y-%m-%d' format.
    """
    return datetime.strftime(
        datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%d"
    )


def _date_minus_months(date: str, n_months: int) -> str:
    """Subtracts n_months to a date.

    Args:
        date (str): Date string in '%Y-%m-%d' format.
        n_months (int): Number of months to subtract to date.

    Returns:
        str: Date subtracted by n months.
    """
    # --- Convert the input date string to a datetime object ---
    date_date = datetime.strptime(date, "%Y-%m-%d")

    # --- Subtract the specified number of months ---
    date_min_months = date_date - relativedelta(months=n_months)

    # --- Return the maximum between the computed date and DATE_DEBUT (as string) ---
    return max(datetime.strftime(date_min_months, "%Y-%m-%d"), DATE_DEBUT)


def _process_benchmark_output(
    values_to_process: dict[str, dict], filters: list[str]
) -> dict[str, dict]:
    """Filters values returned according to filters. Used for benchmark method to filter rate ranges and emissions.

    Args:
        values_to_process (dict[str, dict]): Rates or emissions.
        filters (list[str]): Rate ranges or emission types.

    Returns:
        dict[str, dict]: Filtered values dictionary.
    """
    # --- Return the original values if no filters are provided, otherwise filter the keys ---
    values_process = (
        values_to_process
        if not filters
        else {k: v for k, v in values_to_process.items() if k in filters}
    )

    return values_process


def _split_values_into_batch(iterable: list, size: int) -> Iterator[list]:
    """Creates batches of length size from iterable.

    Args:
        iterable (list): List of elements to split.
        size (int): Size of the batch.

    Returns:
        Iterator[list]: Batches (lists) of max size elements.
    """
    it = iter(iterable)
    while True:
        batch = list(itertools.islice(it, size))
        if not batch:
            break
        yield batch


class Smart(API):
    """Creates a Smart object to use Upply benchmark and UFI products."""

    def __init__(
        self,
        access_token: str,
        env: str = "prod",
        timeout: int = 5,
        sleep_time: float = 0.2,
        retries: int = 0,
    ):
        """Initializes a Smart object with authentication and request settings.

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
            product="smart",
            timeout=timeout,
            sleep_time=sleep_time,
            retries=retries,
        )

    def benchmark(
        self,
        mode: str,
        payload: Union[dict[str, Any], list[dict[str, Any]]],
        historical: bool = False,
        **kwargs,
    ) -> dict[str, dict]:
        """Retrieves lane benchmark.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (Union[dict[str, Any], list[dict[str, Any]]]): Benchmark payload.
            historical (bool): Benchmark on multiple dates or not.

        Other Parameters:
            emission_types (list): Filter by emission type.
                                     Allowed values: co2, nmhc, nox, pm, primaryEnergy, so2.
            rate_ranges (list): Filter by rate range. Allowed values: low_high, min_max, no_range.

        Returns:
            dict[str, dict]: Benchmark result.
        """
        # --- Validate mode and filter parameters ---
        _check_value_in_set(feature="mode", value=mode, correct_set=MODES)
        emission_types_filter = kwargs.get("emission_types")
        rate_ranges_filter = kwargs.get("rate_ranges")
        if emission_types_filter:
            if not all(
                [em_type in EMISSION_TYPES for em_type in emission_types_filter]
            ):
                raise ValueError(
                    "emission_types: expected values from"
                    f" {', '.join(EMISSION_TYPES)} but got"
                    f" {', '.join(emission_types_filter)}"
                )
        if rate_ranges_filter:
            rate_ranges_filter = process_rate_range(
                client_rate_ranges=rate_ranges_filter
            )

        # --- Check that payload format correspond to historical value ---
        if (
            historical
            and not (isinstance(payload, list))
            or not historical
            and isinstance(payload, list)
        ):
            raise ValueError(
                "If historical is True, then payload must be a list of"
                " payloads."
            )

        # --- Construct the endpoint URL for benchmark ---
        base = MODES[mode]["benchmark"] + ("/batch" if historical else "")
        endpoint = urljoin(BENCHMARK_ENDPOINT, base)

        # --- Process the payload (merging, validating, and completing) ---
        if historical:
            payload_process = [
                _process_payload(mode=mode, payload_client=one_payload)
                for one_payload in payload
            ]
        else:
            payload_process = _process_payload(
                mode=mode, payload_client=payload
            )

        # --- Make the API request for benchmark and filter the result based on provided filters ---
        res = self._make_request(
            endpoint=endpoint, method="POST", json=payload_process
        )
        if historical:
            for elem in res["data"]:
                elem["benchmark"]["rate"]["values"] = _process_benchmark_output(
                    values_to_process=elem["benchmark"]["rate"]["values"],
                    filters=rate_ranges_filter,
                )
                elem["emissions"] = _process_benchmark_output(
                    values_to_process=elem["emissions"],
                    filters=emission_types_filter,
                )
        else:
            res["data"]["benchmark"]["rate"]["values"] = (
                _process_benchmark_output(
                    values_to_process=res["data"]["benchmark"]["rate"][
                        "values"
                    ],
                    filters=rate_ranges_filter,
                )
            )
            res["data"]["emissions"] = _process_benchmark_output(
                values_to_process=res["data"]["emissions"],
                filters=emission_types_filter,
            )

        return res["data"]

    def price(
        self, mode: str, payload: dict[str, Any], **kwargs
    ) -> dict[str, Union[str, dict]]:
        """Retrieves lane prices.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.

        Other Parameters:
            rate_ranges (list): Filter by rate range. Allowed values: low_high, min_max, no_range.


        Returns:
            dict[str, Union[str, dict]]: Benchmark results (only rates, not confidence nor emissions).
        """
        res = self.benchmark(mode=mode, payload=payload, **kwargs)
        return res["benchmark"]["rate"]

    def confidence(self, mode: str, payload: dict[str, Any]) -> str:
        """Retrieves lane confidence index.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.

        Returns:
            str: Confidence index.
        """
        res = self.benchmark(mode=mode, payload=payload)
        return res["benchmark"]["confidence_index"]

    def emissions(
        self, mode: str, payload: dict[str, Any], **kwargs
    ) -> dict[str, dict]:
        """Retrieves lane emissions.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.

        Other Parameters:
            emission_types (list): Filter by emission type.
                                     Allowed values: co2, nmhc, nox, pm, primaryEnergy, so2.

        Returns:
            dict[str, dict]: Benchmark results (only emissions, not rates nor confidence).
        """
        res = self.benchmark(mode=mode, payload=payload, **kwargs)
        return res["emissions"]

    def _historical(
        self,
        type_res: str,
        mode: str,
        payload: dict[str, Any],
        date_start: str,
        date_end: str,
        lookback_months: int,
        **kwargs,
    ) -> dict[str, Union[str, dict]]:
        """Retrieves the benchmark historical (benchmark or only rates).

        Args:
            type_res (str): Type of request. Allowed values: benchmark, price.
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months (int): Number of months of historical to compute (if filled, replaces date_start).

        Other Parameters:
            emission_types (list): Filter by emission type.
                                     Allowed values: co2, nmhc, nox, pm, primaryEnergy, so2.
            rate_ranges (list): Filter by rate range. Allowed values: low_high, min_max, no_range.

        Returns:
            dict[str, Union[str, dict]]: Benchmarks results.
        """
        # --- Validate request type ---
        _check_value_in_set(
            feature="type_res", value=type_res, correct_set=HISTORICAL_TYPES
        )

        # --- Set date_end to today's date if not provided ---
        if not date_end:
            date_end = DATE_TODAY_STR

        # --- Adjust date_start if lookback_months is provided ---
        if lookback_months:
            date_start = _date_minus_months(
                date=date_end, n_months=lookback_months
            )

        # --- Validate date range for benchmark ---
        _check_date_start_end(date_start, date_end, product="benchmark")

        # --- Generate list of lists of max 100 payloads, each payload corresponding to one date in date_range ---
        all_dates = generate_weekly_dates(date_start, date_end)
        all_payloads = [
            [
                {**payload, "schedule": {"etd": d.strftime("%Y-%m-%d")}}
                for d in batch
            ]
            for batch in _split_values_into_batch(all_dates, 100)
        ]

        # --- Fetch rates for each date ---
        all_res = {"rates": {"values": {}}}
        for batch in all_payloads:
            res = self.benchmark(
                mode=mode, payload=batch, historical=True, **kwargs
            )
            if "unit" not in all_res["rates"]:
                all_res["rates"]["unit"] = res[0]["benchmark"]["rate"]["unit"]
            for p, payload in enumerate(batch):
                all_res["rates"]["values"][payload["schedule"]["etd"]] = res[p][
                    "benchmark"
                ]["rate"]["values"]

        # --- For benchmark type, retrieve confidence index and emissions ---
        if type_res == "benchmark":
            all_res["confidence_index"] = res[0]["benchmark"][
                "confidence_index"
            ]
            all_res["emissions"] = res[0]["emissions"]

        return all_res

    def benchmark_historical(
        self,
        mode: str,
        payload: dict[str, Any],
        date_start: str = DATE_DEBUT,
        date_end: str = None,
        lookback_months: int = None,
        **kwargs,
    ) -> dict[str, Union[str, dict]]:
        """Retrieves the benchmark historical.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months (int): Number of months of historical to compute. If filled, replaces date_start.

        Other Parameters:
            emission_types (list): Filter by emission type.
                                     Allowed values: co2, nmhc, nox, pm, primaryEnergy, so2.
            rate_ranges (list): Filter by rate range. Allowed values: low_high, min_max, no_range.

        Returns:
            dict[str, Union[str, dict]]: Benchmarks results.
        """
        return self._historical(
            type_res="benchmark",
            mode=mode,
            payload=payload,
            date_start=date_start,
            date_end=date_end,
            lookback_months=lookback_months,
            **kwargs,
        )

    def price_historical(
        self,
        mode: str,
        payload: dict[str, Any],
        date_start: str = DATE_DEBUT,
        date_end: str = None,
        lookback_months: int = None,
        **kwargs,
    ) -> dict[str, dict]:
        """Retrieves the benchmark historical (only rates).

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            payload (dict[str, Any]): Benchmark payload.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months: Number of months of historical to compute. If filled, replaces date_start.

        Other Parameters:
            rate_ranges (list): Filter by rate range. Allowed values: low_high, min_max, no_range.

        Returns:
            dict[str, dict]: Benchmarks results (only rates).
        """
        return self._historical(
            type_res="price",
            mode=mode,
            payload=payload,
            date_start=date_start,
            date_end=date_end,
            lookback_months=lookback_months,
            **kwargs,
        )

    def ufi_iter(
        self,
        mode: str = None,
        market: str = None,
        name: str = "",
        lang: str = "fr",
    ) -> Iterator[tuple[str, str]]:
        """Streams UFIs, filtered by mode, market and name.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            market (str): Market type. Allowed values: spot, contract, full.
            name (str): Name of the UFI to look for.
            lang (str): UFI's name language. Allowed values: fr, en.

        Yields:
            tuple[str, str]: UFI code and name.
        """
        # --- Validate optional parameters ---
        _check_value_in_set(feature="mode", value=mode, correct_set=MODES)
        _check_value_in_set(
            feature="market", value=market, correct_set=UFI_MARKETS
        )
        _check_value_in_set(
            feature="lang", value=lang, correct_set=UFI_LANGUAGES
        )

        # --- Set request settings ---
        markets = [market] if market else UFI_MARKETS
        offset = 0
        batch_size = 10
        max_retries_5xx = 2

        # --- Make the API request and process the returned data ---
        res_ufi = {}
        while True:
            # --- Build query parameters for UFI list ---
            params = {"limit": str(batch_size), "offset": str(offset)}
            if mode:
                params["mode"] = MODES[mode]["ufi"]
            endpoint = UFI_ENDPOINT + "?" + urlencode(params)

            # --- Make the API request ---
            attempt = 0
            while True:
                try:
                    res = self._make_request(endpoint=endpoint, method="GET")
                    break
                except Exception as exc:
                    is_5xx = (
                        getattr(exc, "status", None) and 500 <= exc.status < 600
                    )
                    if is_5xx and attempt < max_retries_5xx:
                        attempt += 1
                        continue
                    raise

            # --- No more UFIs to retrieve ---
            data = res.get("data", [])
            if not data:
                break

            # --- Filter UFIs based on name and market criteria ---
            for ufi in data:
                ufi_market = ufi.get("market")
                names = ufi.get("name", {})
                ufi_name = names.get(lang, "")

                if ufi_market in markets and (name.lower() in ufi_name.lower()):
                    yield ufi["code"], ufi_name

            # --- No more UFIs to retrieve ---
            if len(data) < batch_size:
                break

            # --- To retrieve next UFIs
            offset += batch_size

    def ufi_list(
        self,
        mode: str = None,
        market: str = None,
        name: str = "",
        lang: str = "fr",
    ) -> dict[str, str]:
        """
        Retrieves list of UFIs, filtered by mode, market and name.
        Uses the lazy iterator to build the dictionary.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            market (str): Market type. Allowed values: spot, contract, full.
            name (str): Name of the UFI to look for.
            lang (str): UFI's name language. Allowed values: fr, en.

        Returns:
            dict[str, str]: UFIs code and name.
        """
        return dict(
            self.ufi_iter(mode=mode, market=market, name=name, lang=lang)
        )

    def ufi_historical(
        self,
        code: str,
        date_start: str = DATE_DEBUT,
        date_end: str = None,
        lookback_months: int = None,
        date_baseline: str = DATE_DEBUT,
    ) -> dict[str, Union[str, dict]]:
        """Retrieves the UFI historical.

        Args:
            code (str): UFI code.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months (int): Number of months of historical to compute. If filled, replaces date_start.
            date_baseline (str): Baseline date to compute base 100 rates.

        Returns:
            dict[str, Union[str, dict]]: UFI historical rates.
        """
        # --- Validate the lookback_months parameter ---
        if lookback_months and (lookback_months < 0):
            raise ValueError("lookback_months must be positive if filled")

        # --- Initialize pagination parameters ---
        offset = 0
        limit = 100

        # --- Set date_end to today's date if not provided ---
        if not date_end:
            date_end = DATE_TODAY_STR

        # --- Adjust date_start if lookback_months is provided ---
        if lookback_months:
            date_start = _date_minus_months(
                date=date_end, n_months=lookback_months
            )

        # --- Validate the date range for UFI historical data ---
        _check_date_start_end(date_start, date_end, product="ufi")
        if not _check_date(date_baseline, DATE_DEBUT, DATE_TODAY_STR):
            raise ValueError(
                f"date_baseline must be between {DATE_DEBUT} and"
                f" {DATE_TODAY_STR}"
            )

        # --- Initialize the result dictionary with default rate unit ---
        res_ufi = {"rates": {"unit": "base100", "values": {}}}
        next_page = True

        # --- Prepare the base URL and parameters for UFI historical retrieval ---
        endpoint_ufi_process = UFI_ENDPOINT + "/"
        code_process = code + "/"
        params = {
            "startDate": date_start,
            "endDate": date_end,
            "baselineStart": date_baseline,
            "offset": offset,
            "limit": limit,
        }

        # --- Loop through paginated responses until all historical data is retrieved ---
        while next_page:
            # Build the complete endpoint URL using urljoin and urlencode for parameters
            endpoint = (
                urljoin(endpoint_ufi_process, code_process)
                + UFI_HISTORICAL_ENDPOINT
                + "?"
                + urlencode(params)
            )
            # Make the API request for the current page
            res = self._make_request(endpoint=endpoint, method="GET")
            # Update the result dictionary with data from the current page
            res_ufi["rates"]["values"].update({
                _datetime_to_date(elem["dateTime"]): elem["value"]
                for elem in res["data"]
            })
            # Check if there's another page; update offset accordingly or exit loop
            if res["pagination"]["nextPage"]:
                params["offset"] += limit
            else:
                next_page = False

        return res_ufi

    def ufi_forecast(
        self,
        code: str,
        nb_weeks: int = UFI_NB_WEEKS_MAX,
        date_baseline: str = DATE_DEBUT,
    ) -> dict[str, Union[str, dict]]:
        """Retrieves the UFI short-term forecast.

        Args:
            code (str): UFI code.
            nb_weeks (int): Number of weeks to forecast.
            date_baseline (str): Baseline date to compute base 100 rates.

        Returns:
            dict[str, Union[str, dict]]: UFI short-term forecast rates.
        """
        # --- Validate nb_weeks and baseline date ---
        if (nb_weeks < 0) or (nb_weeks > UFI_NB_WEEKS_MAX):
            raise ValueError(
                f"nb_weeks must be between 0 and {UFI_NB_WEEKS_MAX}"
            )
        if not _check_date(date_baseline, DATE_DEBUT, DATE_TODAY_STR):
            raise ValueError(
                f"date_baseline must be between {DATE_DEBUT} and"
                f" {DATE_TODAY_STR}"
            )

        # --- Construct the endpoint URL ---
        endpoint_ufi_process = UFI_ENDPOINT + "/"
        code_process = code + "/"
        params = {"baselineStart": date_baseline}
        endpoint = (
            urljoin(endpoint_ufi_process, code_process)
            + UFI_FORECAST_ENDPOINT
            + "?"
            + urlencode(params)
        )

        # --- Make the API request ---
        res = self._make_request(endpoint=endpoint, method="GET")

        # --- Update the dictionary with forecast values, limiting the number of weeks to nb_weeks ---
        res_ufi = {"rates": {"unit": "base100", "values": {}}}
        res_ufi["rates"]["values"].update({
            _datetime_to_date(elem["dateTime"]): elem["value"]
            for e, elem in enumerate(res["data"])
            if e < nb_weeks
        })

        return res_ufi

    def ufi_historical_and_forecast(
        self,
        code: str,
        date_start: str = DATE_DEBUT,
        date_end: str = None,
        lookback_months: int = None,
        nb_weeks_forecast: int = 6,
        date_baseline: str = DATE_DEBUT,
    ) -> dict[str, dict]:
        """Retrieves the UFI historical and forecast rates.

        Returns forecast rates only if date_end is not filled (and nb_weeks_forecast not null)
        or if date_end >= first forecast rate date.

        Args:
            code (str): UFI code.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months (int): Number of months of historical to compute. If filled, replaces date_start.
            nb_weeks_forecast (int): Number of weeks to forecast.
            date_baseline (str): Baseline date to compute base 100 rates.

        Returns:
            dict[str, dict]: UFI historical and forecast rates.
        """
        # --- Initialize the historical and forecast result dictionary ---
        res_full = {"historical": {}, "forecast": {}}

        # --- Determine the effective end date for historical data ---
        date_end_historical = (
            min(date_end, DATE_TODAY_STR) if date_end else date_end
        )

        # --- Retrieve historical rates if the start date is not in the future ---
        if date_start <= DATE_TODAY_STR:
            res_full["historical"] = self.ufi_historical(
                code=code,
                date_start=date_start,
                date_end=date_end_historical,
                lookback_months=lookback_months,
                date_baseline=date_baseline,
            )

        # --- Determine the set of dates for the historical rates ---
        historical_rates_dates = (
            res_full["historical"]["rates"]["values"].keys()
            if res_full["historical"]
            else [DATE_DEBUT]
        )

        # --- Retrieve forecast rates if applicable ---
        # Forecast is retrieved if no end date is provided or if the provided end date
        # is later than the maximum date in the historical data
        if (not date_end) or (date_end > max(historical_rates_dates)):
            res_full["forecast"] = self.ufi_forecast(
                code=code,
                nb_weeks=nb_weeks_forecast,
                date_baseline=date_baseline,
            )
            # If an end date is provided, filter forecast rates to not exceed it
            if date_end:
                res_full["forecast"]["rates"]["values"] = {
                    date: value
                    for date, value in res_full["forecast"]["rates"][
                        "values"
                    ].items()
                    if date <= date_end
                }

        return res_full

    def ufi_historical_and_forecast_multiple(
        self,
        mode: str = None,
        market: str = None,
        name: str = "",
        date_start: str = DATE_DEBUT,
        date_end: str = None,
        lookback_months: int = None,
        nb_weeks_forecast: int = 6,
        date_baseline: str = DATE_DEBUT,
    ) -> dict[str, dict]:
        """Retrieves the UFI historical and forecast rates for multiple UFI codes.

        Retrieves UFI codes from ufi_list() and retrieves historical / forecast rates for all these UFI codes
        with ufi_historical_and_forecast(). Returns an empty result if no UFI corresponds to the search.

        Args:
            mode (str): Transport mode. Allowed values: air, road_emea, road_na, sea_longterm.
            market (str): Market type. Allowed values: spot, contract, full.
            name (str): Name of the UFI to look for.
            date_start (str): Start date of the historical.
            date_end (str): End date of the historical.
            lookback_months (int): Number of months of historical to compute. If filled, replaces date_start.
            nb_weeks_forecast (int): Number of weeks to forecast.
            date_baseline (str): Baseline date to compute base 100 rates.

        Returns:
            dict[str, dict]: UFI historical and forecast rates for all UFI corresponding to UFI search.
        """
        # --- Retrieve UFI codes using the ufi_list method based on the provided filters ---
        ufi_codes = self.ufi_list(mode=mode, market=market, name=name)

        # --- Iterate over each UFI code and fetch its historical and forecast rates ---
        res_full = {}
        for ufi_code in ufi_codes:
            res = self.ufi_historical_and_forecast(
                code=ufi_code,
                date_start=date_start,
                date_end=date_end,
                lookback_months=lookback_months,
                nb_weeks_forecast=nb_weeks_forecast,
                date_baseline=date_baseline,
            )
            res_full[ufi_code] = res

        return res_full
