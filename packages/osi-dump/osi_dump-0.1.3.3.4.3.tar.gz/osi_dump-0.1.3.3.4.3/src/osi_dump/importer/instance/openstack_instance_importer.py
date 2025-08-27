import logging

import concurrent

from openstack.connection import Connection
from openstack.compute.v2.server import Server

from openstack.compute.v2.flavor import Flavor as OSFlavor

from osi_dump.importer.instance.instance_importer import InstanceImporter
from osi_dump.model.instance import Instance

logger = logging.getLogger(__name__)


class OpenStackInstanceImporter(InstanceImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_instances(self) -> list[Instance]:
        """Import instances information from Openstack

        Raises:
            Exception: Raises exception if fetching server failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing instances for {self.connection.auth['auth_url']}")

        try:
            servers: list[Server] = list(
                self.connection.compute.servers(details=True, all_projects=True)
            )
        except Exception as e:
            raise Exception(
                f"Can not fetch instances for {self.connection.auth['auth_url']}: {e}"
            ) from e

        instances: list[Instance] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_instance_info, server) for server in servers
            ]
            for future in concurrent.futures.as_completed(futures):
                instances.append(future.result())

        logger.info(f"Imported instances for {self.connection.auth['auth_url']}")

        return instances

    def _get_instance_info(self, server: Server) -> Instance:

        project_name = None
        project_id = None
        try:
            project = self.connection.identity.get_project(server.project_id)
            project_name = project.name
            project_id = project.id
        except Exception as e:
            logger.warn(
                f"Unable to obtain project name for instance: {server.name}: {e}"
            )

        domain_name = None
        try:
            domain = self.connection.identity.get_domain(project.domain_id)
            domain_name = domain.name
        except Exception as e:
            logger.warning(
                f"Unable to obtain domain name for instance {server.name}: {e}"
            )

        # Lấy thông tin IPv4 private
        private_v4_ips = []
        floating_ip = None

        try:
            for ips in server.addresses.values():
                for ip in ips:
                    if ip["OS-EXT-IPS:type"] == "fixed":
                        private_v4_ips.append(ip["addr"])
                    elif ip["OS-EXT-IPS:type"] == "floating":
                        floating_ip = ip["addr"]
        except Exception as e:
            logger.warning(
                f"Unable to obtain IP address information for instance {server.name}: {e}"
            )

        vgpus = None
        vgpu_type = None

        vgpu_metadata_property = "pci_passthrough:alias"

        try:
            flavor: OSFlavor = self.connection.get_flavor(
                name_or_id=server.flavor["id"]
            )

            vgpu_prop: str = flavor.extra_specs[vgpu_metadata_property]

            vgpu_props = vgpu_prop.split(":")

            vgpu_type = vgpu_props[0]
            vgpus = int(vgpu_props[1])

        except Exception as e:
            pass
        
        image_id = server.image["id"]
        flavor_id = server.flavor["id"]
        
        instance = Instance(
            instance_id=server.id,
            instance_name=server.name,
            project_id=project_id,
            project_name=project_name,
            domain_name=domain_name,
            private_v4_ips=private_v4_ips,
            floating_ip=floating_ip,
            status=server.status,
            hypervisor=server.hypervisor_hostname,
            ram=server.flavor["ram"],
            vcpus=server.flavor["vcpus"],
            created_at=server.created_at,
            updated_at=server.updated_at,
            user_id=server.user_id,
            vgpus=vgpus,
            vgpu_type=vgpu_type,
            image_id=image_id, 
            flavor_id=flavor_id
        )

        return instance
