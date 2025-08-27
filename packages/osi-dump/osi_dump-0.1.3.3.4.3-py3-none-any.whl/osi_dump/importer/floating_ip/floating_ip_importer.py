from abc import ABC, abstractmethod

from osi_dump.model.floating_ip import FloatingIP


class FloatingIPImporter(ABC):
    @abstractmethod
    def import_floating_ips(self) -> list[FloatingIP]:
        pass
