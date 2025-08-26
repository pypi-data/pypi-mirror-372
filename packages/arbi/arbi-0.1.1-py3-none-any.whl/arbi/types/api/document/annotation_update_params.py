# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["AnnotationUpdateParams"]


class AnnotationUpdateParams(TypedDict, total=False):
    doc_ext_id: Required[str]

    note: Optional[str]

    page_ref: Optional[int]
