# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .parser_config_param import ParserConfigParam
from .chunker_config_param import ChunkerConfigParam
from .embedder_config_param import EmbedderConfigParam
from .reranker_config_param import RerankerConfigParam
from .query_llm_config_param import QueryLlmConfigParam
from .retriever_config_param import RetrieverConfigParam
from .title_llm_config_param import TitleLlmConfigParam
from .model_citation_config_param import ModelCitationConfigParam
from .document_date_extractor_llm_config_param import DocumentDateExtractorLlmConfigParam

__all__ = ["ConfigCreateParams"]


class ConfigCreateParams(TypedDict, total=False):
    chunker: Annotated[Optional[ChunkerConfigParam], PropertyInfo(alias="Chunker")]

    document_date_extractor_llm: Annotated[
        Optional[DocumentDateExtractorLlmConfigParam], PropertyInfo(alias="DocumentDateExtractorLLM")
    ]

    embedder: Annotated[Optional[EmbedderConfigParam], PropertyInfo(alias="Embedder")]

    model_citation: Annotated[Optional[ModelCitationConfigParam], PropertyInfo(alias="ModelCitation")]

    parent_message_ext_id: Optional[str]

    parser: Annotated[Optional[ParserConfigParam], PropertyInfo(alias="Parser")]

    query_llm: Annotated[Optional[QueryLlmConfigParam], PropertyInfo(alias="QueryLLM")]

    reranker: Annotated[Optional[RerankerConfigParam], PropertyInfo(alias="Reranker")]

    retriever: Annotated[Optional[RetrieverConfigParam], PropertyInfo(alias="Retriever")]

    title: str

    title_llm: Annotated[Optional[TitleLlmConfigParam], PropertyInfo(alias="TitleLLM")]
