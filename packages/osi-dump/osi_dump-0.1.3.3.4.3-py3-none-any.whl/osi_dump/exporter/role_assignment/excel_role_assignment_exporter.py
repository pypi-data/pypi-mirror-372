import pandas as pd

import logging


from osi_dump import util

from osi_dump.exporter.role_assignment.role_assignment_exporter import (
    RoleAssignmentExporter,
)

from osi_dump.model.role_assignment import RoleAssignment

logger = logging.getLogger(__name__)


class ExcelRoleAssignmentExporter(RoleAssignmentExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_role_assignments(self, role_assignments: list[RoleAssignment]):
        df = pd.json_normalize(
            [role_assignment.model_dump() for role_assignment in role_assignments]
        )

        logger.info(f"Exporting role_assignments for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported role_assignments for {self.sheet_name}")
        except Exception as e:
            logger.warning(
                f"Exporting role_assignments for {self.sheet_name} error: {e}"
            )
