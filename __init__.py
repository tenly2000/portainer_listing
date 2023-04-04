import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    for conf in config["sensor"]:
        if conf["platform"] == DOMAIN:
            hass.data[DOMAIN] = conf
    return True
