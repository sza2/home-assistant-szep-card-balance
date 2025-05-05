"""SZÉP Card balance sensor platform."""
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import DiscoveryInfoType
from .scraper import TokenScraper
from .fetch import BalanceFetcher
from .const import (
    DOMAIN,
    CONF_CARD_NUMBER,
    CONF_CARD_CODE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_URL_HTML,
    DEFAULT_URL_API,
)

import logging

import random # remove, only for testing

_LOGGER = logging.getLogger(__name__)

BALANCE_TYPES = ["accommodation", "active_hungarians"]
BALANCE_TYPE_NAMES = {
    "accommodation": "Accommodation",
    "active_hungarians": "Active Hungarians",
}

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up SzepCardSensor from config entry."""
    name = entry.title
    card_number = entry.data.get(CONF_CARD_NUMBER)
    card_code = entry.data.get(CONF_CARD_CODE)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    _LOGGER.info(f"Setting up SzepCardSensor: {name} with value {card_number}")

    coordinator = SzepCardBalanceCoordinator(hass, name, card_number, card_code, scan_interval)

    sensors = [
        SzepCardBalanceSensor(coordinator, balance_type)
        for balance_type in BALANCE_TYPES
    ]
    async_add_entities(sensors)

class SzepCardBalanceCoordinator:
    """Handles shared balance fetching and storage."""

    def __init__(self, hass, name, card_number, card_code, scan_interval):
        self.hass = hass
        self.name = name
        self.balances = {}
        self._card_number = card_number
        self._card_code = card_code
        self._scan_interval = timedelta(seconds = scan_interval)
        self._unsub_interval = async_track_time_interval(
            self.hass, self._scheduled_update, self._scan_interval
        )

    async def _scheduled_update(self, now):
        """Run the update periodically."""
        _LOGGER.debug(f"[{self.name}] Triggering shared update for all balances")
        data = await self.hass.async_add_executor_job(self._blocking_fetch_all_balances)
        if data:
            self.balances = data

    def _blocking_fetch_all_balances(self):
        """Fetching all balances from card API."""
        scraper = TokenScraper(DEFAULT_URL_HTML)
        scraper.scrape()
        credentials = scraper.get_credentials()

        fetcher = BalanceFetcher(
            DEFAULT_URL_API,
            card_number=self._card_number,
            card_code=self._card_code,
            token=credentials['token'],
            session_id=credentials['session_id']
        )
        fetcher.fetch_balance()

        return {
            "accommodation": fetcher.accomodation,
            "active_hungarians": fetcher.active_hungarians,
        }

class SzepCardBalanceSensor(SensorEntity):
    """Representation of a SZÉP Card balance sensor."""

    _attr_should_poll = False
    _attr_icon = "mdi:credit-card"
    _attr_device_class = "monetary"
    _attr_state_class = "total"
    _attr_unit_of_measurement = "HUF"

    def __init__(self, coordinator: SzepCardBalanceCoordinator, balance_type: str):
        self.coordinator = coordinator
        self._balance_type = balance_type
        self._attr_name = f"{coordinator.name} - {BALANCE_TYPE_NAMES[balance_type]}"
        self._attr_unique_id = f"{coordinator.name}_{balance_type}"
        self._attr_native_value: Optional[int] = None

    async def async_added_to_hass(self):
        """Trigger state update when added."""
        self.async_on_remove(
            async_track_time_interval(
                self.hass, self._scheduled_update, self.coordinator._scan_interval
            )
        )

    async def _scheduled_update(self, _):
        """Read latest data from the shared coordinator."""
        value = self.coordinator.balances.get(self._balance_type)
        _LOGGER.debug(f"[{self.name}] Reading {self._balance_type}: {value}")
        if value is not None:
            self._attr_native_value = value
            self.async_write_ha_state()
