from typing import Optional
from pydantic import BaseModel, ConfigDict



class Network(BaseModel):
    model_config = ConfigDict(strict=True)

    network_id: str
    project_id: str
    name: Optional[str]

    subnets: Optional[list[dict]] # {"id": str, "cidr": "str"}
    mtu: int  

    port_security_enabled: Optional[bool]

    network_type: str 
    segmentation_id: Optional[int]
    physical_network: Optional[str]

    status: Optional[str]
    shared: Optional[bool]

    created_at: Optional[str]
    updated_at: Optional[str] 