from abc import ABC, abstractmethod


class RoleAssignmentExporter(ABC):
    @abstractmethod
    def export_role_assignments(self, role_assignments, output_file: str):
        pass
