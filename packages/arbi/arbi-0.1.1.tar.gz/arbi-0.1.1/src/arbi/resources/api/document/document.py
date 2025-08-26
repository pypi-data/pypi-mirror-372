# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Mapping, Optional, cast
from datetime import date
from typing_extensions import Literal

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ...._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ...._compat import cached_property
from .annotation import (
    AnnotationResource,
    AsyncAnnotationResource,
    AnnotationResourceWithRawResponse,
    AsyncAnnotationResourceWithRawResponse,
    AnnotationResourceWithStreamingResponse,
    AsyncAnnotationResourceWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.api import document_view_params, document_update_params, document_upload_params
from ...._base_client import make_request_options
from ....types.api.doc_response import DocResponse
from ....types.api.document_delete_response import DocumentDeleteResponse
from ....types.api.document_update_response import DocumentUpdateResponse
from ....types.api.document_get_tags_response import DocumentGetTagsResponse
from ....types.api.document_get_parsed_response import DocumentGetParsedResponse

__all__ = ["DocumentResource", "AsyncDocumentResource"]


class DocumentResource(SyncAPIResource):
    @cached_property
    def annotation(self) -> AnnotationResource:
        return AnnotationResource(self._client)

    @cached_property
    def with_raw_response(self) -> DocumentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return DocumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return DocumentResourceWithStreamingResponse(self)

    def update(
        self,
        document_ext_id: str,
        *,
        doc_date: Union[str, date, None] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentUpdateResponse:
        """Update document metadata such as title, date, or sharing status.

        Changes are
        encrypted before storage in the database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return self._patch(
            f"/api/document/{document_ext_id}",
            body=maybe_transform(
                {
                    "doc_date": doc_date,
                    "shared": shared,
                    "title": title,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUpdateResponse,
        )

    def delete(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentDeleteResponse:
        """Delete a document by its external ID.

        Removes the document from both database
        and vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return self._delete(
            f"/api/document/{document_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentDeleteResponse,
        )

    def download(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Download a document by its external ID.

        Retrieves and decrypts the document for
        downloading as an attachment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return self._get(
            f"/api/document/{document_ext_id}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocResponse:
        """Retrieve document metadata by its external ID.

        Returns decrypted document
        information with proper access controls.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return self._get(
            f"/api/document/{document_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocResponse,
        )

    def get_parsed(
        self,
        stage: Literal["marker", "subchunk", "final"],
        *,
        document_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetParsedResponse:
        """Retrieve the full parsed document to be handled by the frontend.

        Only requires
        document_ext_id, workspace is determined through RLS.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not stage:
            raise ValueError(f"Expected a non-empty value for `stage` but received {stage!r}")
        return self._get(
            f"/api/document/{document_ext_id}/parsed-{stage}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetParsedResponse,
        )

    def get_tags(
        self,
        doc_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetTagsResponse:
        """
        Get all tags applied to a specific document along with doctag metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        return self._get(
            f"/api/document/{doc_ext_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetTagsResponse,
        )

    def upload(
        self,
        *,
        workspace_ext_id: str,
        files: List[FileTypes],
        config_ext_id: Optional[str] | NotGiven = NOT_GIVEN,
        shared: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Upload multiple documents to a workspace with encryption.

        Documents are queued
        for processing, parsed, and indexed for vector search.

        Args:
          files: Multiple files to upload

          config_ext_id: Configuration to use for processing

          shared: Whether the document should be shared with workspace members

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"files": files})
        extracted_files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/document/upload",
            body=maybe_transform(body, document_upload_params.DocumentUploadParams),
            files=extracted_files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "workspace_ext_id": workspace_ext_id,
                        "config_ext_id": config_ext_id,
                        "shared": shared,
                    },
                    document_upload_params.DocumentUploadParams,
                ),
            ),
            cast_to=object,
        )

    def view(
        self,
        document_ext_id: str,
        *,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """View a document inline in the browser.

        Retrieves and decrypts the document for
        inline viewing with optional page specification.

        Args:
          page: Optional page to open on load

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return self._get(
            f"/api/document/{document_ext_id}/view",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"page": page}, document_view_params.DocumentViewParams),
            ),
            cast_to=object,
        )


class AsyncDocumentResource(AsyncAPIResource):
    @cached_property
    def annotation(self) -> AsyncAnnotationResource:
        return AsyncAnnotationResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDocumentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AsyncDocumentResourceWithStreamingResponse(self)

    async def update(
        self,
        document_ext_id: str,
        *,
        doc_date: Union[str, date, None] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        title: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentUpdateResponse:
        """Update document metadata such as title, date, or sharing status.

        Changes are
        encrypted before storage in the database.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return await self._patch(
            f"/api/document/{document_ext_id}",
            body=await async_maybe_transform(
                {
                    "doc_date": doc_date,
                    "shared": shared,
                    "title": title,
                },
                document_update_params.DocumentUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentUpdateResponse,
        )

    async def delete(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentDeleteResponse:
        """Delete a document by its external ID.

        Removes the document from both database
        and vector store.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return await self._delete(
            f"/api/document/{document_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentDeleteResponse,
        )

    async def download(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Download a document by its external ID.

        Retrieves and decrypts the document for
        downloading as an attachment.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return await self._get(
            f"/api/document/{document_ext_id}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get(
        self,
        document_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocResponse:
        """Retrieve document metadata by its external ID.

        Returns decrypted document
        information with proper access controls.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return await self._get(
            f"/api/document/{document_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocResponse,
        )

    async def get_parsed(
        self,
        stage: Literal["marker", "subchunk", "final"],
        *,
        document_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetParsedResponse:
        """Retrieve the full parsed document to be handled by the frontend.

        Only requires
        document_ext_id, workspace is determined through RLS.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not stage:
            raise ValueError(f"Expected a non-empty value for `stage` but received {stage!r}")
        return await self._get(
            f"/api/document/{document_ext_id}/parsed-{stage}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetParsedResponse,
        )

    async def get_tags(
        self,
        doc_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetTagsResponse:
        """
        Get all tags applied to a specific document along with doctag metadata.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        return await self._get(
            f"/api/document/{doc_ext_id}/tags",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetTagsResponse,
        )

    async def upload(
        self,
        *,
        workspace_ext_id: str,
        files: List[FileTypes],
        config_ext_id: Optional[str] | NotGiven = NOT_GIVEN,
        shared: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Upload multiple documents to a workspace with encryption.

        Documents are queued
        for processing, parsed, and indexed for vector search.

        Args:
          files: Multiple files to upload

          config_ext_id: Configuration to use for processing

          shared: Whether the document should be shared with workspace members

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal({"files": files})
        extracted_files = extract_files(cast(Mapping[str, object], body), paths=[["files", "<array>"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/document/upload",
            body=await async_maybe_transform(body, document_upload_params.DocumentUploadParams),
            files=extracted_files,
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "workspace_ext_id": workspace_ext_id,
                        "config_ext_id": config_ext_id,
                        "shared": shared,
                    },
                    document_upload_params.DocumentUploadParams,
                ),
            ),
            cast_to=object,
        )

    async def view(
        self,
        document_ext_id: str,
        *,
        page: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """View a document inline in the browser.

        Retrieves and decrypts the document for
        inline viewing with optional page specification.

        Args:
          page: Optional page to open on load

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        return await self._get(
            f"/api/document/{document_ext_id}/view",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"page": page}, document_view_params.DocumentViewParams),
            ),
            cast_to=object,
        )


class DocumentResourceWithRawResponse:
    def __init__(self, document: DocumentResource) -> None:
        self._document = document

        self.update = to_raw_response_wrapper(
            document.update,
        )
        self.delete = to_raw_response_wrapper(
            document.delete,
        )
        self.download = to_raw_response_wrapper(
            document.download,
        )
        self.get = to_raw_response_wrapper(
            document.get,
        )
        self.get_parsed = to_raw_response_wrapper(
            document.get_parsed,
        )
        self.get_tags = to_raw_response_wrapper(
            document.get_tags,
        )
        self.upload = to_raw_response_wrapper(
            document.upload,
        )
        self.view = to_raw_response_wrapper(
            document.view,
        )

    @cached_property
    def annotation(self) -> AnnotationResourceWithRawResponse:
        return AnnotationResourceWithRawResponse(self._document.annotation)


class AsyncDocumentResourceWithRawResponse:
    def __init__(self, document: AsyncDocumentResource) -> None:
        self._document = document

        self.update = async_to_raw_response_wrapper(
            document.update,
        )
        self.delete = async_to_raw_response_wrapper(
            document.delete,
        )
        self.download = async_to_raw_response_wrapper(
            document.download,
        )
        self.get = async_to_raw_response_wrapper(
            document.get,
        )
        self.get_parsed = async_to_raw_response_wrapper(
            document.get_parsed,
        )
        self.get_tags = async_to_raw_response_wrapper(
            document.get_tags,
        )
        self.upload = async_to_raw_response_wrapper(
            document.upload,
        )
        self.view = async_to_raw_response_wrapper(
            document.view,
        )

    @cached_property
    def annotation(self) -> AsyncAnnotationResourceWithRawResponse:
        return AsyncAnnotationResourceWithRawResponse(self._document.annotation)


class DocumentResourceWithStreamingResponse:
    def __init__(self, document: DocumentResource) -> None:
        self._document = document

        self.update = to_streamed_response_wrapper(
            document.update,
        )
        self.delete = to_streamed_response_wrapper(
            document.delete,
        )
        self.download = to_streamed_response_wrapper(
            document.download,
        )
        self.get = to_streamed_response_wrapper(
            document.get,
        )
        self.get_parsed = to_streamed_response_wrapper(
            document.get_parsed,
        )
        self.get_tags = to_streamed_response_wrapper(
            document.get_tags,
        )
        self.upload = to_streamed_response_wrapper(
            document.upload,
        )
        self.view = to_streamed_response_wrapper(
            document.view,
        )

    @cached_property
    def annotation(self) -> AnnotationResourceWithStreamingResponse:
        return AnnotationResourceWithStreamingResponse(self._document.annotation)


class AsyncDocumentResourceWithStreamingResponse:
    def __init__(self, document: AsyncDocumentResource) -> None:
        self._document = document

        self.update = async_to_streamed_response_wrapper(
            document.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            document.delete,
        )
        self.download = async_to_streamed_response_wrapper(
            document.download,
        )
        self.get = async_to_streamed_response_wrapper(
            document.get,
        )
        self.get_parsed = async_to_streamed_response_wrapper(
            document.get_parsed,
        )
        self.get_tags = async_to_streamed_response_wrapper(
            document.get_tags,
        )
        self.upload = async_to_streamed_response_wrapper(
            document.upload,
        )
        self.view = async_to_streamed_response_wrapper(
            document.view,
        )

    @cached_property
    def annotation(self) -> AsyncAnnotationResourceWithStreamingResponse:
        return AsyncAnnotationResourceWithStreamingResponse(self._document.annotation)
