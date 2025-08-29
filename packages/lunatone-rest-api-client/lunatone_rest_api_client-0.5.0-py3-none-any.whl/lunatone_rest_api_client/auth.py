from aiohttp import ClientSession, ClientResponse


class Auth:
    """Class to make authenticated requests."""

    def __init__(
        self, session: ClientSession, base_url: str, access_token: str = None
    ) -> None:
        """Initialize the auth."""
        self._session = session
        self._base_url = base_url
        self._access_token = access_token

    async def request(self, method: str, path: str, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        if self._access_token:
            headers["authorization"] = self._access_token

        response = await self._session.request(
            method,
            f"{self._base_url}/{path}",
            **kwargs,
            headers=headers,
        )
        response.raise_for_status()
        return response

    async def get(self, path: str) -> ClientResponse:
        return await self.request("GET", path)

    async def put(self, path: str, **kwargs) -> ClientResponse:
        return await self.request("PUT", path, **kwargs)

    async def post(self, path: str, **kwargs) -> ClientResponse:
        return await self.request("POST", path, **kwargs)

    async def delete(self, path: str) -> ClientResponse:
        return await self.request("DELETE", path)
