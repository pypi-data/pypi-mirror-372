from abc import ABC, abstractmethod

from osi_dump.model.volume import Volume


class VolumeImporter(ABC):
    @abstractmethod
    def import_volumes(self) -> list[Volume]:
        pass
