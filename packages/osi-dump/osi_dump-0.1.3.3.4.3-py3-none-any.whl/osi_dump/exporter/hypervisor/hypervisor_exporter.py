from abc import ABC, abstractmethod


class HypervisorExporter(ABC):
    @abstractmethod
    def export_hypervisors(self, hypervisors, output_file: str):
        pass
