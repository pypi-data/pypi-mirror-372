# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["TagUpdateResponse"]


class TagUpdateResponse(BaseModel):
    detail: str

    tag_id: str

    name: Optional[str] = None

    shared: Optional[bool] = None
