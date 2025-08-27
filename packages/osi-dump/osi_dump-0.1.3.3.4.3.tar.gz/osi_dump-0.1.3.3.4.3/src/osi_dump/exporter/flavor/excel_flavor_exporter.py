import logging


import pandas as pd


from osi_dump.exporter.flavor.flavor_exporter import FlavorExporter

from osi_dump.model.flavor import Flavor

from osi_dump import util

logger = logging.getLogger(__name__)


class ExcelFlavorExporter(FlavorExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_flavors(self, flavors: list[Flavor]):
        df = pd.json_normalize([flavor.model_dump() for flavor in flavors])

        logger.info(f"Exporting flavors for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported flavors for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting flavors for {self.sheet_name} error: {e}")
