from datetime import datetime
from datetime import timezone

import pandas as pd

# GLOBAL
ENVS = ["prod", "sandbox"]
GEO_KEYS = ["pickup", "delivery"]
LAT_LON_KEYS = ["latitude", "longitude"]
LABEL_KEYS = ["label", "country_code"]


# SMART
MODES = {
    "air": {"benchmark": "air", "ufi": "air"},
    "road_emea": {"benchmark": "road-emea", "ufi": "roademea"},
    "road_na": {"benchmark": "road-na", "ufi": "roadna"},
    "sea_longterm": {"benchmark": "sea-fcl", "ufi": "sea"},
}
SMART_PRODUCTS = ["benchmark", "ufi"]
DATE_DEBUT = "2017-01-01"
DATE_TODAY_STR = datetime.now(timezone.utc).strftime("%Y-%m-%d")

BENCHMARK_ENDPOINT = "benchmark/"
EMISSION_TYPES = ["co2", "nmhc", "nox", "pm", "primaryEnergy", "so2"]
RATE_RANGES = ["low_high", "min_max", "no_range"]
HISTORICAL_TYPES = ["benchmark", "price"]

UFI_ENDPOINT = "ufi"
UFI_HISTORICAL_ENDPOINT = "indices/past"
UFI_FORECAST_ENDPOINT = "indices/short-term-future"
UFI_MARKETS = ["spot", "contract", "full"]
UFI_LANGUAGES = ["fr", "en"]
UFI_NB_WEEKS_MAX = 6

ALL_DEFAULT_PAYLOADS = {
    "air": {
        "shipment": {
            "hazardous": False,
            "industry": "all",
            "reefer": False,
            "weight": {"value": 100, "unit": "kg"},
        },
        "schedule": {"etd": DATE_TODAY_STR},
        "pricing": {
            "customs_included": False,
            "service_level": "standard",
            "service_type": "ata",
        },
    },
    "road_emea": {
        "shipment": {
            "goods_type": "GEN",
            "truck_type": "TRL",
            "volume": {"unit": "pallets", "value": 33},
            "weight": {"value": 24000, "unit": "kg"},
            "hazardous": False,
        },
        "schedule": {"etd": DATE_TODAY_STR},
        "pricing": {"market": "contract", "fuel_surcharge_included": True},
    },
    "road_na": {
        "shipment": {
            "truck_type": "DRY",
            "weight": {"unit": "lbs", "value": 2000},
        },
        "schedule": {"etd": DATE_TODAY_STR},
        "pricing": {
            "contracts_included": False,
            "fuel_surcharge_included": False,
        },
    },
    "sea_longterm": {
        "shipment": {
            "container": {"unit": "20gp", "value": 1},
            "hazardous": False,
        },
        "schedule": {"etd": DATE_TODAY_STR},
        "pricing": {
            "service_type": "ptp",
            "thc": {"origin": True, "destination": True},
        },
    },
}


# GEOGRAPHY
GEO_ENDPOINT = "locations/search"
LOCATION_TYPES = ["airport", "city", "seaport"]


# FUNCTIONS
def process_rate_range(client_rate_ranges: list[str]) -> list[str]:
    """Processes rate ranges, so it can be used with benchmark method.

    Args:
        - client_rate_ranges (list[str]): Rate ranges chosen by client.

    Returns:
        list[str]: Rate ranges keys to filter in rates data returned.
    """
    if not all(
        [rate_range in RATE_RANGES for rate_range in client_rate_ranges]
    ):
        raise ValueError(
            "client_rate_ranges: expected values from"
            f" {', '.join(RATE_RANGES)} but got {', '.join(client_rate_ranges)}"
        )

    rate_ranges_process = (
        ["median"]
        if "no_range" in client_rate_ranges
        else ["median"]
        + [
            rr
            for rr_list in [
                rate_range.split("_") for rate_range in client_rate_ranges
            ]
            for rr in rr_list
        ]
    )

    return rate_ranges_process


def generate_weekly_dates(start: str, end: str) -> pd.DatetimeIndex:
    """Generates weekly dates between start date and end date.

    Args:
        - start (str): Start date.
        - end (str): End date.

    Returns:
        pd.DatetimeIndex: List corresponding to date range.
    """
    return pd.date_range(start=start, end=end, freq="W")
