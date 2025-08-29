from typing import Optional

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt

from lunatone_rest_api_client.models import (
    DALIType,
    FeaturesStatus,
    TimeSignature,
)


class DeviceStatus(BaseModel):
    raw: NonNegativeInt = 0
    control_gear_failure: bool = Field(False, alias="controlGearFailure")
    lamp_failure: bool = Field(False, alias="lampFailure")
    lamp_on: bool = Field(False, alias="lampOn")
    limit_error: bool = Field(False, alias="limitError")
    fade_running: bool = Field(False, alias="fadeRunning")
    reset_state: bool = Field(False, alias="resetState")
    is_unaddressed: bool = Field(False, alias="isUnaddressed")
    power_cycle_see: bool = Field(False, alias="powerCycleSeen")


class DeviceData(BaseModel):
    id: PositiveInt
    name: str = ""
    type: str = "default"
    available: Optional[bool] = None
    status: Optional[DeviceStatus] = None
    features: Optional[FeaturesStatus] = None
    scenes: list = []
    groups: list[NonNegativeInt] = []
    address: Optional[NonNegativeInt] = None
    line: Optional[NonNegativeInt] = None
    dali_types: list[DALIType | NonNegativeInt] = Field([], alias="daliTypes")
    time_signature: Optional[TimeSignature] = Field(None, alias="timeSignature")


class DevicesData(BaseModel):
    devices: list[DeviceData]
    time_signature: Optional[TimeSignature] = Field(None, alias="timeSignature")


class DeviceUpdateData(BaseModel):
    name: str
    groups: Optional[list[NonNegativeInt]] = None
