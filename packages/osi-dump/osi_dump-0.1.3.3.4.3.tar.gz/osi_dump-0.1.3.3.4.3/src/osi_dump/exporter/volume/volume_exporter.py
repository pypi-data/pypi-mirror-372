from abc import ABC, abstractmethod


class VolumeExporter(ABC):
    @abstractmethod
    def export_volumes(self, volumes, output_file: str):
        pass
