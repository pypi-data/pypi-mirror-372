from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.models import SensorData, SensorsData

_PATH = "sensors"


class Sensor:
    """Class that represents a Sensor object in the API."""

    base_path: str = _PATH

    def __init__(self, auth: Auth, data: SensorData) -> None:
        """Initialize a Sensor object."""
        self._auth = auth
        self._data = data

    @property
    def path(self) -> str:
        return f"{self.base_path}/{self.id}"

    @property
    def data(self) -> SensorData:
        """Return the raw sensor data."""
        return self._data

    @property
    def id(self) -> int:
        """Return the ID of the zone."""
        return self.data.id

    @property
    def name(self) -> str:
        """Return the name of the zone."""
        return self.data.name

    async def async_update(self) -> None:
        response = await self._auth.get(self.path)
        self._data = SensorData.model_validate(await response.json())

    async def async_refresh(self) -> None:
        response = await self._auth.post(self.path)
        self._data = SensorData.model_validate(await response.json())


class Sensors:
    """Class that represents a Sensors object in the API."""

    path: str = _PATH
    _data: SensorsData = None

    def __init__(self, auth: Auth) -> None:
        """Initialize a Sensors object."""
        self._auth = auth

    @property
    def data(self) -> SensorsData:
        """Return the raw sensors data."""
        return self._data

    @property
    def sensors(self) -> list[Sensor]:
        if self.data:
            return [Sensor(self._auth, sensor) for sensor in self.data.sensors]
        return []

    async def async_update(self) -> None:
        response = await self._auth.get(self.path)
        self._data = SensorsData.model_validate(await response.json())

    async def async_refresh(self) -> None:
        response = await self._auth.post(self.path)
        self._data = SensorsData.model_validate(await response.json())
