from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import model_validator


class GeoLocation(BaseModel):
    """A geolocation, composed of latitude and longitude, or country code and label"""

    latitude: Optional[float] = Field(None, le=90, ge=-90)
    longitude: Optional[float] = Field(None, le=180, ge=-180)
    country_code: Optional[str] = Field(
        None,
        description="The country code of the location (ISO 3166-1 alpha-2).",
    )
    label: Optional[str] = Field(None, description="The label of the location.")

    @model_validator(mode="after")
    def check_coords_or_cc_label(cls, model):
        """Checks that there is at least either latitude and longitude or country_code and label."""
        has_coords = model.latitude is not None and model.longitude is not None
        has_cc_label = (
            model.country_code is not None and model.label is not None
        )
        if not (has_coords or has_cc_label):
            raise ValueError(
                "Location requires at least latitude and longitude OR"
                " country_code and label."
            )
        return model


class Schedule(BaseModel):
    """A schedule, composed of a date"""

    etd: datetime = Field(
        ..., description="Estimated date of departure of the shipment."
    )


class WeightUnit(str, Enum):
    """A weight unit object (kg)"""

    kg = "kg"


class Weight(BaseModel):
    """A weight object, composed of a unit and a value"""

    value: float = Field(2000.0, ge=100, le=40000)
    unit: WeightUnit = Field("kg", description="Weight in kg.")
