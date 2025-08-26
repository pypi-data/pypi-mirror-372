# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["UserResponse"]


class UserResponse(BaseModel):
    email: Optional[str] = None

    external_id: Optional[str] = None

    last_name: Optional[str] = None

    name: Optional[str] = None

    public_key: Optional[str] = None
