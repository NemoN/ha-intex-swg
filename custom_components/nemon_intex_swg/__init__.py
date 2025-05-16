import logging

from datetime import timedelta, datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN, PLATFORMS,
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL,
    CONF_REBOOT_ENABLED, CONF_REBOOT_INTERVAL,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL,
    DEFAULT_REBOOT_ENABLED, DEFAULT_REBOOT_INTERVAL,
)
from .api import IntexSWGApiClient

_LOGGER = logging.getLogger(__name__)


async def _async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry to apply updated options (host/port or reboot)."""
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
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    reboot_enabled = entry.options.get(
        CONF_REBOOT_ENABLED,
        entry.data.get(CONF_REBOOT_ENABLED, DEFAULT_REBOOT_ENABLED),
    )
    reboot_interval = entry.options.get(
        CONF_REBOOT_INTERVAL,
        entry.data.get(CONF_REBOOT_INTERVAL, DEFAULT_REBOOT_INTERVAL),
    )

    client = IntexSWGApiClient(
        host=host,
        port=port,
        session=async_get_clientsession(hass),
    )
    coordinator = DataUpdateCoordinator(
        hass, _LOGGER,
        name=f"{DOMAIN}-{entry.entry_id}",
        update_method=client.async_update,
        update_interval=timedelta(seconds=scan_interval),
    )
    await coordinator.async_config_entry_first_refresh()

    # store client and coordinator
    hass.data.setdefault(DOMAIN, {})
    entry_data = hass.data[DOMAIN].setdefault(entry.entry_id, {})
    entry_data["client"] = client
    entry_data["coordinator"] = coordinator

    # remember flag on client for debug-logs
    client._reboot_enabled = reboot_enabled

    # scheduling logic: async_track_time_interval returns an unsubscribe function
    unsubscribe = entry_data.get("reboot_unsub")

    if reboot_enabled and not unsubscribe:
        _LOGGER.debug("Restart enabled every %s minutes", reboot_interval)
        client._next_reboot_time = datetime.now() + timedelta(minutes=reboot_interval)

        async def _reboot_interval(now):
            _LOGGER.debug("Starting reboot now")
            try:
                await client.async_reboot()
            except Exception as err:
                _LOGGER.error("Error during reboot: %s", err)
            client._next_reboot_time = datetime.now() + timedelta(minutes=reboot_interval)

        # schedule and keep the unsubscribe callback
        entry_data["reboot_unsub"] = async_track_time_interval(
            hass, _reboot_interval, timedelta(minutes=reboot_interval)
        )

    elif not reboot_enabled and unsubscribe:
        _LOGGER.debug("Restart scheduling disabled, removing existing schedule")
        unsubscribe()
        entry_data.pop("reboot_unsub")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # reload on any option change
    entry.add_update_listener(_async_update_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove any existing reboot schedule before unloading platforms."""
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data:
        unsubscribe = entry_data.get("reboot_unsub")
        if unsubscribe:
            _LOGGER.debug("Unloading entry: cancelling reboot schedule")
            unsubscribe()

    ok = True
    for platform in PLATFORMS:
        res = await hass.config_entries.async_forward_entry_unload(entry, platform)
        ok = ok and res

    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return ok
