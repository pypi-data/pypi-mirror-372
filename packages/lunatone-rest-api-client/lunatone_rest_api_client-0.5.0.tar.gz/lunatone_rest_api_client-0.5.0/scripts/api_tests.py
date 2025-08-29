import argparse
import asyncio

import aiohttp

from lunatone_rest_api_client import (
    Auth,
    Device,
    Devices,
)
from lunatone_rest_api_client.models import ControlData


parser = argparse.ArgumentParser(prog="API Test")
parser.add_argument("-i", "--ip", type=str, required=True,
                    help="Specify IP address of the device")
arguments = parser.parse_args()


async def test_consecutively_get_and_post_requests(auth: Auth):
    devices = Devices(auth)
    await devices.async_update() # Send GET request to /devices

    device: Device = devices.devices[0]

    # Send POST request with { "switchable": true } to /device/1/control
    await device.async_control(ControlData(switchable=True))
    await device.async_update() # Send GET request to /device/1
    print(f"request1: expected switchable=True, actual switchable={device.data.features.switchable}")
    await device.async_update() # Send GET request to /device/1
    print(f"request2: expected switchable=True, actual switchable={device.data.features.switchable}")

    # Send POST request with { "switchable": false } to /device/1/control
    await device.async_control(ControlData(switchable=False))
    await device.async_update() # Send GET request to /device/1
    print(f"request1: expected switchable=False, actual switchable={device.data.features.switchable}")
    await device.async_update() # Send GET request to /device/1
    print(f"request2: expected switchable=False, actual switchable={device.data.features.switchable}")


async def main():
    async with aiohttp.ClientSession() as session:
        auth = Auth(session, f"http://{arguments.ip}")

        await test_consecutively_get_and_post_requests(auth)


if __name__ == "__main__":
    asyncio.run(main())
