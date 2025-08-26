# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["EmbedderConfig"]


class EmbedderConfig(BaseModel):
    api_type: Optional[Literal["local", "remote"]] = FieldInfo(alias="API_TYPE", default=None)
    """The inference type (local or remote)."""

    api_model_name: Optional[str] = FieldInfo(alias="MODEL_NAME", default=None)
    """The name of the embedder model."""
