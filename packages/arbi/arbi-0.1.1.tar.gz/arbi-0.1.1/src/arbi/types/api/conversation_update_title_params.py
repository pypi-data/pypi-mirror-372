# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ConversationUpdateTitleParams"]


class ConversationUpdateTitleParams(TypedDict, total=False):
    title: Required[str]
    """New conversation title (1-60 characters)"""
