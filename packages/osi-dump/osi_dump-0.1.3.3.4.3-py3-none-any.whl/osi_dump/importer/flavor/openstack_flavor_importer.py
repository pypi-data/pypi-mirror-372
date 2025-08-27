import logging

import concurrent

from openstack.connection import Connection
from openstack.compute.v2.flavor import Flavor as OSFlavor

from osi_dump.importer.flavor.flavor_importer import FlavorImporter
from osi_dump.model.flavor import Flavor

logger = logging.getLogger(__name__)


class OpenStackFlavorImporter(FlavorImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_flavors(self) -> list[Flavor]:
        """Import flavors information from Openstack

        Raises:
            Exception: Raises exception if fetching flavor failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing flavors for {self.connection.auth['auth_url']}")

        try:
            osflavors: list[OSFlavor] = list(self.connection.list_flavors())
        except Exception as e:
            raise Exception(
                f"Can not fetch flavors for {self.connection.auth['auth_url']}"
            ) from e

        flavors: list[Flavor] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_flavor_info, osflavor)
                for osflavor in osflavors
            ]
            for future in concurrent.futures.as_completed(futures):
                flavors.append(future.result())

        logger.info(f"Imported flavors for {self.connection.auth['auth_url']}")

        return flavors

    def _get_flavor_info(self, flavor: OSFlavor) -> Flavor:

        ret_flavor = Flavor(
            flavor_id=flavor.id,
            flavor_name=flavor.name,
            ram=flavor.ram,
            vcpus=flavor.vcpus,
            disk=flavor.disk,
            swap=flavor.swap,
            public=flavor.is_public,
            properties=flavor.extra_specs,
        )

        return ret_flavor
