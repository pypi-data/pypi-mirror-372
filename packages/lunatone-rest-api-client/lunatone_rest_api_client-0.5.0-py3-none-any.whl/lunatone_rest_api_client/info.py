from typing import ClassVar, Optional

from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.models import InfoData


class Info:
    """Class that represents a info object in the API."""

    path: ClassVar[str] = "info"

    def __init__(self, auth: Auth) -> None:
        """Initialize an info object."""
        self._auth = auth
        self._data = None

    @property
    def data(self) -> Optional[InfoData]:
        """Return the raw info data."""
        return self._data

    @property
    def name(self) -> Optional[str]:
        """Return the name of the API interface."""
        if self.data:
            return self.data.name
        return None

    @property
    def version(self) -> Optional[str]:
        """Return the software version of the API interface."""
        if self.data:
            return self.data.version
        return None

    @property
    def serial_number(self) -> Optional[int]:
        """Return the serial number of the API interface."""
        if self.data:
            return self.data.device.serial
        return None

    async def async_update(self) -> None:
        response = await self._auth.get(self.path)
        self._data = InfoData.model_validate(await response.json())
