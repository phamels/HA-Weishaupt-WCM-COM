"""Weishaupt WCM-COM."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.discovery import load_platform

from .const import DOMAIN
import logging
from homeassistant.core import HomeAssistant
from datetime import timedelta
from . import heat_exchanger
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle


from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)

WEISHAUPT_PLATFORMS = ['sensor']
scan_interval = timedelta(seconds=20)


CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

def setup(hass: HomeAssistant, config):
    """Your controller/hub specific code."""
    # Data that you want to share with your platforms

    host = config[DOMAIN][CONF_HOST]
    username = config[DOMAIN][CONF_USERNAME]
    passwort = config[DOMAIN][CONF_PASSWORD]

    api = WeishauptAPI(host, username, passwort)

    hass.data[DOMAIN] = api

    load_platform(hass,'sensor', DOMAIN, {}, config)

    return True


class WeishauptBaseEntity(SensorEntity):
    def __init__(self, hass, config):
        self._api = hass.data[DOMAIN]
        
    def api(self):
        return self._api


    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.debug("Super Updating")
        self._api.update()

    async def async_added_to_hass(self) -> None:
        """Callback when entity is registered in HA"""
        await super().async_added_to_hass()

        _LOGGER.debug(
            "    Added %s from WCM-COM",
            self.entity_id
        )


class WeishauptAPI:

    SCAN_INTERVAL = timedelta(seconds=30)

    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password
        self._data = {}

    def getData(self):
        _LOGGER.debug("Getting WCM-COM Data: %s", self._data)
        return self._data

    # The actual fetch of information, since the wcm-com module can only handle one connection at a time, this has to be throttled
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        result = heat_exchanger.process_values(self._host, self._username, self._password)
        _LOGGER.debug("Fetching new WCM-COM data")
        if result != None:
            self._data = json.loads(result)
        else:
            _LOGGER.warning("Cannot Update WCM-COM Data")
    
