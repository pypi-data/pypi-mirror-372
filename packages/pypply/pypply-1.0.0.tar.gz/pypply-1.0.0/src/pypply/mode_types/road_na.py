from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from .commons import GeoLocation
from .commons import Schedule


class TruckType(str, Enum):
    """A type of truck, specific to roadna"""

    dry = "DRY"
    reefer = "REEFER"


class WeightUnit(str, Enum):
    """A weight unit object (lbs)"""

    lbs = "lbs"


class Weight(BaseModel):
    """A weight object, composed of a unit and a value, specific to roadna"""

    value: float = Field(2000.0, ge=45, le=99999)
    unit: WeightUnit = Field("lbs", description="Weight in lbs.")


class Shipment(BaseModel):
    """A shipment object, composed of truck type and weight objects"""

    truck_type: TruckType = Field(
        ...,
        description=(
            "Available truck types:\n\n- Dry: DRY\n\n- Reefer: REEFER\n"
        ),
    )
    weight: Weight


class Pricing(BaseModel):
    """A pricing object, composed of fuel_surcharge_included and contracts_included"""

    fuel_surcharge_included: bool = Field(
        ...,
        description="Set as _True_ to include fuel charges in the estimation.",
    )
    contracts_included: bool = Field(
        ...,
        description=(
            "Set as _True_ to include contract rates in the estimation."
        ),
    )


class PayloadRoadna(BaseModel):
    """A payload object, specific to roadna mode"""

    pickup: GeoLocation
    delivery: GeoLocation
    shipment: Shipment
    schedule: Schedule
    pricing: Pricing
