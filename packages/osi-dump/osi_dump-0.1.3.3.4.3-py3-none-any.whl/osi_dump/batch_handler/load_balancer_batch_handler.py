import logging

from openstack.connection import Connection

from osi_dump.exporter.load_balancer.load_balancer_exporter import (
    LoadBalancerExporter,
)
from osi_dump.exporter.load_balancer.excel_load_balancer_exporter import (
    ExcelLoadBalancerExporter,
)

from osi_dump.importer.load_balancer.load_balancer_importer import (
    LoadBalancerImporter,
)
from osi_dump.importer.load_balancer.openstack_load_balancer_importer import (
    OpenStackLoadBalancerImporter,
)


from osi_dump import util

logger = logging.getLogger(__name__)


class LoadBalancerBatchHandler:
    def __init__(self):
        self._importer_exporter_list: list[
            tuple[LoadBalancerImporter, LoadBalancerExporter]
        ] = []

    def add_importer_exporter_from_openstack_connections(
        self, connections: list[Connection], output_file: str
    ):
        for connection in connections:
            importer = OpenStackLoadBalancerImporter(connection)

            sheet_name = f"{util.extract_hostname(connection.auth['auth_url'])}-lb"
            exporter = ExcelLoadBalancerExporter(
                sheet_name=sheet_name, output_file=output_file
            )

            self.add_importer_exporter(importer=importer, exporter=exporter)

    def add_importer_exporter(
        self, importer: LoadBalancerImporter, exporter: LoadBalancerExporter
    ):
        self._importer_exporter_list.append((importer, exporter))

    def process(self):

        for importer, exporter in self._importer_exporter_list:
            try:

                load_balancers = importer.import_load_balancers()

                exporter.export_load_balancers(load_balancers=load_balancers)
            except Exception as e:
                logger.warning(e)
                logger.warning("Skipping...")
