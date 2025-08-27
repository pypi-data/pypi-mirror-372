from abc import ABC, abstractmethod


class InstanceExporter(ABC):
    @abstractmethod
    def export_instances(self, instances, output_file: str):
        pass
