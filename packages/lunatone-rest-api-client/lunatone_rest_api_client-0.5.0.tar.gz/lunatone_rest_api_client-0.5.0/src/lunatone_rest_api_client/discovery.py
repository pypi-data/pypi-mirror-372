"""Discovery module for Lunatone interfaces."""

import asyncio
from dataclasses import dataclass
from enum import StrEnum
import json
import socket
from typing import Any, Final

DISCOVERY_ADDRESS: Final[str] = "255.255.255.255"
DISCOVERY_PORT: Final[int] = 5555
DISCOVERY_MESSAGE: Final[str] = "discovery"
DISCOVERY_LISTEN_TIMEOUT_SECONDS: Final[float] = 3.0


class DiscoveryTypes(StrEnum):
    """DiscoveryTypes."""

    DALI2_IOT = "dali-2-iot"
    DALI2_IOT4 = "dali-2-iot4"
    DALI2_DISPLAY = "dali-2-display"


@dataclass
class LunatoneDiscoveryInfo:
    """LunatoneDiscoveryInfo."""

    host: str
    name: str


class LunatoneUDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol implementation for discovering Lunatone interfaces."""

    def __init__(self) -> None:
        """Initialize the UDP protocol instance."""
        super().__init__()
        self.interfaces: list[LunatoneDiscoveryInfo] = []

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        """Handle an incoming UDP datagram."""
        try:
            message = json.loads(data.decode())
        except json.JSONDecodeError:
            return
        if not ("type" in message and "name" in message):  # Validate message
            return
        if message["type"] in DiscoveryTypes:
            self.interfaces.append(LunatoneDiscoveryInfo(addr[0], message["name"]))


async def async_discover_devices(
    loop: asyncio.AbstractEventLoop, timeout: float = DISCOVERY_LISTEN_TIMEOUT_SECONDS
) -> list[LunatoneDiscoveryInfo]:
    """Return discovered interfaces."""
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: LunatoneUDPProtocol(),  # pylint: disable=unnecessary-lambda
        local_addr=("0.0.0.0", DISCOVERY_PORT),
        family=socket.AF_INET,
        allow_broadcast=True,
    )

    try:
        transport.sendto(
            DISCOVERY_MESSAGE.encode(), (DISCOVERY_ADDRESS, DISCOVERY_PORT)
        )
        await asyncio.sleep(timeout)
    finally:
        transport.close()

    return protocol.interfaces
