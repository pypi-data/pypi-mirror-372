from abc import ABC, abstractmethod


class NetworkExporter(ABC):
    @abstractmethod
    def export_networks(self, networks, output_file: str):
        pass
