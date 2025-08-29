from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, NonNegativeInt


class StartScanData(BaseModel):
    new_installation: bool = Field(False, alias="newInstallation")
    no_addressing: bool = Field(False, alias="noAddressing")
    use_lines: list[NonNegativeInt] = Field([], alias="useLines")


class ScanState(StrEnum):
    NOT_STARTED = "not started"
    CANCELLED = "cancelled"
    DONE = "done"
    ADDRESSING = "addressing"
    IN_PROGRESS = "in progress"


class ScanData(BaseModel):
    id: str = ""
    progress: Optional[float] = None
    found: Optional[int] = None
    found_sensors: Optional[int] = Field(None, alias="foundSensors")
    status: ScanState = ScanState.NOT_STARTED
    lines: list[dict] = []
