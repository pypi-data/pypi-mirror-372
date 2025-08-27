from abc import ABC, abstractmethod

from osi_dump.model.external_port import ExternalPort


class ExternalPortImporter(ABC):
    @abstractmethod
    def import_external_ports(self) -> list[ExternalPort]:
        pass
