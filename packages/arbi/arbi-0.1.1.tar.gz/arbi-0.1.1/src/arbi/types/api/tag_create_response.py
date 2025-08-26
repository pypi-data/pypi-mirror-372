# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["TagCreateResponse"]


class TagCreateResponse(BaseModel):
    detail: str

    tag_id: str
