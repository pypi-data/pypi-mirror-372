# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypeAlias

from ..chunk import Chunk
from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "ConversationRetrieveThreadsResponse",
    "Thread",
    "ThreadHistory",
    "ThreadHistoryTools",
    "ThreadHistoryToolsModelCitationTool",
    "ThreadHistoryToolsRetrievalChunkToolOutput",
    "ThreadHistoryToolsRetrievalFullContextToolOutput",
]


class ThreadHistoryToolsModelCitationTool(BaseModel):
    description: Optional[str] = None

    name: Optional[Literal["model_citation"]] = None

    tool_responses: Optional[Dict[str, List[str]]] = None


class ThreadHistoryToolsRetrievalChunkToolOutput(BaseModel):
    description: Optional[str] = None

    name: Optional[Literal["retrieval_chunk"]] = None

    tool_args: Optional[Dict[str, List[str]]] = None

    tool_responses: Optional[Dict[str, List[Chunk]]] = None


class ThreadHistoryToolsRetrievalFullContextToolOutput(BaseModel):
    description: Optional[str] = None

    name: Optional[Literal["retrieval_full_context"]] = None

    tool_args: Optional[Dict[str, List[str]]] = None

    tool_responses: Optional[Dict[str, List[Chunk]]] = None


ThreadHistoryTools: TypeAlias = Annotated[
    Union[
        ThreadHistoryToolsModelCitationTool,
        ThreadHistoryToolsRetrievalChunkToolOutput,
        ThreadHistoryToolsRetrievalFullContextToolOutput,
    ],
    PropertyInfo(discriminator="name"),
]


class ThreadHistory(BaseModel):
    content: str

    conversation_ext_id: str

    created_at: datetime

    created_by_ext_id: str

    external_id: str

    role: Literal["user", "assistant", "system"]

    config_ext_id: Optional[str] = None

    parent_message_ext_id: Optional[str] = None

    shared: Optional[bool] = None

    tools: Optional[Dict[str, ThreadHistoryTools]] = None


class Thread(BaseModel):
    history: List[ThreadHistory]

    leaf_message_ext_id: str


class ConversationRetrieveThreadsResponse(BaseModel):
    conversation_ext_id: str

    threads: List[Thread]
