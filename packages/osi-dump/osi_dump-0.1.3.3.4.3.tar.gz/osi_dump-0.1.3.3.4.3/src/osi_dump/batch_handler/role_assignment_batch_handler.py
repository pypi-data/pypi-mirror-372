import logging

from openstack.connection import Connection

from osi_dump.exporter.role_assignment.role_assignment_exporter import (
    RoleAssignmentExporter,
)
from osi_dump.exporter.role_assignment.excel_role_assignment_exporter import (
    ExcelRoleAssignmentExporter,
)

from osi_dump.importer.role_assignment.role_assignment_importer import (
    RoleAssignmentImporter,
)
from osi_dump.importer.role_assignment.openstack_role_assignment_importer import (
    OpenStackRoleAssignmentImporter,
)


from osi_dump import util

logger = logging.getLogger(__name__)


class RoleAssignmentBatchHandler:
    def __init__(self):
        self._importer_exporter_list: list[
            tuple[RoleAssignmentImporter, RoleAssignmentExporter]
        ] = []

    def add_importer_exporter_from_openstack_connections(
        self, connections: list[Connection], output_file: str
    ):
        for connection in connections:
            importer = OpenStackRoleAssignmentImporter(connection)

            sheet_name = (
                f"{util.extract_hostname(connection.auth['auth_url'])}-role_ass"
            )
            exporter = ExcelRoleAssignmentExporter(
                sheet_name=sheet_name, output_file=output_file
            )

            self.add_importer_exporter(importer=importer, exporter=exporter)

    def add_importer_exporter(
        self, importer: RoleAssignmentImporter, exporter: RoleAssignmentExporter
    ):
        self._importer_exporter_list.append((importer, exporter))

    def process(self):

        for importer, exporter in self._importer_exporter_list:
            try:

                role_assignments = importer.import_role_assignments()

                exporter.export_role_assignments(role_assignments=role_assignments)
            except Exception as e:
                logger.warning(e)
                logger.warning("Skipping...")
