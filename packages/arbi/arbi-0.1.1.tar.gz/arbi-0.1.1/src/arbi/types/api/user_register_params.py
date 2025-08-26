# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserRegisterParams"]


class UserRegisterParams(TypedDict, total=False):
    email: Required[str]

    last_name: Required[str]

    name: Required[str]

    password: Required[str]
