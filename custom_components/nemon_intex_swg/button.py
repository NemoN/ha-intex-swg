import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]
    async_add_entities([IntexSWGRebootButton(client, coordinator)])

class IntexSWGRebootButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, client, coordinator):
        super().__init__(coordinator)

        self._client = client
        self._attr_name = "Reboot ESP32"
        self._attr_unique_id = f"{coordinator.name}_reboot"

    async def async_press(self) -> None:
        url = f"http://{self._client._host}:{self._client._port}/api/v1/intex/swg/reboot"
        payload = {"data": {"reboot": "yes"}}
        _LOGGER.debug("POST reboot: URL=%s, payload=%s", url, payload)

        try:
            await self._client._session.post(url, json=payload)
        except Exception as err:
            # _LOGGER.error("Error on reboot command: %s", err)
            pass
        
        # Schedule a refresh after 60 seconds
        def _refresh_cb(_):
            self.hass.async_create_task(self.coordinator.async_request_refresh())
        async_call_later(self.hass, 60, _refresh_cb)
