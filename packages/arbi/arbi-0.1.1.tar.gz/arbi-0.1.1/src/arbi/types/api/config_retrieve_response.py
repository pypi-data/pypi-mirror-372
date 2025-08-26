# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .embedder_config import EmbedderConfig
from .reranker_config import RerankerConfig
from .query_llm_config import QueryLlmConfig
from .retriever_config import RetrieverConfig
from .title_llm_config import TitleLlmConfig
from .model_citation_config import ModelCitationConfig
from .document_date_extractor_llm_config import DocumentDateExtractorLlmConfig

__all__ = ["ConfigRetrieveResponse", "AllConfigs", "NonDeveloperConfig"]


class AllConfigs(BaseModel):
    chunker: Optional[object] = FieldInfo(alias="Chunker", default=None)

    document_date_extractor_llm: Optional[DocumentDateExtractorLlmConfig] = FieldInfo(
        alias="DocumentDateExtractorLLM", default=None
    )

    embedder: Optional[EmbedderConfig] = FieldInfo(alias="Embedder", default=None)

    api_model_citation: Optional[ModelCitationConfig] = FieldInfo(alias="ModelCitation", default=None)

    parser: Optional[object] = FieldInfo(alias="Parser", default=None)

    query_llm: Optional[QueryLlmConfig] = FieldInfo(alias="QueryLLM", default=None)

    reranker: Optional[RerankerConfig] = FieldInfo(alias="Reranker", default=None)

    retriever: Optional[RetrieverConfig] = FieldInfo(alias="Retriever", default=None)

    title_llm: Optional[TitleLlmConfig] = FieldInfo(alias="TitleLLM", default=None)


class NonDeveloperConfig(BaseModel):
    query_llm: Dict[str, str] = FieldInfo(alias="QueryLLM")


ConfigRetrieveResponse: TypeAlias = Union[AllConfigs, NonDeveloperConfig]
