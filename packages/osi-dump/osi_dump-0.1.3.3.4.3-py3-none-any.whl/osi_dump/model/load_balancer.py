from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class LoadBalancer(BaseModel):
    model_config = ConfigDict(strict=True)

    id: str

    load_balancer_name: Optional[str]

    provisioning_status: Optional[str]

    operating_status: Optional[str]

    flavor_name: Optional[str]
    flavor_description: Optional[str]

    amphoraes: list[dict] # compute_id, compute_flavor_id, flavor_name, flavor_description
    vip: Optional[str]

    project_id: Optional[str]

    created_at: Optional[str]
    updated_at: Optional[str]
