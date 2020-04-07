import asyncio
import logging
import websocket
import json
import time

from threading import Thread

from homeassistant import config_entries
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.core import callback

from .const import DOMAIN, SIGNAL_DEVICE_UPDATE, SIGNAL_HUB_CONNECTION_ON, SIGNAL_HUB_CONNECTION_OFF

_LOGGER = logging.getLogger(__name__)

def connectorStart(hass, entry):
    """Start Broadlink Hub Connector"""
    data = hass.data[DOMAIN][entry.entry_id]
    data.lock.acquire()
    if hasattr(data, 'thread'):
        data.lock.release()
        _LOGGER.error('Connector already ruunning for %s', entry.entry_id)
        return False
    if data.die:
        data.lock.release()
        _LOGGER.warning('Connector already dying for %s', entry.entry_id)
        return False
    data.thread_waiting_relase = True
    data.thread_name = (DOMAIN + ':' + entry.entry_id)
    data.thread = Thread(name=data.thread_name, target=run, args=[hass, entry])
    data.thread.start()
    return True

def connectorRelease(hass, entry):
    """Release Broadlink Hub Connector"""
    data = hass.data[DOMAIN][entry.entry_id]
    if data.thread_waiting_relase:
        data.thread_waiting_relase = False
        data.lock.release()
        return True
    _LOGGER.error('connectorRelease called but thread is not waiting to be released')
    return False

def connectorStop(hass, entry):
    """Stop Broadlink Hub Connector"""
    data = hass.data[DOMAIN][entry.entry_id]
    data.lock.acquire()
    if not hasattr(data, 'thread'):
        data.lock.release()
        _LOGGER.warning('Connector already dead for %s', entry.entry_id)
        return False
    if not data.die:
        data.die = True
        if hasattr(data, 'ws'):
            data.ws.close()
    data.lock.release()
    try:
        data.thread.join(2)
    except:
        pass
    data.lock.acquire()
    if hasattr(data, 'thread'):
        if data.thread.is_alive():
            data.lock.release()
            _LOGGER.warning('Connector refuses to die for %s', entry.entry_id)
            return False
        del data.thread
        del data.thread_name
    return True

def run(hass, entry):
    """Broadlink Hub background thread"""
    data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.info('Background thread initiated and is waiting to be released')
    data.lock.acquire()
    data.lock.release()
    _LOGGER.info('Background thread is released and will start running now')
    def handle(message):
        status = message['status']
        uid = None
        if status == 'hello':
            pass
        elif status == 'reachable':
            uid = message['device']['uid']
            _LOGGER.info(uid + ' is reachable')
            if 'udata' not in message['device']:
                message['device']['udata'] = {}
            message['hass_url_headers'] = data.headers
            message['hass_url_power_on'] = data.url + 'power?uid=' + uid + '&power=on'
            message['hass_url_power_off'] = data.url + 'power?uid=' + uid + '&power=off'
            message['hass_config_entry_id'] = entry.entry_id
            message['hass_entity_created'] = False
            message['hass_switch_entity'] = None
            if uid in data.dev:
                message['hass_entity_created'] = data.dev[uid]['hass_entity_created']
                message['hass_switch_entity'] = data.dev[uid]['hass_switch_entity']
            data.dev[uid] = message
        elif status == 'unreachable':
            uid = message['device']['uid']
            if uid not in data.dev:
                #_LOGGER.warning('Unreachable notification for unknown device ' + uid)
                return
            _LOGGER.info(uid + ' is unreachable')
            data.dev[uid]['status'] = 'unreachable'
        elif status == 'update':
            uid = message['device']['uid']
            if uid not in data.dev:
                _LOGGER.warning('Update for unknown device ' + uid)
                return
            for key in message['device']:
                if key != 'uid' and key != 'udata':
                    data.dev[uid]['device'][key] = message['device'][key]
            if 'udata' in message['device']:
                for key in message['device']['udata']:
                    data.dev[uid]['device']['udata'][key] = message['device']['udata'][key]
                    _LOGGER.info(uid + ' is updated')
        if uid is not None:
            dispatcher_send(hass, SIGNAL_DEVICE_UPDATE, entry, uid)
    def on_message(ws, message):
        try:
            message = json.loads(message)
            handle(message)
        except:
            _LOGGER.warning('Unable to parse input')
            ws.close()
    def on_error(ws, error):
        _LOGGER.warning('### error ###: %s', error)
        ws.close()
    def on_close(ws):
        _LOGGER.info('### close ###')
        for uid in data.dev:
            data.dev[uid]['status'] = 'unreachable'
        dispatcher_send(hass, SIGNAL_HUB_CONNECTION_OFF, entry)
        del data.ws
    def on_open(ws):
        _LOGGER.info('### open ###')
        dispatcher_send(hass, SIGNAL_HUB_CONNECTION_ON, entry)
    while not data.die:
        data.lock.acquire()
        if not data.die:
            _LOGGER.info("Attempting connect to %s\n", data.ws_url)
            header = []
            for h in data.headers:
                header.append(h + ': ' + data.headers[h])
            data.ws = websocket.WebSocketApp(data.ws_url,
                                             on_message=on_message,
                                             on_error=on_error,
                                             on_close=on_close,
                                             header=header
            )
            data.ws.on_open = on_open
            data.lock.release()
            data.ws.run_forever()
        else:
            data.lock.release()
        if not data.die:
            time.sleep(10)
