from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class Project(BaseModel):
    model_config = ConfigDict(strict=True)

    project_id: str
    project_name: Optional[str]
    domain_id: Optional[str]
    domain_name: Optional[str]
    enabled: bool
    parent_id: Optional[str]

    usage_instance: Optional[int]
    quota_instance: Optional[int]

    usage_vcpu: Optional[int]
    quota_vcpu: Optional[int]

    usage_ram: Optional[int]
    quota_ram: Optional[int]

    usage_volume: Optional[int]
    quota_volume: Optional[int]

    usage_snapshot: Optional[int]
    quota_snapshot: Optional[int]

    usage_storage: Optional[int]
    quota_storage: Optional[int]

    load_balancer_count: Optional[int]