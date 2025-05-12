import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

class IntexSWGApiClient:
    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._session = session
        self.data = {}

    async def async_update(self) -> None:
        try:
            url = f"http://{self._host}/api/v1/intex/swg/status"
            response = await self._session.get(url)
            result = await response.json()
            # Nur der eigentliche Datenblock
            self.data = result.get("data", {})
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data: %s", err)