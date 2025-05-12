import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

class IntexSWGConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data={
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, description={"name": "Hostname/IP"}): str,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=DEFAULT_SCAN_INTERVAL,
                description={"name": "Scan Interval (s)"},
            ): int,
        })
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)