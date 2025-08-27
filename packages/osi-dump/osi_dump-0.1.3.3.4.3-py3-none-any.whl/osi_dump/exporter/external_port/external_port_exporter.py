from abc import ABC, abstractmethod


class ExternalPortExporter(ABC):
    @abstractmethod
    def export_external_ports(self, projects, output_file: str):
        pass
