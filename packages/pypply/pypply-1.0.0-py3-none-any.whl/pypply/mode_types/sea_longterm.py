from enum import Enum

from pydantic import BaseModel
from pydantic import Field

from .commons import GeoLocation
from .commons import Schedule


class ContainerType(str, Enum):
    """A type of container"""

    GP20 = "20gp"
    GP40 = "40gp"
    HC40 = "40hc"
    RE20 = "20re"
    RF40 = "40rf"
    RH40 = "40rh"
    RF20 = "20rf"


class Container(BaseModel):
    """A container object, composed of a type of container and a number of containers"""

    unit: ContainerType = Field(
        ...,
        description=(
            "Available container types:\n"
            "\n- 20 feets General Purpose container: 20gp\n"
            "\n- 20 feets Reefer container: 20re\n"
            "\n- 20 feets Reefer container: 20rf\n"
            "\n- 40 feets General Purpose container: 40gp\n"
            "\n- 40 feets High Cube container: 40hc\n"
            "\n- 40 feets Reefer container: 40rf\n"
            "\n- 40 feets High Cube Reefer container: 40rh\n"
        ),
    )
    value: int = Field(..., ge=1, le=999999)


class ServiceType(str, Enum):
    """A service type object: is the shipment with or without pre-(post-)carriage, specific to sea long-term"""

    port_to_port = "ptp"
    port_to_door = "ptd"
    door_to_port = "dtp"
    door_to_door = "dtd"


class THC(BaseModel):
    """A Terminal Handling Charges object"""

    origin: bool = Field(
        ...,
        description=(
            "Set as _True_ to include _origin_ Terminal Handling Charges to the"
            " price estimation."
        ),
    )
    destination: bool = Field(
        ...,
        description=(
            "Set as _True_ to include _destination_ Terminal Handling Charges"
            " to the price estimation."
        ),
    )


class Shipment(BaseModel):
    """A shipment object, composed of a container object and hazardous"""

    container: Container
    hazardous: bool = Field(
        ..., description="Set as _True_ to apply hazardous cargo fees."
    )


class Pricing(BaseModel):
    """A pricing object, composed of a service type and a thc objects"""

    service_type: ServiceType = Field(
        ...,
        description=(
            "Available service types:\n"
            "\n- Port To Port: ptp\n"
            "\n- Port To Door: ptd\n"
            "\n- Door To Port: dtp\n"
            "\n- Door To Door: dtd\n"
        ),
    )
    thc: THC


class PayloadSeaLongterm(BaseModel):
    """A payload object, specific to sea long-term mode"""

    pickup: GeoLocation
    delivery: GeoLocation
    shipment: Shipment
    schedule: Schedule
    pricing: Pricing
