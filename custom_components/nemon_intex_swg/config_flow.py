import voluptuous as vol

from homeassistant import config_entries
from .const import (
    DOMAIN, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL,
    CONF_REBOOT_ENABLED, CONF_REBOOT_INTERVAL,
    DEFAULT_PORT, DEFAULT_SCAN_INTERVAL,
    DEFAULT_REBOOT_ENABLED, DEFAULT_REBOOT_INTERVAL,
)

class IntexSWGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input:
            options = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input.get(CONF_PORT, DEFAULT_PORT),
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                CONF_REBOOT_ENABLED: user_input.get(CONF_REBOOT_ENABLED, DEFAULT_REBOOT_ENABLED),
                CONF_REBOOT_INTERVAL: user_input.get(CONF_REBOOT_INTERVAL, DEFAULT_REBOOT_INTERVAL),
            }
            return self.async_create_entry(
                title=f"{options[CONF_HOST]}:{options[CONF_PORT]}",
                data=options,
                options=options,
            )

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            vol.Optional(CONF_REBOOT_ENABLED, default=DEFAULT_REBOOT_ENABLED): bool,
            vol.Optional(CONF_REBOOT_INTERVAL, default=DEFAULT_REBOOT_INTERVAL): int,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(entry):
        return OptionsFlowHandler(entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    # def __init__(self, config_entry):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        # self.config_entry = config_entry
        super().__init__()

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)
        current = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_HOST, default=current.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=current.get(CONF_PORT, DEFAULT_PORT)): int,
            vol.Required(CONF_SCAN_INTERVAL, default=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
            vol.Required(CONF_REBOOT_ENABLED, default=current.get(CONF_REBOOT_ENABLED, DEFAULT_REBOOT_ENABLED)): bool,
            vol.Required(CONF_REBOOT_INTERVAL, default=current.get(CONF_REBOOT_INTERVAL, DEFAULT_REBOOT_INTERVAL)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema)