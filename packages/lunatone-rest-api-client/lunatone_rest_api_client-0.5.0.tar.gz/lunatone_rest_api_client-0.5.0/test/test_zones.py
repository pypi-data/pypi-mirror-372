import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, Zone, Zones
from lunatone_rest_api_client.models import ZoneData, ZonesData

from .common import ZONES_DATA_RAW


@pytest.fixture
def zones_data() -> ZonesData:
    return ZonesData.model_validate(ZONES_DATA_RAW)


@pytest.fixture
def zone_data(zones_data: ZonesData) -> ZoneData:
    for zone_data in zones_data.zones:
        return zone_data


@pytest.mark.asyncio
async def test_zones_update(
    aioresponses: aioresponses, base_url: str, zones_data: ZonesData
) -> None:
    json_data = zones_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Zones.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        zones = Zones(Auth(session, base_url))
        await zones.async_update()
        assert zones.data == zones_data


@pytest.mark.asyncio
async def test_zone_update(
    aioresponses: aioresponses, base_url: str, zone_data: ZoneData
) -> None:
    json_data = zone_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Zone.base_path}/{zone_data.id}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        zones = Zone(Auth(session, base_url), ZoneData(id=zone_data.id))
        await zones.async_update()
        assert zones.data == zone_data
