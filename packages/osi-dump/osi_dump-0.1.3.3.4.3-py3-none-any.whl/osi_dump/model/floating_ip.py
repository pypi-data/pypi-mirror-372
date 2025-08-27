from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class FloatingIP(BaseModel):
    model_config = ConfigDict(strict=True)

    floating_ip_id: str
    project_id: Optional[str]

    floating_network: str

    floating_ip_address: str

    fixed_ip_address: Optional[str]

    router_id: Optional[str]

    port_id: Optional[str]

    status: str
    created_at: str
    updated_at: str
