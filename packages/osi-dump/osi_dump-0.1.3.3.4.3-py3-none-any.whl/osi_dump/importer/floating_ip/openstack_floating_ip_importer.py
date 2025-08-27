import logging

import concurrent

from openstack.connection import Connection
from openstack.network.v2.floating_ip import FloatingIP as OSFloatingIP

from osi_dump.importer.floating_ip.floating_ip_importer import FloatingIPImporter
from osi_dump.model.floating_ip import FloatingIP

logger = logging.getLogger(__name__)


class OpenStackFloatingIPImporter(FloatingIPImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_floating_ips(self) -> list[FloatingIP]:
        """Import instances information from Openstack

        Raises:
            Exception: Raises exception if fetching server failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing floating ips for {self.connection.auth['auth_url']}")

        try:
            osfloating_ips: list[OSFloatingIP] = list(
                self.connection.list_floating_ips()
            )
        except Exception as e:
            raise Exception(
                f"Can not fetch floating IPs for {self.connection.auth['auth_url']}"
            ) from e

        floating_ips: list[FloatingIP] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_floating_ip_info, osfloating_ip)
                for osfloating_ip in osfloating_ips
            ]
            for future in concurrent.futures.as_completed(futures):
                floating_ips.append(future.result())

        logger.info(f"Imported floating ips for {self.connection.auth['auth_url']}")

        return floating_ips

    def _get_floating_ip_info(self, floating_ip: OSFloatingIP) -> FloatingIP:

        ret_floating_ip = FloatingIP(
            floating_ip_id=floating_ip.id,
            project_id=floating_ip.project_id,
            floating_ip_address=floating_ip.floating_ip_address,
            floating_network=floating_ip.floating_network_id,
            fixed_ip_address=floating_ip.fixed_ip_address,
            router_id=floating_ip.router_id,
            port_id=floating_ip.port_id,
            status=floating_ip.status,
            created_at=floating_ip.created_at,
            updated_at=floating_ip.updated_at,
        )

        return ret_floating_ip
