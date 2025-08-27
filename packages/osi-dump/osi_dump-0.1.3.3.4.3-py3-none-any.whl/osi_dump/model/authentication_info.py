from typing import Optional

from pydantic import BaseModel, ConfigDict


class AuthenticationInfo(BaseModel):
    model_config = ConfigDict(strict=True)

    auth_url: str
    project_name: str
    username: str
    password: str
    user_domain_name: str
    project_domain_name: str
    interface: Optional[str] = "public"
