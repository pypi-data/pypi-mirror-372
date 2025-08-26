# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date

from ..._models import BaseModel

__all__ = ["DocumentUpdateResponse"]


class DocumentUpdateResponse(BaseModel):
    external_id: str

    success: bool

    title: str

    detail: Optional[str] = None

    doc_date: Optional[date] = None

    shared: Optional[bool] = None
