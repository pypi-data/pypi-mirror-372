# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from ..._models import BaseModel

__all__ = ["Token"]


class Token(BaseModel):
    access_token: str

    token_type: str

    user_ext_id: str
