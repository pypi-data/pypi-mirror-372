# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["DocTagResponse"]


class DocTagResponse(BaseModel):
    created_at: datetime

    created_by_ext_id: str

    doc_ext_id: str

    doctag_ext_id: str

    tag_ext_id: str

    updated_at: datetime

    note: Optional[str] = None

    page_ref: Optional[int] = None
