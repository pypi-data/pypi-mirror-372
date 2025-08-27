from abc import ABC, abstractmethod

from osi_dump.model.instance import Instance


class InstanceImporter(ABC):
    @abstractmethod
    def import_instances(self) -> list[Instance]:
        pass
