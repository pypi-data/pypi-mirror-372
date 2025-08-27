import pandas as pd

import logging


from osi_dump import util

from osi_dump.exporter.load_balancer.load_balancer_exporter import (
    LoadBalancerExporter,
)

from osi_dump.model.load_balancer import LoadBalancer

logger = logging.getLogger(__name__)


class ExcelLoadBalancerExporter(LoadBalancerExporter):
    def __init__(self, sheet_name: str, output_file: str):
        self.sheet_name = sheet_name
        self.output_file = output_file

    def export_load_balancers(self, load_balancers: list[LoadBalancer]):
        df = pd.json_normalize(
            [load_balancer.model_dump() for load_balancer in load_balancers]
        )

        if "amphoraes" in df.columns:
            df = util.expand_list_column(df, "amphoraes")

        logger.info(f"Exporting load_balancers for {self.sheet_name}")
        try:
            util.export_data_excel(self.output_file, sheet_name=self.sheet_name, df=df)

            logger.info(f"Exported load_balancers for {self.sheet_name}")
        except Exception as e:
            logger.warning(f"Exporting load_balancers for {self.sheet_name} error: {e}")
