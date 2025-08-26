# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from ..._models import BaseModel

__all__ = ["TagRemoveFromDocsResponse"]


class TagRemoveFromDocsResponse(BaseModel):
    detail: str

    removed_doc_tag_ids: List[str]
