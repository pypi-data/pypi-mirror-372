# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..chunk_param import ChunkParam

__all__ = [
    "AssistantRetrieveParams",
    "Tools",
    "ToolsModelCitationTool",
    "ToolsRetrievalChunkToolInput",
    "ToolsRetrievalFullContextToolInput",
]


class AssistantRetrieveParams(TypedDict, total=False):
    content: Required[str]

    workspace_ext_id: Required[str]

    config_ext_id: Optional[str]

    parent_message_ext_id: Optional[str]

    tools: Dict[str, Tools]


class ToolsModelCitationTool(TypedDict, total=False):
    description: str

    name: Literal["model_citation"]

    tool_responses: Dict[str, List[str]]


class ToolsRetrievalChunkToolInput(TypedDict, total=False):
    description: str

    name: Literal["retrieval_chunk"]

    tool_args: Dict[str, List[str]]

    tool_responses: Dict[str, Iterable[ChunkParam]]


class ToolsRetrievalFullContextToolInput(TypedDict, total=False):
    description: str

    name: Literal["retrieval_full_context"]

    tool_args: Dict[str, List[str]]

    tool_responses: Dict[str, Iterable[ChunkParam]]


Tools: TypeAlias = Union[ToolsModelCitationTool, ToolsRetrievalChunkToolInput, ToolsRetrievalFullContextToolInput]
