"""Support for Broadlink Hub"""

import asyncio
import logging
import base64

from threading import Lock
from typing import Callable

from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_USERNAME, CONF_PASSWORD
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send

from .const import (DOMAIN, DEFAULT_PORT, BROADLINK_HUB_PLATFORMS, SIGNAL_NEW_SWITCH,
                    SIGNAL_DEVICE_UPDATE, SIGNAL_HUB_CONNECTION_ON, SIGNAL_HUB_CONNECTION_OFF)
from .connector import connectorStart, connectorStop

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistantType, config):
    """Broadlink Hub setup"""
    _LOGGER.info("Broadlink Hub Setup")
    hass.data[DOMAIN] = {}
    @callback
    def device_update_cb(*av):
        device_update(hass, *av)
    @callback
    def hub_connected_cb(*av):
        hub_connected(hass, *av)
    @callback
    def hub_disconnected_cb(*av):
        hub_disconnected(hass, *av)
    async_dispatcher_connect(hass, SIGNAL_DEVICE_UPDATE, device_update_cb)
    async_dispatcher_connect(hass, SIGNAL_HUB_CONNECTION_ON, hub_connected_cb)
    async_dispatcher_connect(hass, SIGNAL_HUB_CONNECTION_OFF, hub_disconnected_cb)
    return True

class BroadlinkHubEntryData:
    pass

async def async_setup_entry(hass: HomeAssistantType, entry):
    """Broadlink Hub configuration entry setup"""
    _LOGGER.info("Broadlink Hub Setup Entry: %s", entry.title)
    data =  BroadlinkHubEntryData()
    hass.data[DOMAIN][entry.entry_id] = data
    data.lock = Lock()
    data.dev = {}
    data.entry = entry
    if entry.data[CONF_SSL]:
        data.url = 'https'
        data.ws_url = 'wss'
    else:
        data.url = 'http'
        data.ws_url = 'ws'
    data.url += '://' + entry.data[CONF_HOST] + ':' + str(entry.data[CONF_PORT]) + '/'
    data.ws_url += '://' + entry.data[CONF_HOST] + ':' + str(entry.data[CONF_PORT]) + '/status'
    data.headers = {
        'Authorization': ('Basic ' +
                          (base64.b64encode(bytes(entry.data[CONF_USERNAME] +
                                                  ':' +
                                                  entry.data[CONF_PASSWORD], 'utf-8'))).decode('utf-8')),
    }
    data.die  = False
    data.platforms_set_up = [];
    data.platform_setups_pending = len(BROADLINK_HUB_PLATFORMS);
    for platform in BROADLINK_HUB_PLATFORMS:
        hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, platform))
    connectorStart(hass, entry);
    return True

async def async_unload_entry(hass: HomeAssistantType, entry):
    """Broadlink Hub configuration entry unload"""
    _LOGGER.info("Broadlink Hub Unload Entry: %s", entry.entry_id)
    connectorStop(hass, entry);
    return True

def device_update(hass: HomeAssistantType, entry, uid: str):
    dev = hass.data[DOMAIN][entry.entry_id].dev[uid]
    _LOGGER.info("Update: %s:%s %s", entry.entry_id, uid, str(dev))
    if not dev['hass_entity_created']:
        dev['hass_entity_created'] = True
        if dev['device']['devClass'] in [ 'sp1', 'sp2', 'sc1', 'sp3', 'sp3s', 'sp4', 'mcb1' ]:
            dispatcher_send(hass, SIGNAL_NEW_SWITCH(entry), uid)
    else:
        if dev['hass_switch_entity'] is not None:
            dev['hass_switch_entity'].async_schedule_update_ha_state(True)

def hub_connected(hass: HomeAssistantType, entry):
    _LOGGER.info("Connected: %s", entry.entry_id)

def hub_disconnected(hass: HomeAssistantType, entry):
    _LOGGER.info("Disconnected: %s", entry.entry_id)
    data = hass.data[DOMAIN][entry.entry_id]
    for uid in data.dev:
        if data.dev[uid]['hass_entity'] is not None:
            data.dev[uid]['hass_entity'].async_schedule_update_ha_state(True)
