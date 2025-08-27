from abc import ABC, abstractmethod

from osi_dump.model.router import Router


class RouterImporter(ABC):
    @abstractmethod
    def import_routers(self) -> list[Router]:
        pass
