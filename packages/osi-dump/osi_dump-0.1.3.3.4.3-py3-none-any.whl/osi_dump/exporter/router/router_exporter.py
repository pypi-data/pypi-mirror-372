from abc import ABC, abstractmethod


class RouterExporter(ABC):
    @abstractmethod
    def export_routers(self, routers, output_file: str):
        pass
