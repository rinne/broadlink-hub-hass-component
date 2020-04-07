"""Broadlink Hub sensors"""

import asyncio
import logging

from homeassistant.const import DEVICE_CLASS_POWER, POWER_WATT
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_NEW_SENSOR
from .entity import BroadlinkHubEntity
from .connector import connectorRelease

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, entry, async_add_entities):
    """Broadlink Hub sensor setup"""
    _LOGGER.info("Broadlink Hub Sensor Setup Entry: %s", entry.title)
    data = hass.data[DOMAIN][entry.entry_id]
    if 'sensor' in data.platforms_set_up:
        _LOGGER.warning('Sensor platform already set up for %s', entry.entry_id)
        return True
    data.platforms_set_up.append('sensor')
    def new_device(uid: str):
        _LOGGER.info('New sensor device: %s:%s', entry.entry_id, uid)
        dev = hass.data[DOMAIN][entry.entry_id].dev[uid]
        if dev['hass_sensor_entity'] is not None:
            return
        if dev['device']['devClass'] in [ 'sp3s' ]:
            dev['hass_sensor_entity'] = BroadlinkHubPowerSensor(hass, entry, uid)
            async_add_entities([ dev['hass_sensor_entity'] ])
    async_dispatcher_connect(hass, SIGNAL_NEW_SENSOR(entry), new_device)
    data.platform_setups_pending = data.platform_setups_pending - 1
    if data.platform_setups_pending == 0:
        connectorRelease(hass, entry)
    return True

class BroadlinkHubPowerSensor(BroadlinkHubEntity):
    """Broadlink Hub sensor entity"""

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return POWER_WATT

    @property
    def device_class(self):
        """Return the class of this device."""
        return DEVICE_CLASS_POWER

    @property
    def unique_id(self):
        return self.uid
