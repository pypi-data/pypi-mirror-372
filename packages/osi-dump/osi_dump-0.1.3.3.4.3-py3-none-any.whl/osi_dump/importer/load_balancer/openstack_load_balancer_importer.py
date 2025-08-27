import logging

import concurrent

from openstack.connection import Connection

from openstack.load_balancer.v2.load_balancer import LoadBalancer as OSLoadBalancer

from osi_dump.importer.load_balancer.load_balancer_importer import (
    LoadBalancerImporter,
)
from osi_dump.model.load_balancer import LoadBalancer

import osi_dump.api.octavia as octavia_api

logger = logging.getLogger(__name__)


class OpenStackLoadBalancerImporter(LoadBalancerImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_load_balancers(self) -> list[LoadBalancer]:
        """Import load_balancers information from Openstack

        Raises:
            Exception: Raises exception if fetching load_balancer failed

        Returns:
            list[LoadBalancer]: _description_
        """

        logger.info(f"Importing load_balancers for {self.connection.auth['auth_url']}")

        try:
            osload_balancers: list[OSLoadBalancer] = octavia_api.get_load_balancers(
                connection=self.connection
            )
        except Exception as e:
            raise Exception(
                f"Can not fetch load_balancers for {self.connection.auth['auth_url']} {e}"
            ) from e

        load_balancers: list[LoadBalancer] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [] 
            
            for load_balancer in osload_balancers:
                logger.info("Importing load_balancer: %s", load_balancer["id"])
                if load_balancer["id"] != None:
                    futures.append(executor.submit(self._get_load_balancer_info, load_balancer))
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result() 
                
                if result != None: 
                    load_balancers.append(result)

        logger.info(f"Imported load_balancers for {self.connection.auth['auth_url']}")

        return load_balancers

    def _get_load_balancer_info(self, load_balancer: OSLoadBalancer) -> LoadBalancer:

        lb_flavor_name = None 
        lb_flavor_description = None 

        try: 
            lb_flavor = octavia_api.get_load_balancer_flavor(
                connection=self.connection, 
                flavor_id=load_balancer["flavor_id"]
            )

            if lb_flavor:
                lb_flavor_name = lb_flavor["name"]
                lb_flavor_description = lb_flavor["description"]
            else: 
                raise Exception(f'No flavor id found for {load_balancer["id"]}')
        except Exception as e: 
            logger.warning(f"Get load balancer flavor failed {e}")

        try: 
            amphoraes = octavia_api.get_amphoraes(
                connection=self.connection, load_balancer_id=load_balancer["id"]
            )

            for amphorae in amphoraes:
                flavor = self.connection.get_flavor_by_id(amphorae["compute_flavor"])
                amphorae["ram"] = flavor.ram
                amphorae["vcpus"] = flavor.vcpus
                amphorae["flavor_name"] = flavor.name 
                amphorae["flavor_description"] = flavor.description

            load_balancer_ret = LoadBalancer(
                id=load_balancer["id"],
                load_balancer_name=load_balancer["name"],
                operating_status=load_balancer["operating_status"],
                project_id=load_balancer["project_id"],
                provisioning_status=load_balancer["provisioning_status"],
                created_at=load_balancer["created_at"],
                updated_at=load_balancer["updated_at"],
                amphoraes=amphoraes,
                vip=load_balancer["vip_address"],
                flavor_name=lb_flavor_name, 
                flavor_description=lb_flavor_description
            )

            return load_balancer_ret
        except Exception as e: 
            logger.warning(f"Getting lb failed {e}")
            
            return None
