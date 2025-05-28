import logging
import aiohttp

from datetime import datetime

from homeassistant.helpers.update_coordinator import UpdateFailed

_LOGGER = logging.getLogger(__name__)

class IntexSWGApiClient:
    def __init__(self, host: str, port: int, session: aiohttp.ClientSession, hass=None, power_entity_id=None) -> None:
        self._host = host
        self._port = port
        self._session = session
        self._hass = hass
        self._power_entity_id = power_entity_id
        self.data: dict = {}        

    async def async_update(self) -> None:
        url = f"http://{self._host}:{self._port}/api/v1/intex/swg/status"

        try:
            response = await self._session.get(url)
            response.raise_for_status()
            result = await response.json()
            self.data = result.get("data", {})

            # Debug: time remaining until next reboot (only if reboot is enabled)
            if getattr(self, "_reboot_enabled", False):
                next_rb = getattr(self, "_next_reboot_time", None)
                if next_rb:
                    delta = next_rb - datetime.now()
                    _LOGGER.debug("Time until next reboot: %s", delta)

            # Opt: if a power sensor was configured, read its current state and store it
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
            raise UpdateFailed(f"Error connecting to {self._host}:{self._port}: {err}")
        except ValueError as err:
            _LOGGER.error("Error parsing JSON: %s", err)
            raise UpdateFailed(f"Invalid JSON response: {err}")
        
        return self.data

    async def async_reboot(self) -> None:
        url = f"http://{self._host}:{self._port}/api/v1/intex/swg/reboot"

        payload = {"data": {"reboot": "yes"}}
        _LOGGER.debug("POST interval reboot: URL=%s, payload=%s", url, payload)

        try:
            await self._session.post(url, json=payload)
        except aiohttp.ClientError as err:
            # _LOGGER.error("Error sending reboot command: %s", err)
            pass
        except Exception as err:
            _LOGGER.error("Unexpected error sending reboot command: %s", err)