import pandas as pd

import logging

from openpyxl import load_workbook

from osi_dump import util
from osi_dump.exporter.instance.instance_exporter import InstanceExporter

from osi_dump.model.instance import Instance

logger = logging.getLogger(__name__)


class ExcelInstanceExporter(InstanceExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_instances(self, instances: list[Instance]):
        df = pd.DataFrame([instance.model_dump() for instance in instances])

        logger.info(f"Exporting instances for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported instances for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting instances for {self.sheet_name} error: {e}")
