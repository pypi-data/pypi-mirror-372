import pandas as pd

import logging

from openpyxl import load_workbook

from osi_dump import util
from osi_dump.exporter.external_port.external_port_exporter import ExternalPortExporter

from osi_dump.model.external_port import ExternalPort

logger = logging.getLogger(__name__)


class ExcelExternalPortExporter(ExternalPortExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_external_ports(self, external_ports: list[ExternalPort]):

        df = pd.DataFrame(
            [external_port.model_dump() for external_port in external_ports]
        )

        df = util.panda_excel.expand_list_column(df, "allowed_address_pairs")

        logger.info(f"Exporting external_ports for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported external_ports for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting external_ports for {self.sheet_name} error: {e}")
