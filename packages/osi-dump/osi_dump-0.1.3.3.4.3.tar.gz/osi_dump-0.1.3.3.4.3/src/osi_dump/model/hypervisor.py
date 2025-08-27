from typing import Optional
from pydantic import BaseModel, ConfigDict, ValidationError


class Hypervisor(BaseModel):
    hypervisor_id: str
    hypervisor_type: str
    name: str
    state: str
    status: str

    vcpus: int
    vcpus_usage: int

    memory_size: int
    memory_usage: int

    local_disk_usage: int
    local_disk_size: int

    aggregates: Optional[list[dict]]  # id, name, az
    availability_zone: Optional[str]

    vm_count: int
