from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from .commons import GeoLocation
from .commons import Schedule
from .commons import Weight


class GoodsType(str, Enum):
    """A type of goods"""

    GEN = "GEN"
    REF = "REF"
    BUL = "BUL"
    FOO = "FOO"
    LIQ = "LIQ"
    ROL = "ROL"


class TruckType(str, Enum):
    """A type of truck, specific to roademea"""

    TRL = "TRL"
    FBD = "FBD"
    CON = "CON"
    CIT = "CIT"
    BEN = "BEN"


class VolumeUnit(str, Enum):
    """A volume unit object"""

    loading_meters = "loading_meters"
    cubic_meters = "cubic_meters"
    pallets = "pallets"


class Volume(BaseModel):
    """A volume object, composed of a unit and a value"""

    value: float = Field(14, ge=1, le=100)
    unit: VolumeUnit = Field(
        "loading_meters",
        description=(
            "Unit types for _Volume_:\n"
            "\n- Pallets: pallets\n"
            "\n- Cubic meter: cubic_meters\n"
            "\n- Linear meter: loading_meters"
        ),
    )


class WeightRoademea(Weight):
    """A weight object, composed of a unit and a value, specific to roademea"""

    value: float = Field(2000.0, ge=100, le=40000)


class Market(str, Enum):
    """A market object"""

    spot = "spot"
    contract = "contract"


class Shipment(BaseModel):
    """A shipment object, composed of goods type, truck type, weight and volume objects, and hazardous"""

    goods_type: GoodsType = Field(
        ...,
        description=(
            "Available goods types:\n"
            "\n- General cargo: GEN\n"
            "\n- Reefer: REF\n"
            "\n- Bulk: BUL\n"
            "\n- Food: FOO\n"
            "\n- Liquid: LIQ\n"
            "\n- Rolling material: ROL\n"
        ),
    )
    truck_type: TruckType = Field(
        ...,
        description=(
            "Available truck types:\n"
            "\n- Tautliner: TRL\n"
            "\n- Flatbed: FBD\n"
            "\n- Container: CON\n"
            "\n- Tank: CIT\n"
            "\n- Dump truck: BEN\n"
        ),
    )
    weight: WeightRoademea
    volume: Volume
    hazardous: bool = Field(
        ..., description="Set as _True_ to apply hazardous cargo fees."
    )


class Pricing(BaseModel):
    """A pricing object, composed of fuel_surcharge_included and a market object"""

    fuel_surcharge_included: bool = Field(
        ...,
        description="Set as _True_ to include fuel charges in the estimation.",
    )
    market: Market


class PayloadRoademea(BaseModel):
    """A payload object, specific to roademea mode"""

    pickup: GeoLocation
    delivery: GeoLocation
    shipment: Shipment
    schedule: Schedule
    pricing: Pricing
