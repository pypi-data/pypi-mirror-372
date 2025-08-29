from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeInt


class SensorMeasurementUnit(StrEnum):
    NONE = ""
    DEGREE_CELSIUS = "°C"
    PERCENT = "%"
    HECTOPASCAL = "hPa"
    PARTS_PER_MILLION = "ppm"
    PARTS_PER_BILLION = "ppb"
    INDOOR_AIR_QUALITY = "AQI"
    LUX = "lx"


class SensorType(StrEnum):
    UNKNOWN = "unknown"
    TEMPERATURE = "temperature"
    AIR_HUMIDITY = "airHumidity"
    AIR_PRESSURE = "airPressure"
    ECO2 = "eCO2"
    VOC = "VOC"
    AIR_QUALITY = "airQuality"
    LIGHT = "light"
    OCCUPANCY = "occupancy"


class SensorAddressType(StrEnum):
    INTERNAL = "internal"
    DALI = "dali"


class SensorDaliAddress(BaseModel):
    line: int
    address: int
    instanceNumber: int


class SensorData(BaseModel):
    id: NonNegativeInt
    name: str = ""
    unit: SensorMeasurementUnit = SensorMeasurementUnit.NONE
    type: SensorType = SensorType.UNKNOWN
    value: Optional[float] = None
    timestamp: Optional[str] = None
    address_type: Optional[SensorAddressType] = Field(None, alias="addressType")
    dali_sensor_address: Optional[SensorDaliAddress] = Field(None, alias="daliSensorAddress")


class SensorsData(BaseModel):
    sensors: list[SensorData]
