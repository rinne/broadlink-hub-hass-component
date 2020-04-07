"""Base Class for Broadlink Hub"""

import logging

from datetime import date

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class BroadlinkHubEntity(Entity):
    """Common base for Broadlink Hub entities"""

    def __init__(self, hass, entry, uid):
        """Set up entity."""
        self.uid = uid
        self.hass = hass
        self.entry_id = entry.entry_id

    @property
    def _d(self):
        return self.hass.data[DOMAIN][self.entry_id].dev[self.uid]
    
    @property
    def name(self):
        """Return a unique identifier for this device."""
        dev = self._d
        return dev['device']['name'];

    @property
    def device_id(self):
        """Return the id of the device."""
        return self.uid

    @property
    def _last_updated(self):
        """Return the time of last update of a device."""
        dev = self._d
        return str(date.fromtimestamp(dev['device']['udata']['lastSeen'] / 1000))

    @property
    def available(self):
        """Return true if device is not offline."""
        dev = self._d
        return (dev['status'] == 'reachable')

    @property
    def should_poll(self):
        """Return polling state."""
        return False

    @property
    def current_power_w(self):
        """Return the current power usage in W."""
        dev = self._d
        if ('udata' in dev['device']) and ('energy' in dev['device']['udata']):
            return float(dev['device']['udata']['energy'])
        return None

    @property
    def device_info(self):
        """Return device info."""
        dev = self._d
        return { "identifiers": {(DOMAIN, self.uid)},
                 "connections": {(CONNECTION_NETWORK_MAC, dev['device']['mac'])},
                 "name": dev['device']['name'],
                 "manufacturer": 'Braadlink',
                 "model": dev['device']['devType'], }

    @property
    def unique_id(self):
        return self.uid
