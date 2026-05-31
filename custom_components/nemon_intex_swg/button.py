import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    DEVICE_NAME,
    DEVICE_MANUFACTURER,
    DEVICE_MODEL    
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data["coordinator"]
    
    async_add_entities([
        IntexSWGRebootButton(client, coordinator, entry),
        IntexSWGPowerOnButton(client, coordinator, entry),
        IntexSWGPowerOffButton(client, coordinator, entry),
        IntexSWGPowerStandbyButton(client, coordinator, entry),
    ])

class IntexSWGRebootButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, client, coordinator, entry):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Reboot ESP32"
        self._attr_unique_id = f"{coordinator.name}_reboot"
        self._attr_icon = "mdi:restart"

        # device_info
        host = entry.data.get(CONF_HOST)
        port = entry.data.get(CONF_PORT)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEVICE_NAME} ({host}:{port})",
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "connections": {("ip", host)}
        }

    async def async_press(self) -> None:
        _LOGGER.debug("Reboot button pressed")
        await self._client.async_reboot()

        # Schedule a refresh after 60 seconds
        def _refresh_cb(_):
            self.hass.async_create_task(self.coordinator.async_request_refresh())
        async_call_later(self.hass, 60, _refresh_cb)

class IntexSWGPowerOnButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, client, coordinator, entry):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Power ON"
        self._attr_unique_id = f"{coordinator.name}_power_on"

        # Device info for the dashboard
        host = entry.data.get(CONF_HOST)
        port = entry.data.get(CONF_PORT)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEVICE_NAME} ({host}:{port})",
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "connections": {("ip", host)},
        }

    @property
    def icon(self) -> str:
        """Return a solid power icon if status == 'ON', else outline."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return "mdi:radiobox-marked" if current_power == "ON" else "mdi:radiobox-blank"

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        """Provide an 'active' attribute for Lovelace usage."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return {"active": current_power == "ON"}
    
    async def async_press(self) -> None:
        await self._client.async_set_power("on")

        # Schedule a brief refresh so the UI reflects the new state
        async def _refresh_cb(_):
            self.hass.async_create_task(self.coordinator.async_request_refresh())

        async_call_later(self.hass, 0.1, _refresh_cb)

class IntexSWGPowerOffButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, client, coordinator, entry):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Power OFF"
        self._attr_unique_id = f"{coordinator.name}_power_off"

        # Device info for the dashboard
        host = entry.data.get(CONF_HOST)
        port = entry.data.get(CONF_PORT)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEVICE_NAME} ({host}:{port})",
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "connections": {("ip", host)},
        }

    @property
    def icon(self) -> str:
        """Return a solid power-off icon if status == 'OFF', else outline."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return "mdi:radiobox-marked" if current_power == "OFF" else "mdi:radiobox-blank"

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        """Provide an 'active' attribute for Lovelace usage."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return {"active": current_power == "OFF"}

    async def async_press(self) -> None:
        await self._client.async_set_power("off")

        # Schedule a brief refresh so the UI reflects the new state
        async def _refresh_cb(_):
            self.hass.async_create_task(self.coordinator.async_request_refresh())

        async_call_later(self.hass, 0.1, _refresh_cb)

class IntexSWGPowerStandbyButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, client, coordinator, entry):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Power STANDBY"
        self._attr_unique_id = f"{coordinator.name}_power_standby"

        # Device info for the dashboard
        host = entry.data.get(CONF_HOST)
        port = entry.data.get(CONF_PORT)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"{DEVICE_NAME} ({host}:{port})",
            "manufacturer": DEVICE_MANUFACTURER,
            "model": DEVICE_MODEL,
            "connections": {("ip", host)},
        }

    @property
    def icon(self) -> str:
        """Return a solid power-sleep icon if status == 'STANDBY', else outline."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return "mdi:radiobox-marked" if current_power == "STANDBY" else "mdi:radiobox-blank"

    @property
    def extra_state_attributes(self) -> dict[str, bool]:
        """Provide an 'active' attribute for Lovelace usage."""
        current_power = self._client.data.get("status", {}).get("power", "")
        return {"active": current_power == "STANDBY"}

    async def async_press(self) -> None:
        await self._client.async_set_power("standby")

        # Schedule a brief refresh so the UI reflects the new state
        async def _refresh_cb(_):
            self.hass.async_create_task(self.coordinator.async_request_refresh())

        async_call_later(self.hass, 0.1, _refresh_cb)