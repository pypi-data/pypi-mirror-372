# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["WorkspaceGetStatsResponse"]


class WorkspaceGetStatsResponse(BaseModel):
    conversation_count: Optional[int] = None

    document_count: Optional[int] = None
