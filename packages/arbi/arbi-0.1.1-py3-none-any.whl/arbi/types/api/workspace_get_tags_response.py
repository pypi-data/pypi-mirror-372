# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["WorkspaceGetTagsResponse", "Tag"]


class Tag(BaseModel):
    created_at: datetime

    created_by_ext_id: str

    name: str

    tag_ext_id: str

    type: str

    updated_at: datetime

    workspace_ext_id: str

    shared: Optional[bool] = None


class WorkspaceGetTagsResponse(BaseModel):
    tags: List[Tag]
