import re
import logging

import requests
import docker
from docker.errors import ImageNotFound

from api.models import Service
from api.config import SERVICE_URL, DOCKER_SOCKET_PATH


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

VERSION_PATTERN = re.compile(r'[\d\.]+')


class ServiceInfo:
    _instance = None

    def __init__(self):
        self._docker = docker.DockerClient(
            base_url=f'unix://{DOCKER_SOCKET_PATH}')

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = ServiceInfo()
        return cls._instance

    def get_installed_version(self, service_name):
        try:
            image = self._docker.images.get(service_name)
        except ImageNotFound:
            # Image does not exist, not downloaded or running...
            return False, None

        for container in self._docker.containers.list():
            image = container.image
            if image.name == service_name:
                for tag in image.tags:
                    # Try to find a version:
                    if VERSION_PATTERN.match(tag):
                        return True, tag

        # Downloaded, but not running
        return True, None
