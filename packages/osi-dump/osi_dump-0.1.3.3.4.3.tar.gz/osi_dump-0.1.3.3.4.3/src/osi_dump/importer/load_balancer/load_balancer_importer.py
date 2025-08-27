from abc import ABC, abstractmethod

from osi_dump.model.load_balancer import LoadBalancer


class LoadBalancerImporter(ABC):
    @abstractmethod
    def import_load_balancers(self) -> list[LoadBalancer]:
        pass
