from abc import ABC, abstractmethod


class LoadBalancerExporter(ABC):
    @abstractmethod
    def export_load_balancers(self, load_balancers, output_file: str):
        pass
