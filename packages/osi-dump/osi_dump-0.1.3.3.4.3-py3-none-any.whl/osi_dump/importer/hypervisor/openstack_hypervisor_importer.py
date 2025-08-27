import logging

import concurrent

from openstack.connection import Connection
from openstack.compute.v2.hypervisor import Hypervisor as OSHypervisor
from openstack.compute.v2.aggregate import Aggregate as OSAggregate

from openstack.placement.v1._proxy import Proxy as PlacementProxy
from openstack.placement.v1.resource_provider_inventory import ResourceProviderInventory

from osi_dump.importer.hypervisor.hypervisor_importer import HypervisorImporter
from osi_dump.model.hypervisor import Hypervisor

from osi_dump.api.placement import get_usage

logger = logging.getLogger(__name__)


class OpenStackHypervisorImporter(HypervisorImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_hypervisors(self) -> list[Hypervisor]:
        """Import hypervisors information from Openstack

        Raises:
            Exception: Raises exception if fetching hypervisor failed

        Returns:
            list[Hypervisor]: _description_
        """
        aggregates = list(self.connection.list_aggregates())

        try:
            oshypervisors: list[OSHypervisor] = list(
                self.connection.compute.hypervisors(details=True, with_servers=True)
            )

        except Exception as e:
            raise Exception(
                f"Can not fetch hypervisor for {self.connection.auth['auth_url']}"
            ) from e

        hypervisors: list[Hypervisor] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_hypervisor_info, hypervisor, aggregates)
                for hypervisor in oshypervisors
            ]
            for future in concurrent.futures.as_completed(futures):
                hypervisors.append(future.result())

        logger.info(f"Imported hypervisors for {self.connection.auth['auth_url']}")

        return hypervisors


    def _normalize_hypervisor_aggregate(self, hypervisors: list[Hypervisor]):
        
        aggregate_id_map = {

        }

        aggregates: list[list[dict]] = [

        ]

        for hypervisor in hypervisors:
            aggregates.append(hypervisor.aggregates)

    def _swap_element(array, i, j): 
        array[i], array[j] = array[j], array[i]

    def _get_hypervisor_info(
        self, hypervisor: OSHypervisor, aggregates: list[OSAggregate]
    ) -> Hypervisor:
        aggregate_list, az = self._get_aggregates(hypervisor=hypervisor)

        placement_proxy: PlacementProxy = self.connection.placement

        rpi: ResourceProviderInventory = list(
            placement_proxy.resource_provider_inventories(
                resource_provider=hypervisor.id
            )
        )

        usage_data = get_usage(self.connection, resource_provider_id=hypervisor.id)

        vcpu = rpi[0]
        memory = rpi[1]
        disk = rpi[2]

        ret_hypervisor = Hypervisor(
            hypervisor_id=hypervisor.id,
            hypervisor_type=hypervisor.hypervisor_type,
            name=hypervisor.name,
            state=hypervisor.state,
            status=hypervisor.status,
            local_disk_size=disk["max_unit"],
            memory_size=memory["max_unit"] + memory["reserved"],
            vcpus=vcpu["max_unit"],
            vcpus_usage=usage_data["VCPU"],
            memory_usage=usage_data["MEMORY_MB"],
            local_disk_usage=usage_data["DISK_GB"],
            vm_count=len(hypervisor.servers),
            aggregates=aggregate_list,
            availability_zone=az,
        )

        return ret_hypervisor

    def _get_aggregates(self, hypervisor: OSHypervisor):
        aggregates_ret = []

        aggregates: OSAggregate = list(self.connection.list_aggregates())

        az = None

        for aggregate in aggregates:
            if hypervisor.name in aggregate.hosts:
                aggregates_ret.append(
                    {
                        "id": aggregate.id,
                        "name": aggregate.name,
                    }
                )

                if aggregate.availability_zone != None:
                    az = aggregate.availability_zone

        aggregates_ret = [
            dict(sorted(aggregate.items())) for aggregate in aggregates_ret
        ]

        return aggregates_ret, az
