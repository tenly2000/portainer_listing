"""
Portainer Status Support

Original Author:  Jim Thompson

Description:
  Configuration Instructions are on GitHub.

"""

import logging
import requests
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=2)

def setup_platform(hass, config, add_entities, discovery_info=None):
    url = config.get("url")
    username = config.get("username")
    password = config.get("password")
    name = config.get("name")
    
    if not url or not username or not password or not name:
        _LOGGER.error("URL, username, name or password not provided.")
        return False

    try:
        _LOGGER.debug(f"Loading Portainer server from {url}")
        portainer = PortainerData(url, username, password)
        portainer.update()
    except Exception as e:
        _LOGGER.error(f"Failed to connect to Portainer: {e}")
        return False

    server_entity = PortainerServerSensor(portainer, url, name)
    add_entities([server_entity], True)
    add_entities([PortainerContainerSensor(container, portainer, url, name) for container in portainer.containers], True)


class PortainerServerSensor(Entity):
    def __init__(self, portainer, url, name):
        self._portainer = portainer
        self._url = url
        self._state = None
        self._attributes = {}
        self._name = f"portainer_server_{name}"

    @property
    def unique_id(self):
        return self._name

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return "mdi:server"

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def extra_state_attributes(self):
        return {
            "PortainerId": self._portainer.instance_id,
            "FriendlyName": self._name,
            "Version": self._portainer.version,
            "NumberOfContainers": len(self._portainer.containers),
            "url": self._url,
        }
        
    def update(self):
        self._portainer.update()
        _LOGGER.debug(f"Updating Portainer server: {self._portainer.instance_id} from {self._url}")
        self._state = self._portainer.version
   
class PortainerContainerSensor(Entity):
    def __init__(self, container, portainer, url, server_name):
        self._container = container
        self._portainer = portainer
        self._url = url
        self._state = None
        self._attributes = {}
        self._name = f"portainer_{server_name}_{container['Names'][0].strip('/')}"

    @property
    def unique_id(self):
        return self._name
#        return f"portainer_container_{self._container['Id']}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return "mdi:docker"

    @property
    def extra_state_attributes(self):
        attrs = {
            "Name": self._container["Names"][0].strip("/"),
            "Image": self._container["Image"],
            "ContainerId": self._container["Id"],
            "Created": datetime.fromtimestamp(self._container["Created"]).strftime("%Y%m%dT%H:%M:%S"),
            "Status": self._container["Status"],
            "Ports": [f"{port.get('PublicPort', 'N/A')}->{port['PrivatePort']}/{port['Type']}"
                      for port in self._container["Ports"]
                      if not ':' in str(port.get('IP', ''))],
            "url": self._url,
            "parent_friendly_name": f"portainer_server_{self._name.split('_')[1]}",
            "parent_instance_id": self._portainer.instance_id
        }
        return attrs


    def update(self):
        # Update the container data from the PortainerData instance
        self._container = next((c for c in self._portainer.containers if c['Id'] == self._container['Id']), None)

        if self._container:
            _LOGGER.debug(f"Updating container named: {self._container['Names'][0].strip('/')} ({self._container['Image']})  from {self._url}")
            self._state = self._container['State']
        else:
            _LOGGER.error(f"Container not found: {self.unique_id}")

class PortainerData:
    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password
        self._jwt = None
        self.instance_id = None
        self.version = None
        self.containers = []
        self.endpoint_id = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        if not self._jwt:
            self._jwt = self._get_jwt()

        if self._jwt:
            if not self.endpoint_id:
                self.endpoint_id = self._get_first_endpoint_id()
            self.containers = self._get_containers(self.endpoint_id)
            self.instance_id, self.version = self._get_status()
        else:
            _LOGGER.error("Failed to authenticate with Portainer.")

    def _get_jwt(self):
        try:
            response = requests.post(f"{self._url}/api/auth", json={"Username": self._username, "Password": self._password}, timeout=5)
            response.raise_for_status()
            return response.json().get("jwt")
        except Exception as e:
            _LOGGER.error(f"Failed to get JWT: {e}")
            return None

    def _get_first_endpoint_id(self):
        try:
            response = requests.get(f"{self._url}/api/endpoints", headers={"Authorization": f"Bearer {self._jwt}"}, timeout=5)
            response.raise_for_status()
            endpoints = response.json()
            for endpoint in endpoints:
                if endpoint["Type"] != 4:  # Filter out edge agent endpoints
                    return endpoint["Id"]
            return None
        except Exception as e:
            _LOGGER.error(f"Failed to get endpoint ID: {e}")
            return None

    def _get_containers(self, endpoint_id):
        try:
            response = requests.get(f"{self._url}/api/endpoints/{endpoint_id}/docker/containers/json?all=1", headers={"Authorization": f"Bearer {self._jwt}"}, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            _LOGGER.error(f"Failed to get containers: {e}")
            return []

    def _get_status(self):
        try:
            response = requests.get(f"{self._url}/api/status", headers={"Authorization": f"Bearer {self._jwt}"}, timeout=5)
            response.raise_for_status()
            status_data = response.json()
            return status_data["InstanceID"], status_data["Version"]
        except Exception as e:
            _LOGGER.error(f"Failed to get status: {e}")
            return None, None

