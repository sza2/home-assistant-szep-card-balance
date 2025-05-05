"""Config flow for SZÉP Card balance sensor."""
from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import (
    DOMAIN,
    CONF_CARD_NUMBER,
    CONF_CARD_CODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

class SzepCardSensorConfigFlow(config_entries.ConfigFlow, domain = DOMAIN):
    """Handle a config flow for SZÉP Card balance sensor."""

    VERSION = 1

    async def async_step_user(self, user_input = None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title = user_input["name"],
                data = {
                    CONF_CARD_NUMBER: user_input[CONF_CARD_NUMBER],
                    CONF_CARD_CODE: user_input[CONF_CARD_CODE],
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                },
            )

        return self.async_show_form(
            step_id = "user",
            data_schema = vol.Schema({
                vol.Required("name"): str,
                vol.Required(CONF_CARD_NUMBER): vol.All(cv.string, vol.Length(min = 8, max = 8)),
                vol.Required(CONF_CARD_CODE): vol.All(cv.string, vol.Length(min = 3, max = 3)),
                vol.Required(CONF_SCAN_INTERVAL, default = DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }),
        )
