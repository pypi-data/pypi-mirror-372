from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


class Volume(BaseModel):
    model_config = ConfigDict(strict=True)

    volume_id: str

    project_id: Optional[str]

    volume_name: Optional[str]

    attachments: Optional[list[str]]

    status: str

    type: str
    size: int

    snapshots: Optional[list[str]]

    updated_at: Optional[str]
    created_at: Optional[str]
