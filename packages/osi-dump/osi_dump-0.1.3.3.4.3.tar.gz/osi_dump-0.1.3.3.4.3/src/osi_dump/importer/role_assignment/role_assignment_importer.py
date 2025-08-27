from abc import ABC, abstractmethod

from osi_dump.model.role_assignment import RoleAssignment


class RoleAssignmentImporter(ABC):
    @abstractmethod
    def import_role_assignments(self) -> list[RoleAssignment]:
        pass
