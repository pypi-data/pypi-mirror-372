import pandas as pd

import logging

from openpyxl import load_workbook

from osi_dump import util
from osi_dump.exporter.project.project_exporter import ProjectExporter

from osi_dump.model.project import Project

logger = logging.getLogger(__name__)


class ExcelProjectExporter(ProjectExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_projects(self, projects: list[Project]):

        df = pd.DataFrame([project.model_dump() for project in projects])

        logger.info(f"Exporting projects for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported projects for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting projects for {self.sheet_name} error: {e}")
