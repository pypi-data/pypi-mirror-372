from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class Image(BaseModel):
    model_config = ConfigDict(strict=True)

    image_id: str

    disk_format: str
    min_disk: int
    min_ram: int
    image_name: Optional[str]
    owner: Optional[str]

    os_distro: Optional[str]
    properties: Optional[dict]

    protected: bool
    status: str
    size: Optional[int]
    virtual_size: Optional[int]
    visibility: str

    created_at: Optional[str]
    updated_at: Optional[str]
