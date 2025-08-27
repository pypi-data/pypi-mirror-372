import logging

import ipaddress

import concurrent

import numpy as np

from openstack.connection import Connection
from openstack.network.v2.port import Port as OSPort
from openstack.network.v2.subnet import Subnet as OSSubnet
from openstack.network.v2.floating_ip import FloatingIP as OSFloatingIP
from openstack.network.v2.router import Router as OSRouter
from openstack.network.v2.network import Network as OSNetwork

from osi_dump.importer.external_port.external_port_importer import ExternalPortImporter
from osi_dump.model.external_port import ExternalPort

import osi_dump.api.neutron as osi_neutron

logger = logging.getLogger(__name__)


class OpenStackExternalPortImporter(ExternalPortImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def _get_external_ports(self) -> list[OSPort]:

        # Get all external networks
        networks = self.connection.network.networks(
            is_router_external=True,
        )

        external_ports = []

        for network in networks:
            ex_ports = list(self.connection.network.ports(network_id=network.id))

            for ex_port in ex_ports:
                external_ports.append(ex_port)

        # Get all port on those networks

        return external_ports

    def import_external_ports(self) -> list[ExternalPort]:
        """Import external_ports information from Openstack


        Raises:
            Exception: Raises exception if fetching external_port failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing external_ports for {self.connection.auth['auth_url']}")

        try:
            os_ports: list[OSPort] = self._get_external_ports()
        except Exception as e:
            raise Exception(
                f"Can not fetch external_ports for {self.connection.auth['auth_url']} {e}"
            ) from e

        external_ports: list[ExternalPort] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_external_port_info, external_port)
                for external_port in os_ports
            ]
            for future in concurrent.futures.as_completed(futures):
                external_ports.append(future.result())

        logger.info(f"Imported external_ports for {self.connection.auth['auth_url']}")

        external_ports = sorted(
            external_ports,
            key=lambda external_port: (
                external_port.network_id,
                (
                    ipaddress.ip_address(external_port.ip_address)
                    if external_port.ip_address
                    else ipaddress.ip_address("0.0.0.0")
                ),
            ),
        )

        return external_ports

    def _get_external_port_info(self, external_port: OSPort) -> ExternalPort:

        subnet_id = None
        ip_address = None
        subnet_cidr = None

        try:
            ip_address = external_port.fixed_ips[0]["ip_address"]
        except Exception as e:
            logger.warning(f"No IP address found for port {external_port.id}")

        try:
            subnet_id = external_port.fixed_ips[0]["subnet_id"]
        except Exception as e:
            logger.warning(f"No subnet ID found for {external_port.id}")

        try:
            subnet: OSSubnet = self.connection.get_subnet_by_id(subnet_id)

            subnet_cidr = subnet.cidr
        except Exception as e:
            logger.warning(f"No subnet cidr found for port {external_port.id}")

        mapped_device_project = ["network:floatingip", "network:router_gateway"]

        project_id = (
            external_port.project_id
            if external_port.device_owner not in mapped_device_project
            else self._map_project_id(
                device_owner=external_port.device_owner,
                device_id=external_port.device_id,
            )
        )
        
        network: OSNetwork = self.connection.get_network(name_or_id=external_port.network_id)

        vlan_id = None
        
        try: 
            if not network.segments: 
                vlan_id = network.provider_segmentation_id
            else: 
                logger.warning(f"Multiple segments mapped for net id {network.id}")
        except Exception as e: 
            logger.warning(f"Can not get vlan ID for external port {external_port.id}, net id {network.id}")
        
        external_port_ret = ExternalPort(
            port_id=external_port.id,
            project_id=project_id,
            network_id=external_port.network_id,
            network_name=network.name,
            subnet_id=subnet_id,
            subnet_cidr=subnet_cidr,
            ip_address=ip_address,
            allowed_address_pairs=external_port.allowed_address_pairs,
            device_id=external_port.device_id,
            device_owner=external_port.device_owner,
            status=external_port.status,
            vlan_id=vlan_id
        )

        return external_port_ret

    def _map_project_id(self, device_owner: str, device_id: str) -> str:

        if device_owner == "network:router_gateway":
            return self._map_project_id_router(device_id=device_id)
        elif device_owner == "network:floatingip":
            return self._map_project_id_floating(device_id=device_id)

        return ""

    def _map_project_id_router(self, device_id: str) -> str:
        project_id = osi_neutron.get_router_project(
            self.connection, router_id=device_id
        )

        return project_id

    def _map_project_id_floating(self, device_id: str) -> str:
        project_id = osi_neutron.get_floating_ip_project(
            self.connection, floating_ip_id=device_id
        )

        return project_id
