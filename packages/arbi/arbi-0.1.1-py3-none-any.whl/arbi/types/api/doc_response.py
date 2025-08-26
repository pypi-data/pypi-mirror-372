# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import date, datetime

from ..._models import BaseModel

__all__ = ["DocResponse"]


class DocResponse(BaseModel):
    created_at: datetime

    external_id: str

    title: str

    updated_at: datetime

    workspace_ext_id: str

    config_ext_id: Optional[str] = None

    created_by_ext_id: Optional[str] = None

    doc_date: Optional[date] = None

    file_name: Optional[str] = None

    file_size: Optional[int] = None

    file_type: Optional[str] = None

    n_chunks: Optional[int] = None

    n_pages: Optional[int] = None

    re_ocred: Optional[bool] = None

    shared: Optional[bool] = None

    status: Optional[str] = None

    storage_type: Optional[str] = None

    storage_uri: Optional[str] = None

    tokens: Optional[int] = None
