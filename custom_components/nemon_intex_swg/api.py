import logging
import aiohttp

from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import UpdateFailed

_LOGGER = logging.getLogger(__name__)

class IntexSWGApiClient:
    def __init__(
        self,
        host: str,
        port: int,
        session: aiohttp.ClientSession,
        hass=None,
        power_entity_id=None,
    ) -> None:
        self._host = host
        self._port = port
        self._session = session
        self._hass = hass
        self._power_entity_id = power_entity_id
        self.data: dict = {}

        # Cache settings: cache duration and timestamp of last fetch
        self._cache_duration = timedelta(seconds=15)
        self._last_fetch: datetime | None = None

    async def async_update(self) -> dict:
        """Fetch data from the API, caching the result for 15 seconds."""
        now = datetime.now()

        # 1) Check if cached data is still valid
        if self._last_fetch and (now - self._last_fetch) < self._cache_duration:
            remaining = self._cache_duration - (now - self._last_fetch)
            _LOGGER.debug(
                "Using cached data from %s (remaining %s)",
                self._last_fetch,
                remaining,
            )
            return self.data

        # 2) Fetch fresh data from the API endpoint
        url = f"http://{self._host}:{self._port}/api/v1/intex/swg/status"
        try:
            response = await self._session.get(url)
            response.raise_for_status()
            result = await response.json()
            self.data = result.get("data", {})

            # Debug reboot timer if reboot feature is enabled
            if getattr(self, "_reboot_enabled", False):
                next_rb = getattr(self, "_next_reboot_time", None)
                if next_rb:
                    _LOGGER.debug("Time until next reboot: %s", next_rb - now)

            # Read external power sensor state if configured
            if self._power_entity_id and self._hass:
                state = self._hass.states.get(self._power_entity_id)
                try:
                    self.data["power"] = float(state.state)
                except Exception:
                    self.data["power"] = None

        except aiohttp.ClientResponseError as err:
            _LOGGER.error("HTTP error fetching data: %s", err)
            raise UpdateFailed(f"HTTP error: {err}")
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(
                f"Error connecting to {self._host}:{self._port}: {err}"
            )
        except ValueError as err:
            _LOGGER.error("Error parsing JSON: %s", err)
            raise UpdateFailed(f"Invalid JSON response: {err}")

        # 3) Update cache timestamp and return the data
        self._last_fetch = now
        return self.data

    async def async_reboot(self) -> None:
        """Send a reboot command to the device."""
        url = f"http://{self._host}:{self._port}/api/v1/intex/swg/reboot"
        payload = {"data": {"reboot": "yes"}}
        _LOGGER.debug("POST reboot command: URL=%s, payload=%s", url, payload)

        try:
            await self._session.post(url, json=payload)
        except aiohttp.ClientError:
            # Ignore errors from reboot attempts
            pass
        except Exception as err:
            _LOGGER.error("Unexpected error sending reboot command: %s", err)
