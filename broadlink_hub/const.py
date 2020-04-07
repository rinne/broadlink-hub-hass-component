"""Constants for Broadlink Hub"""

DOMAIN = "broadlink_hub"

DEFAULT_PORT = 8525
DEFAULT_SSL = False

BROADLINK_HUB_PLATFORMS = [ 'switch', 'sensor' ]

SIGNAL_DEVICE_UPDATE = DOMAIN + ':' + 'DEVICE_UPDATE'
SIGNAL_HUB_CONNECTION_ON = DOMAIN + ':' + 'HUB_CONNECTION_ON'
SIGNAL_HUB_CONNECTION_OFF = DOMAIN + ':' + 'HUB_CONNECTION_OFF'

def SIGNAL_NEW_SWITCH(entry):
    return DOMAIN + ':' + 'NEW_SWITCH' + ':' + entry.entry_id

def SIGNAL_NEW_SENSOR(entry):
    return DOMAIN + ':' + 'NEW_SENSOR' + ':' + entry.entry_id
