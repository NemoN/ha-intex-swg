import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]
    async_add_entities([IntexSWGPowerSelect(client, coordinator)])

class IntexSWGPowerSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, client, coordinator):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Power"
        self._attr_unique_id = f"{coordinator.name}_power"
        self._attr_options = ["ON", "OFF", "STANDBY"]

    @property
    def current_option(self):
        power = self._client.data.get("status", {}).get("power")
        return power.upper() if isinstance(power, str) else None

    async def async_select_option(self, option: str) -> None:
        if option not in self._attr_options:
            _LOGGER.debug("Invalid power option: %s", option)
            return
        url = f"http://{self._client._host}:{self._client._port}/api/v1/intex/swg"
        payload = {"data": {"power": option.lower()}}
        _LOGGER.debug("POST select Power: URL=%s, payload=%s", url, payload)
        
        await self._client._session.post(url, json=payload)
        await self.coordinator.async_request_refresh()