from abc import ABC, abstractmethod

from osi_dump.model.project import Project


class ProjectImporter(ABC):
    @abstractmethod
    def import_projects(self) -> list[Project]:
        pass
