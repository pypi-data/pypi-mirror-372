# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["SSOLoginParams"]


class SSOLoginParams(TypedDict, total=False):
    token: Required[str]

    email: Required[str]

    passcode: Optional[str]
