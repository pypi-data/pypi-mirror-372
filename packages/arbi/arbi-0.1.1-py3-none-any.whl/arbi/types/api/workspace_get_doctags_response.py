# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .document.doc_tag_response import DocTagResponse

__all__ = ["WorkspaceGetDoctagsResponse"]

WorkspaceGetDoctagsResponse: TypeAlias = List[DocTagResponse]
