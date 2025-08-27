from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from .commons import GeoLocation
from .commons import Schedule
from .commons import Weight


class Industry(str, Enum):
    """A type of industry"""

    all = "all"
    automotive = "automotive"
    electronics = "electronics"
    food = "food"
    high_tech = "high_tech"
    luxury = "luxury"
    pharmaceutical = "pharmaceutical"


class WeightAir(Weight):
    """A weight object, composed of a unit and a value, specific to air"""

    value: float = Field(100.0, ge=1, le=5000)


class Shipment(BaseModel):
    """A shipment object, composed of industry and weight objects, and hazardous and reefer"""

    hazardous: bool = Field(
        ..., description="Set as _True_ to apply hazardous fees."
    )
    industry: Industry = Field(
        ...,
        description=(
            "Available industries:\n"
            "\n- all\n"
            "\n- automotive\n"
            "\n- electronics\n"
            "\n- food\n"
            "\n- high_tech\n"
            "\n- luxury\n"
            "\n- pharma\n"
        ),
    )
    reefer: bool = Field(..., description="Set as _True_ to apply reefer fees.")
    weight: WeightAir


class ServiceLevel(str, Enum):
    """A service level object"""

    standard = "standard"
    express = "express"


class ServiceType(str, Enum):
    """A service type object: is the shipment with or without pre-(post-)carriage, specific to air"""

    airport_to_airport = "ata"
    airport_to_door = "atd"
    door_to_airport = "dta"
    door_to_door = "dtd"


class Pricing(BaseModel):
    """A pricing object, composed of a service type and service level objects, and customs_included"""

    service_type: ServiceType = Field(
        ...,
        description=(
            "Available service types:\n"
            "\n- Airport To Airport: ata\n"
            "\n- Airport To Door: atd\n"
            "\n- Door To Airport: dta\n"
            "\n- Door To Door: dtd\n"
        ),
    )
    service_level: ServiceLevel = Field(
        ...,
        description=(
            "Available service types:\n"
            "\n- Standard delivery: standard\n"
            "\n- Express delivery: express\n"
        ),
    )
    customs_included: bool = Field(
        ...,
        description=(
            "Set as _True_ to include customs fees to the price estimation."
        ),
    )


class PayloadAir(BaseModel):
    """A payload object, specific to air mode"""

    pickup: GeoLocation
    delivery: GeoLocation
    shipment: Shipment
    schedule: Schedule
    pricing: Pricing
