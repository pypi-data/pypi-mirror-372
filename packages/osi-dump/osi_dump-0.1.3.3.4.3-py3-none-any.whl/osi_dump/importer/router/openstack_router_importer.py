import logging

import concurrent

from openstack.connection import Connection
from openstack.network.v2.router import Router as OSRouter

from osi_dump.importer.router.router_importer import (
    RouterImporter,
)
from osi_dump.model.router import Router

logger = logging.getLogger(__name__)


class OpenStackRouterImporter(RouterImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_routers(self) -> list[Router]:
        """Import routers information from Openstack

        Raises:
            Exception: Raises exception if fetching router failed

        Returns:
            list[Router]: _description_
        """

        logger.info(f"Importing routers for {self.connection.auth['auth_url']}")

        try:
            osrouters: list[OSRouter] = list(self.connection.network.routers())
        except Exception as e:
            raise Exception(
                f"Can not fetch routers for {self.connection.auth['auth_url']}"
            ) from e

        routers: list[Router] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_router_info, router) for router in osrouters
            ]
            for future in concurrent.futures.as_completed(futures):
                routers.append(future.result())

        logger.info(f"Imported routers for {self.connection.auth['auth_url']}")

        return routers

    def _get_router_info(self, router: OSRouter) -> Router:
        """
                {"network_id": "49760654-71d8-4967-8fdd-5a35d3ff78ef", "external_fixed_ips": [{"subnet_id":                                   |
        |                           | "c044a5c0-4b11-4d8d-ae5e-9ff4ce6c1be6", "ip_address": "10.0.2.188"}], "enable_snat": true}
        """

        external_net_id = None

        try:
            external_net_id = router.external_gateway_info["network_id"]
        except Exception as e:
            logger.warning(f"Could not get external net id for router: {router.id}")

        external_net_ip = None

        try:
            external_net_ip = router.external_gateway_info["external_fixed_ips"][0][
                "ip_address"
            ]

        except Exception as e:
            logger.warning(f"Could not get external net ip for router {router.id}")

        router_ret = Router(
            router_id=router.id,
            name=router.name,
            external_net_id=external_net_id,
            external_net_ip=external_net_ip,
            status=router.status,
            admin_state=router.is_admin_state_up,
            project_id=router.project_id,
            created_at=router.created_at,
            updated_at=router.updated_at,
        )

        return router_ret
