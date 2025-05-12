import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, PLATFORMS, CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .api import IntexSWGApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_HOST]
    interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    client = IntexSWGApiClient(host=host, session=hass.helpers.aiohttp_client.async_get_clientsession())

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}-{entry.entry_id}",
        update_method=client.async_update,
        update_interval=timedelta(seconds=interval),
    )
    # Erste Datenabfrage
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok