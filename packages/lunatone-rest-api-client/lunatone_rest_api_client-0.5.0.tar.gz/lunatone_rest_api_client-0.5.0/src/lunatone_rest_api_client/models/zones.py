from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt

from lunatone_rest_api_client.models import FeaturesStatus, TimeSignature


class ZoneTarget(BaseModel):
    type: str
    id: Optional[NonNegativeInt] = None


class ZoneData(BaseModel):
    id: PositiveInt
    name: str = ""
    targets: list[ZoneTarget] = []
    features: Optional[FeaturesStatus] = None
    time_signature: Optional[TimeSignature] = Field(None, alias="timeSignature")


class ZonesData(BaseModel):
    zones: list[ZoneData]
    time_signature: TimeSignature = Field(alias="timeSignature")
