import logging

from openpyxl import load_workbook
import pandas as pd


from osi_dump.exporter.hypervisor.hypervisor_exporter import HypervisorExporter

from osi_dump.model.hypervisor import Hypervisor

from osi_dump import util

logger = logging.getLogger(__name__)


class ExcelHypervisorExporter(HypervisorExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_hypervisors(self, hypervisors: list[Hypervisor]):
        df = pd.DataFrame([hypervisor.model_dump() for hypervisor in hypervisors])

        df = util.expand_list_column(df, "aggregates")

        logger.info(f"Exporting hypervisors for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported hypervisors for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting hypervisors for {self.sheet_name} error: {e}")
