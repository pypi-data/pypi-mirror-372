import logging

import concurrent

from openstack.network.v2.network import Network as OSNetwork
from openstack.network.v2.subnet import Subnet as OSSubnet

from openstack.connection import Connection

from osi_dump.importer.network.network_importer import NetworkImporter 
from osi_dump.model.network import Network 


logger = logging.getLogger(__name__)


class OpenStackNetworkImporter(NetworkImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_networks(self) -> list[Network]:
        """Import networks information from Openstack

        Raises:
            Exception: Raises exception if fetching networks failed

        Returns:
            list[Network]: _description_
        """

        try:
            os_networks: list[OSNetwork] = list(self.connection.list_networks())
        except Exception as e:
            raise Exception(
                f"Can not fetch hypervisor for {self.connection.auth['auth_url']}"
            ) from e

        networks: list[Network] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_network_info, network)
                for network in os_networks
            ]
            for future in concurrent.futures.as_completed(futures):
                networks.append(future.result())

        logger.info(f"Imported networks for {self.connection.auth['auth_url']}")

        return networks


    def _get_network_info(
        self, network: OSNetwork, 
    ) -> Network:

        subnets = self._get_subnets_info(subnet_ids=network.subnet_ids)

        return Network(
            network_id=network.id,
            project_id=network.project_id, 
            name=network.name, 
            mtu=network.mtu, 
            port_security_enabled=network.is_port_security_enabled,
            network_type=network.provider_network_type, 
            physical_network=network.provider_physical_network,
            segmentation_id=network.provider_segmentation_id,
            status=network.status, 
            shared=network.is_shared,
            created_at=network.created_at,
            updated_at=network.updated_at,
            subnets=subnets
        )
    

    def _get_subnets_info(self, subnet_ids: list[str]) -> list[dict]: 
        subnets = []

        for subnet_id in subnet_ids: 
            os_subnet: OSSubnet = self.connection.get_subnet(name_or_id=subnet_id) 

            if not os_subnet: 
                continue 
                
            subnets.append({
                "id": os_subnet.id, 
                "cidr": os_subnet.cidr
            })

        return subnets



    