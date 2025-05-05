"""Initialize SZÉP Card balance sensor integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

async def async_setup_entry(hass, entry):
    """Set up SZEP Card Sensor from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass, entry):
    """Unload SZEP Card Sensor config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
