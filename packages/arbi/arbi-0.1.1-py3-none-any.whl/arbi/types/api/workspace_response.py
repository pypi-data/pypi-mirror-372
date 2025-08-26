# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["WorkspaceResponse"]


class WorkspaceResponse(BaseModel):
    created_at: datetime

    created_by_ext_id: str

    description: Optional[str] = None

    external_id: str

    name: str

    updated_at: datetime

    updated_by_ext_id: Optional[str] = None
