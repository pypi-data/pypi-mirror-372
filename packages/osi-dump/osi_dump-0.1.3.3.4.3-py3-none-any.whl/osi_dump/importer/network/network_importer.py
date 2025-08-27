from abc import ABC, abstractmethod

from osi_dump.model.network import Network


class NetworkImporter(ABC):
    @abstractmethod
    def import_networks(self) -> list[Network]:
        pass
