import logging

from openpyxl import load_workbook
import pandas as pd


from osi_dump.exporter.floating_ip.floating_ip_exporter import FloatingIPExporter

from osi_dump.model.floating_ip import FloatingIP

from osi_dump import util

logger = logging.getLogger(__name__)


class ExcelFloatingIPExporter(FloatingIPExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_floating_ips(self, floating_ips: list[FloatingIP]):
        df = pd.DataFrame([floating_ip.model_dump() for floating_ip in floating_ips])

        logger.info(f"Exporting floating ips for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported floating ips for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting floating ips for {self.sheet_name} error: {e}")
