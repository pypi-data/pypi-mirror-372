from abc import ABC, abstractmethod


class ProjectExporter(ABC):
    @abstractmethod
    def export_projects(self, projects, output_file: str):
        pass
