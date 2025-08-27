from abc import ABC, abstractmethod

from osi_dump.model.hypervisor import Hypervisor


class HypervisorImporter(ABC):
    @abstractmethod
    def import_hypervisors(self) -> list[Hypervisor]:
        pass
