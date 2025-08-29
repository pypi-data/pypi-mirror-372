import aiohttp
import pytest
from aioresponses.core import aioresponses

from lunatone_rest_api_client import Auth, Info
from lunatone_rest_api_client.models import InfoData

from .common import INFO_DATA_RAW


@pytest.fixture
def info_data() -> InfoData:
    return InfoData.model_validate(INFO_DATA_RAW)


@pytest.mark.asyncio
async def test_info_update(
    aioresponses: aioresponses, base_url: str, info_data: InfoData
) -> None:
    json_data = info_data.model_dump(by_alias=True)
    aioresponses.get(f"{base_url}/{Info.path}", payload=json_data)

    async with aiohttp.ClientSession() as session:
        info = Info(Auth(session, base_url))
        await info.async_update()
        assert info.data == info_data
