# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["AnnotationCreateParams"]


class AnnotationCreateParams(TypedDict, total=False):
    note: Optional[str]

    page_ref: Optional[int]

    tag_name: Optional[str]
