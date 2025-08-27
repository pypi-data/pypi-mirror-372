from abc import ABC, abstractmethod


class FloatingIPExporter(ABC):
    @abstractmethod
    def export_floating_ips(self, floating_ips, output_file: str):
        pass
