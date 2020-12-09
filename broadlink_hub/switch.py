"""Broadlink Hub switches"""

import asyncio
import logging

from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.switch import SwitchDevice, DEVICE_CLASS_SWITCH, DEVICE_CLASS_OUTLET

from .const import DOMAIN, SIGNAL_NEW_SWITCH
from .entity import BroadlinkHubEntity
from .get import get
from .connector import connectorRelease

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, entry, async_add_entities):
    """Broadlink Hub switch setup"""
    _LOGGER.info("Broadlink Hub Switch Setup Entry: %s", entry.title)
    data = hass.data[DOMAIN][entry.entry_id]
    if 'switch' in data.platforms_set_up:
        _LOGGER.warning('Switch platform already set up for %s', entry.entry_id)
        return True
    data.platforms_set_up.append('switch')
    def new_device(uid: str):
        _LOGGER.info('New switch device: %s:%s', entry.entry_id, uid)
        dev = hass.data[DOMAIN][entry.entry_id].dev[uid]
        if dev['hass_switch_entity'] is not None:
            return
        dev['hass_switch_entity'] = BroadlinkHubSwitch(hass, entry, uid)
        async_add_entities([ dev['hass_switch_entity'] ])
    async_dispatcher_connect(hass, SIGNAL_NEW_SWITCH(entry), new_device)
    data.platform_setups_pending = data.platform_setups_pending - 1
    if data.platform_setups_pending == 0:
        connectorRelease(hass, entry)
    return True

class BroadlinkHubSwitch(BroadlinkHubEntity, SwitchDevice):
    """Broadlink Hub switch entity"""

    def __init__(self, hass, entry, uid):
        """Set up switch device."""
        super().__init__(hass, entry, uid)

    async def async_turn_on(self, **kwargs):
        """Turn on the device."""
        dev = self._d
        status = await get(dev['hass_url_power_on'],  dev['hass_url_headers'])
        return (status == 200)

    async def async_turn_off(self, **kwargs):
        """Turn off the device."""
        dev = self._d
        status = await get(dev['hass_url_power_off'], dev['hass_url_headers'])
        return (status == 200)
    
    async def async_toggle(self, **kwargs):
        """Toggle the device."""
        dev = self._d
        if self.is_on:
            return await self.sync_turn_off()
        else:
            return await self.sync_turn_on()
        return (status == 200)
    
    @property
    def state(self):
        """Return state of the device."""
        dev = self._d
        if dev['device']['udata']['power']:
            return STATE_ON
        else:
            return STATE_OFF

    @property
    def is_on(self):
        """Return true if device is on."""
        dev = self._d
        return dev['device']['udata']['power']

    @property
    def device_class(self):
        """Return the class of this device."""
        dev = self._d
        if dev['device']['devClass'] in [ 'sp1', 'sp2', 'sp3', 'sp3s', 'sp4' ]:
            return DEVICE_CLASS_OUTLET
        elif dev['device']['devClass'] in [ 'sc1', 'mcb1' ]:
            return DEVICE_CLASS_SWITCH
        return None
