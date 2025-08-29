import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, DALIBroadcast, DALIGroup, DALIScan
from lunatone_rest_api_client.models import (
    ControlData,
    ScanData,
    ScanState,
    StartScanData,
)


@pytest.fixture
def dali_scan_data_init() -> ScanData:
    return ScanData()


@pytest.mark.asyncio
async def test_scan_update(
    aioresponses: aioresponses, base_url: str, dali_scan_data_init: ScanData
) -> None:
    expected_scan_data = ScanData(
        id="2bcdf829-2770-4a98-b1c7-b1ca4bac408f",
        progress=100,
        found=0,
        foundSensors=0,
        status=ScanState.DONE,
    )

    aioresponses.get(
        f"{base_url}/{DALIScan.path}",
        payload=dali_scan_data_init.model_dump(by_alias=True),
    )
    aioresponses.get(
        f"{base_url}/{DALIScan.path}",
        payload=expected_scan_data.model_dump(by_alias=True),
    )

    async with aiohttp.ClientSession() as session:
        scan = DALIScan(Auth(session, base_url))

        await scan.async_update()
        assert scan.data == dali_scan_data_init

        await scan.async_update()
        assert scan.data == expected_scan_data


@pytest.mark.asyncio
async def test_scan_start(
    aioresponses: aioresponses, base_url: str, dali_scan_data_init: ScanData
) -> None:
    expected_scan_data = ScanData(
        id="2bcdf829-2770-4a98-b1c7-b1ca4bac408f",
        progress=0,
        found=0,
        foundSensors=0,
        status=ScanState.NOT_STARTED,
    )

    aioresponses.get(
        f"{base_url}/{DALIScan.path}",
        payload=dali_scan_data_init.model_dump(by_alias=True),
    )
    aioresponses.post(
        f"{base_url}/{DALIScan.path}",
        payload=expected_scan_data.model_dump(by_alias=True),
    )

    async with aiohttp.ClientSession() as session:
        scan = DALIScan(Auth(session, base_url))

        await scan.async_update()
        assert scan.data == dali_scan_data_init

        await scan.async_start(
            StartScanData(newInstallation=False, noAddressing=False, useLines=[])
        )
        assert scan.data == expected_scan_data


@pytest.mark.asyncio
async def test_scan_cancel(
    aioresponses: aioresponses, base_url: str, dali_scan_data_init: ScanData
) -> None:
    expected_scan_data = ScanData(
        id="2bcdf829-2770-4a98-b1c7-b1ca4bac408f",
        progress=0,
        found=0,
        foundSensors=0,
        status=ScanState.CANCELLED,
    )

    aioresponses.get(
        f"{base_url}/{DALIScan.path}",
        payload=dali_scan_data_init.model_dump(by_alias=True),
    )
    aioresponses.post(
        f"{base_url}/{DALIScan.path}/cancel",
        payload=expected_scan_data.model_dump(by_alias=True),
    )

    async with aiohttp.ClientSession() as session:
        scan = DALIScan(Auth(session, base_url))

        await scan.async_update()
        assert scan.data == dali_scan_data_init

        await scan.async_cancel()
        assert scan.data == expected_scan_data


@pytest.mark.asyncio
async def test_control_broadcast(aioresponses: aioresponses, base_url: str) -> None:
    aioresponses.post(
        f"{base_url}/broadcast/control",
        status=204,
    )

    async with aiohttp.ClientSession() as session:
        dali_control = DALIBroadcast(Auth(session, base_url))

        try:
            await dali_control.async_control(ControlData(switchable=True))
        except aiohttp.ClientError:
            assert False


@pytest.mark.asyncio
async def test_control_broadcast_should_throw_error(
    aioresponses: aioresponses, base_url: str
) -> None:
    aioresponses.post(
        f"{base_url}/{DALIBroadcast.path}/control",
        status=500,
    )

    async with aiohttp.ClientSession() as session:
        dali_control = DALIBroadcast(Auth(session, base_url))

        with pytest.raises(aiohttp.ClientResponseError):
            await dali_control.async_control(ControlData(switchable=True))


@pytest.mark.asyncio
@pytest.mark.parametrize("group_number", list(range(16)))
async def test_control_group(
    aioresponses: aioresponses, base_url: str, group_number: int
) -> None:
    aioresponses.post(
        f"{base_url}/{DALIGroup.path}/{group_number}/control",
        status=204,
    )

    async with aiohttp.ClientSession() as session:
        dali_control = DALIGroup(Auth(session, base_url), group_number)

        try:
            await dali_control.async_control(ControlData(switchable=True))
        except aiohttp.ClientError:
            assert False


@pytest.mark.asyncio
@pytest.mark.parametrize("group_number", list(range(16)))
async def test_control_group_should_throw_error(
    aioresponses: aioresponses, base_url: str, group_number: int
) -> None:
    aioresponses.post(
        f"{base_url}/{DALIGroup.path}/{group_number}/control",
        status=500,
    )

    async with aiohttp.ClientSession() as session:
        dali_control = DALIGroup(Auth(session, base_url), group_number)

        with pytest.raises(aiohttp.ClientResponseError):
            await dali_control.async_control(ControlData(switchable=True))
