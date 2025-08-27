import logging


import pandas as pd


from osi_dump.exporter.network.network_exporter import NetworkExporter 

from osi_dump.model.network import Network 

from osi_dump import util

logger = logging.getLogger(__name__)


class ExcelNetworkExporter(NetworkExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_networks(self, networks: list[Network]):
        df = pd.json_normalize([network.model_dump() for network in networks])
        
        df = util.expand_list_column(df, "subnets")

        logger.info(f"Exporting networks for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported networks for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting networks for {self.sheet_name} error: {e}")
