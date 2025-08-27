from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class ExternalPort(BaseModel):
    model_config = ConfigDict(strict=True)

    port_id: str

    project_id: Optional[str]

    subnet_id: Optional[str]

    subnet_cidr: Optional[str]

    ip_address: Optional[str]

    network_name: Optional[str]
    network_id: Optional[str]

    allowed_address_pairs: Optional[list[dict]]

    device_id: Optional[str]

    device_owner: Optional[str]

    status: Optional[str]
    
    vlan_id: Optional[int]
