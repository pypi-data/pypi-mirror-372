# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["SettingRetrieveResponse"]


class SettingRetrieveResponse(BaseModel):
    developer: Optional[bool] = None

    last_workspace: Optional[str] = None

    pinned_workspaces: Optional[List[str]] = None

    show_document_navigator: Optional[bool] = None

    show_help_page: Optional[bool] = None

    show_invite_tab: Optional[bool] = None

    show_security_settings: Optional[bool] = None

    show_smart_search: Optional[bool] = None

    show_thread_visualization: Optional[bool] = None

    __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    if TYPE_CHECKING:
        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
