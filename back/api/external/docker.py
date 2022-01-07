import re
import logging

import requests
import docker
from docker.errors import ImageNotFound

from api.tasks import cron
from api.config import SERVICE_URL, DOCKER_SOCKET_PATH


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

VERSION_PATTERN = re.compile(r'[\d\.]+')


@cron('0 */4 * * *')
def update_services():
    "Pull service information from website and update local data."
    if not SERVICE_URL:
        LOGGER.warning('Cannot update service descriptions, no URL')
        return

    data = requests.get(SERVICE_URL).json()
    for obj in data:
        try:
            service = Service.get(Service.name == obj['name'])

        except Service.DoesNotExist:
            service = Service(name=obj['name'])

        info = ServiceInfo.get()
        service.downloaded, service.installed_version = \
            info.get_installed_version(service.name)
        service.latest_version = obj['version']
        for attr in ('group', 'icon', 'description'):
            setattr(service, attr, obj[attr])

        service.save()

    data_names = [obj.name for obj in data]
    for service in Service.select():
        if service.name not in data_names:
            LOGGER.info('Purging service: %s', service.name)
            service.delete_instance()
            continue


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
