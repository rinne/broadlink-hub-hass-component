import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SSL

class BroadlinkHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Broadlink Hub config flow"""
    VERSION = 1
    CONNECTION_CLASS = 'local_poll'
    async def async_step_user(self, user_input):
        errors = {}
        if user_input is not None:
            if user_input[CONF_PORT] < 1 or user_input[CONF_PORT] > 65535:
                errors["base"] = 'invalid_port'
            elif len(user_input[CONF_HOST]) < 1:
                errors["base"] = 'invalid_host'
            elif user_input[CONF_USERNAME] == '':
                errors["base"] = 'missing_username'
            elif user_input[CONF_PASSWORD] == '':
                errors["base"] = 'missing_password'
            else:
                self.config = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_SSL: user_input[CONF_SSL],
                }
                return self.async_create_entry(
                    title="Broadlink Hub: "+user_input[CONF_HOST]+':'+str(user_input.get(CONF_PORT)),
                    data=self.config,
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({ vol.Required(CONF_HOST): str,
                                     vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                                     vol.Required(CONF_USERNAME): str,
                                     vol.Required(CONF_PASSWORD): str,
                                     vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
            }),
            errors=errors,
        )
