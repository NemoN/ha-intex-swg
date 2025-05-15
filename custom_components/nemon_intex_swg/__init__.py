import logging

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN, PLATFORMS, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL,
    CONF_REBOOT_ENABLED, CONF_REBOOT_INTERVAL,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL,
    DEFAULT_REBOOT_ENABLED, DEFAULT_REBOOT_INTERVAL,
)
from .api import IntexSWGApiClient

_LOGGER = logging.getLogger(__name__)

async def _async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    port = entry.options.get(CONF_PORT, entry.data.get(CONF_PORT, DEFAULT_PORT))
    new_title = f"{host}:{port}"
    hass.config_entries.async_update_entry(entry, title=new_title)
    await hass.config_entries.async_reload(entry.entry_id)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    port = entry.options.get(CONF_PORT, entry.data.get(CONF_PORT, DEFAULT_PORT))
    interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    reboot_enabled = entry.options.get(CONF_REBOOT_ENABLED, entry.data.get(CONF_REBOOT_ENABLED, DEFAULT_REBOOT_ENABLED))
    reboot_interval = entry.options.get(CONF_REBOOT_INTERVAL, entry.data.get(CONF_REBOOT_INTERVAL, DEFAULT_REBOOT_INTERVAL))

    client = IntexSWGApiClient(
        host=host, port=port,
        session=async_get_clientsession(hass),
    )
    coordinator = DataUpdateCoordinator(
        hass, _LOGGER,
        name=f"{DOMAIN}-{entry.entry_id}",
        update_method=client.async_update,
        update_interval=timedelta(seconds=interval),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"client": client, "coordinator": coordinator}

    entry.add_update_listener(_async_update_entry)

    if reboot_enabled:
        _LOGGER.debug("Restart enabled: %s min", reboot_interval)
        async def _reboot_interval(now):
            _LOGGER.debug("Restart: execute async_reboot")
            try:
                await client.async_reboot()
            except Exception as err:
                _LOGGER.error("Error during restart: %s", err)
        async_track_time_interval(
            hass,
            _reboot_interval,
            timedelta(minutes=reboot_interval),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = True
    for platform in PLATFORMS:
        res = await hass.config_entries.async_forward_entry_unload(entry, platform)
        ok = ok and res
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok