from enum import StrEnum

from pydantic import BaseModel, Field


class DescriptorData(BaseModel):
    lines: int = 0
    bufferSize: int = 0
    tickResolution: int = 0
    maxYnFrameSize: int = 0
    implementedMacros: list[int] = []
    deviceListSpecifier: int = 0
    protocolVersionMajor: int = 1
    protocolVersionMinor: int = 0
    powerSupplyImplemented: bool = False


class DeviceInfoData(BaseModel):
    serial: int
    gtin: int
    pcb: str
    article_number: int = Field(alias="articleNumber")
    article_info: str = Field("", alias="articleInfo")
    production_year: int = Field(alias="productionYear")
    production_week: int = Field(alias="productionWeek")


class LineStatus(StrEnum):
    OK = "ok"
    LOW_POWER = "lowPower"
    NO_POWER = "noPower"


class DALIBusData(BaseModel):
    send_blocked_initialize: bool = Field(alias="sendBlockedInitialize")
    send_blocked_quiescent: bool = Field(alias="sendBlockedQuiescent")
    send_blocked_macro_running: bool = Field(alias="sendBlockedMacroRunning")
    send_buffer_full: bool = Field(alias="sendBufferFull")
    line_status: LineStatus = Field(alias="lineStatus")


class InfoData(BaseModel):
    name: str
    version: str
    tier: str = "basic"
    emergency_light: bool = Field(False, alias="emergencyLight")
    node_red: bool = Field(False, alias="nodeRed")
    errors: dict[str, str] = {}
    descriptor: DescriptorData = DescriptorData()
    device: DeviceInfoData
    lines: dict[str, DALIBusData] = {}
