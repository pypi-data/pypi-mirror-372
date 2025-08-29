from typing import Optional

from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.base import Controllable
from lunatone_rest_api_client.models import (
    ControlData,
    DeviceData,
    DevicesData,
    DeviceUpdateData,
    TimeSignature,
)

_PATH = "devices"


class Device(Controllable):
    """Class that represents a Device object in the API."""

    base_path: str = _PATH[:-1]

    def __init__(self, auth: Auth, data: DeviceData) -> None:
        """Initialize a device object."""
        self._auth = auth
        self._data = data

    @property
    def path(self) -> str:
        """Return the resource path."""
        return f"{self.base_path}/{self.id}"

    @property
    def data(self) -> DeviceData:
        """Return the raw device data."""
        return self._data

    @property
    def id(self) -> int:
        """Return the ID of the device."""
        return self.data.id

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self.data.name

    @property
    def time_signature(self) -> Optional[TimeSignature]:
        """Return the time signature."""
        return self.data.time_signature

    @property
    def is_on(self) -> bool:
        """Return if the light is on."""
        return self.data.features.switchable.status

    @property
    def brightness(self) -> Optional[float]:
        """Return the brightness of the light."""
        return self.data.features.dimmable.status

    @property
    def color_temperature(self) -> Optional[int]:
        """Return the color temperature of the light in kelvin."""
        return self.data.features.color_kelvin.status

    @property
    def rgb_color(self) -> Optional[tuple[float, float, float]]:
        """Return the RGB color of the light as tuple."""
        return (
            self.data.features.color_rgb.status.red,
            self.data.features.color_rgb.status.green,
            self.data.features.color_rgb.status.blue,
        )

    @property
    def rgbw_color(self) -> Optional[tuple[float, float, float, float]]:
        """Return the RGBW color of the light as tuple."""
        return (*self.rgb_color, self.data.features.color_waf.status.white)

    @property
    def xy_color(self) -> Optional[tuple[float, float]]:
        """Return the XY color of the light as tuple."""
        return (
            self.data.features.color_xy.status.x,
            self.data.features.color_xy.status.y,
        )

    async def async_update(self, data: DeviceUpdateData = None) -> None:
        """Update the device data."""
        if data is not None:
            json_data = data.model_dump(by_alias=True, exclude_none=True)
            response = await self._auth.put(self.path, json=json_data)
        else:
            response = await self._auth.get(self.path)
        self._data = DeviceData.model_validate(await response.json())

    async def async_control(self, data: ControlData) -> None:
        """Control the device."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        await self._auth.post(f"{self.path}/control", json=json_data)


class Devices:
    """Class that represents a Devices object in the API."""

    path: str = _PATH
    _data: DevicesData = None

    def __init__(self, auth: Auth) -> None:
        """Initialize a Devices object."""
        self._auth = auth

    @property
    def data(self) -> Optional[DevicesData]:
        """Return the raw devices data."""
        return self._data

    @property
    def devices(self) -> list[Device]:
        if self.data:
            return [Device(self._auth, device) for device in self.data.devices]
        return []

    @property
    def time_signature(self) -> Optional[TimeSignature]:
        return self.data.time_signature if self.data else None

    async def async_update(self) -> None:
        response = await self._auth.get(self.path)
        self._data = DevicesData.model_validate(await response.json())
