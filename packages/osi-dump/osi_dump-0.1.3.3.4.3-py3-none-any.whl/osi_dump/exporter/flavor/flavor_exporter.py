from abc import ABC, abstractmethod


class FlavorExporter(ABC):
    @abstractmethod
    def export_flavors(self, flavors, output_file: str):
        pass
