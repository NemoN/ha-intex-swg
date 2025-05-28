from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .const import (
    CONF_HOST, 
    CONF_PORT, 
    CONF_SCAN_INTERVAL,
    CONF_REBOOT_ENABLED, 
    CONF_REBOOT_INTERVAL,
    CONF_POWER_ENTITY, 
    DEFAULT_PORT, 
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_POWER_ENTITY,
    DEFAULT_REBOOT_ENABLED, 
    DEFAULT_REBOOT_INTERVAL,
    DOMAIN,
) # pylint:disable=unused-import

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        vol.Optional(CONF_REBOOT_ENABLED, default=DEFAULT_REBOOT_ENABLED): cv.boolean,
        vol.Optional(CONF_REBOOT_INTERVAL, default=DEFAULT_REBOOT_INTERVAL): cv.positive_int,
        vol.Optional(CONF_POWER_ENTITY, default=None): vol.Any(
            None,
            selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                    device_class=["power"],
                )
            )
        )
    }
)

_LOGGER = logging.getLogger(__name__)

class IntexSWGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow."""
        return OptionsFlowHandler(config_entry)    

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors = {}
        
        if user_input is not None:
            data = {
                CONF_HOST: user_input.get(CONF_HOST),
                CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT)
            }

            return self.async_create_entry(
                title=f"{data[CONF_HOST]}:{data[CONF_PORT]}",
                data=data
            )

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Init object."""
        self.entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:          
            return self.async_create_entry(title="", data=user_input)

        host = self.entry.options.get(CONF_HOST, self.entry.data[CONF_HOST])
        port = self.entry.options.get(CONF_PORT, self.entry.data[CONF_PORT])
        scan_int = self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        reboot =  self.entry.options.get(CONF_REBOOT_ENABLED, True)
        reboot_int = self.entry.options.get(CONF_REBOOT_INTERVAL, DEFAULT_REBOOT_INTERVAL)
        power = self.entry.options.get(CONF_POWER_ENTITY, DEFAULT_POWER_ENTITY)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA,
                {
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_SCAN_INTERVAL: scan_int,
                    CONF_REBOOT_ENABLED: reboot,
                    CONF_REBOOT_INTERVAL: reboot_int,
                    CONF_POWER_ENTITY: power,
                },
            ),
        )