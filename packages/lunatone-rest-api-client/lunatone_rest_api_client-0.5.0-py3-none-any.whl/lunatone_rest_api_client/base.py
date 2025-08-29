from abc import ABC, abstractmethod

from lunatone_rest_api_client.models import ControlData
from lunatone_rest_api_client.models.common import ColorRGBData, ColorWAFData


class Controllable(ABC):
    """Class that provides basic control methods."""

    async def switch_on(self) -> None:
        """Switch on the device."""
        await self.async_control(ControlData(switchable=True))

    async def switch_off(self) -> None:
        """Switch off the device."""
        await self.async_control(ControlData(switchable=False))

    async def fade_to_brightness(self, brightness: float) -> None:
        """Fade to provided brightness level."""
        await self.async_control(ControlData(dimmable=brightness))

    async def fade_to_last_active_level(self) -> None:
        """Fade to last active level."""
        await self.async_control(ControlData(gotoLastActive=True))

    async def fade_to_color_temperature(self, color_temperature: int) -> None:
        """Fade to color temperature."""
        await self.async_control(ControlData(colorKelvin=color_temperature))

    async def fade_to_rgbw_color(
        self, rgb_color: tuple[float, float, float], white: float = None
    ) -> None:
        """Fade to RGBW color."""
        if white is not None:
            await self.async_control(ControlData(colorWAF=ColorWAFData(w=white)))
        await self.async_control(
            ControlData(
                colorRGB=ColorRGBData(r=rgb_color[0], g=rgb_color[1], b=rgb_color[2])
            )
        )

    @abstractmethod
    async def async_control(self, data: ControlData) -> None:
        """Control the instance."""
