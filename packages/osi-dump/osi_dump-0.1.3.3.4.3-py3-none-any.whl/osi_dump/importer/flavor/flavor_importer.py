from abc import ABC, abstractmethod

from osi_dump.model.flavor import Flavor


class FlavorImporter(ABC):
    @abstractmethod
    def import_flavors(self) -> list[Flavor]:
        pass
