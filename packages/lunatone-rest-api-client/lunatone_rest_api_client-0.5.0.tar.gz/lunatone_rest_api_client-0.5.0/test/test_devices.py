import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, Device, Devices
from lunatone_rest_api_client.models import (
    DeviceData,
    DevicesData,
    DeviceUpdateData,
)

from .common import DEVICES_DATA_RAW


@pytest.fixture
def devices_data() -> DevicesData:
    return DevicesData.model_validate(DEVICES_DATA_RAW)


@pytest.fixture
def device_data(devices_data: DevicesData) -> DeviceData:
    for d in devices_data.devices:
        d.time_signature = devices_data.time_signature
        return d


@pytest.mark.asyncio
async def test_devices_update(
    aioresponses: aioresponses, base_url: str, devices_data: DevicesData
) -> None:
    json_data = devices_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Devices.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        devices = Devices(Auth(session, base_url))
        await devices.async_update()
        assert devices.data == devices_data


@pytest.mark.asyncio
async def test_device_update(
    aioresponses: aioresponses, base_url: str, device_data: DevicesData
) -> None:
    json_data = device_data.model_dump(by_alias=True)
    aioresponses.get(
        f"{base_url}/{Device.base_path}/{device_data.id}", payload=json_data
    )

    async with aiohttp.ClientSession() as session:
        device = Device(Auth(session, base_url), DeviceData(id=device_data.id))
        await device.async_update()
        assert device.data == device_data


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, groups",
    [
        ("Test Device 1 (Updated)", [0, 3, 6, 8]),
        ("Test Device 2 (Updated)", [2, 5, 9, 15]),
    ],
)
async def test_device_update_without_changes(
    aioresponses: aioresponses,
    base_url: str,
    device_data: DeviceData,
    name: str,
    groups: list[int],
) -> None:
    old_name = device_data.name
    old_groups = device_data.groups
    device_data.name = name
    device_data.groups = groups
    json_data = device_data.model_dump(by_alias=True)
    aioresponses.put(
        f"{base_url}/{Device.base_path}/{device_data.id}", payload=json_data
    )

    async with aiohttp.ClientSession() as session:
        device_data.name = old_name
        device_data.groups = old_groups
        device = Device(Auth(session, base_url), device_data)
        await device.async_update(DeviceUpdateData(name=name, groups=groups))
        assert device.data.name == name
        assert device.data.groups == groups
