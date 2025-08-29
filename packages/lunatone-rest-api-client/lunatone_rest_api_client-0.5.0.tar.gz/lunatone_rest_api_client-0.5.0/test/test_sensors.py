import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, Sensor, Sensors
from lunatone_rest_api_client.models import SensorData, SensorsData

from .common import SENSORS_DATA_RAW


@pytest.fixture
def sensors_data() -> SensorsData:
    return SensorsData.model_validate(SENSORS_DATA_RAW)


@pytest.fixture
def sensor_data(sensors_data: SensorsData) -> SensorData:
    for sensor in sensors_data.sensors:
        return sensor


@pytest.mark.asyncio
async def test_sensors_update(
    aioresponses: aioresponses, base_url: str, sensors_data: SensorsData
) -> None:
    json_data = sensors_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Sensors.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        sensors = Sensors(Auth(session, base_url))
        await sensors.async_update()
        assert sensors.data == sensors_data


@pytest.mark.asyncio
async def test_sensor_update(
    aioresponses: aioresponses, base_url: str, sensor_data: SensorData
) -> None:
    json_data = sensor_data.model_dump(by_alias=True)
    aioresponses.get(
        f"{base_url}/{Sensor.base_path}/{sensor_data.id}", payload=json_data
    )

    async with aiohttp.ClientSession() as session:
        sensors = Sensor(Auth(session, base_url), SensorData(id=sensor_data.id))
        await sensors.async_update()
        assert sensors.data == sensor_data
