# Lunatone REST API Client

`lunatone-rest-api-client` is a Python package providing access to the Lunatone REST API.

It includes async clients for Lunatones REST API endpoints.

The following devices are supported:

- [DALI-2 IoT Gateway (v1.14.1 or later)](https://www.lunatone.com/produkt/dali-2-iot-gateway/)
- [DALI-2 IoT4 Gateway (v1.14.1 or later)](https://www.lunatone.com/produkt/dali-2-iot4-gateway/)
- [DALI-2 Display 4'' (v1.14.1 or later)](https://www.lunatone.com/produkt/dali-2-display-4/)
- [DALI-2 Display 7'' (v1.14.1 or later)](https://www.lunatone.com/produkt/dali-2-display-7/)

## Installation

Use `pip` to install the latest stable version of `lunatone-rest-api-client`
```bash
pip install --upgrade lunatone-rest-api-client
```

The current development version is available on [GitLab.com]
(https://gitlab.com/lunatone-public/lunatone-rest-api-client) and can be
installed directly from the git repository:

```bash
pip install git+https://gitlab.com/lunatone-public/lunatone-rest-api-client.git
```

## Usage

```python
import asyncio

import aiohttp

from lunatone_rest_api_client import Auth, Devices


async def main() -> None:
    """Show example of fetching devices."""
    async with aiohttp.ClientSession() as session:
        auth = Auth(session, "http://10.0.0.31")
        devices = Devices(auth)
        await devices.async_update()
        print(devices.data)


if __name__ == "__main__":
    asyncio.run(main())
```

## Setting up development environment

This Python project is fully managed using the uv dependency manager.

### Requirements:

- uv (See https://docs.astral.sh/uv/getting-started/installation/)

To install all packages, including all development requirements:

```bash
uv sync
```

To run just the Python tests:

```bash
uv run pytest
```

## Scripts

### API tests:

This script sends a `POST` request and right after two `GET` requests to check if the status is changed immediately.

```bash
uv run ./scripts/api_tests.py --ip <ip-address>
```
