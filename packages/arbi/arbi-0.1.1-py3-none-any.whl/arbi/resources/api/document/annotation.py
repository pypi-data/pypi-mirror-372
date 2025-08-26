# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.api.document import annotation_create_params, annotation_update_params
from ....types.api.document.doc_tag_response import DocTagResponse
from ....types.api.document.annotation_delete_response import AnnotationDeleteResponse

__all__ = ["AnnotationResource", "AsyncAnnotationResource"]


class AnnotationResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AnnotationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AnnotationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AnnotationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AnnotationResourceWithStreamingResponse(self)

    def create(
        self,
        doc_ext_id: str,
        *,
        note: Optional[str] | NotGiven = NOT_GIVEN,
        page_ref: Optional[int] | NotGiven = NOT_GIVEN,
        tag_name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocTagResponse:
        """
        Create an annotation for a document.

        If tag_name is provided, uses existing tag or creates new one. If tag_name is
        not provided, auto-generates a system tag. The shared status inherits from
        document unless explicitly overridden.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        return self._post(
            f"/api/document/{doc_ext_id}/annotation",
            body=maybe_transform(
                {
                    "note": note,
                    "page_ref": page_ref,
                    "tag_name": tag_name,
                },
                annotation_create_params.AnnotationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    def update(
        self,
        doctag_ext_id: str,
        *,
        doc_ext_id: str,
        note: Optional[str] | NotGiven = NOT_GIVEN,
        page_ref: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocTagResponse:
        """
        Update an annotation (doctag) for a document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return self._patch(
            f"/api/document/{doc_ext_id}/annotation/{doctag_ext_id}",
            body=maybe_transform(
                {
                    "note": note,
                    "page_ref": page_ref,
                },
                annotation_update_params.AnnotationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    def delete(
        self,
        doctag_ext_id: str,
        *,
        doc_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnnotationDeleteResponse:
        """
        Delete a specific annotation (doctag) for a document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return self._delete(
            f"/api/document/{doc_ext_id}/annotation/{doctag_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnnotationDeleteResponse,
        )


class AsyncAnnotationResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAnnotationResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAnnotationResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAnnotationResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AsyncAnnotationResourceWithStreamingResponse(self)

    async def create(
        self,
        doc_ext_id: str,
        *,
        note: Optional[str] | NotGiven = NOT_GIVEN,
        page_ref: Optional[int] | NotGiven = NOT_GIVEN,
        tag_name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocTagResponse:
        """
        Create an annotation for a document.

        If tag_name is provided, uses existing tag or creates new one. If tag_name is
        not provided, auto-generates a system tag. The shared status inherits from
        document unless explicitly overridden.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        return await self._post(
            f"/api/document/{doc_ext_id}/annotation",
            body=await async_maybe_transform(
                {
                    "note": note,
                    "page_ref": page_ref,
                    "tag_name": tag_name,
                },
                annotation_create_params.AnnotationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    async def update(
        self,
        doctag_ext_id: str,
        *,
        doc_ext_id: str,
        note: Optional[str] | NotGiven = NOT_GIVEN,
        page_ref: Optional[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocTagResponse:
        """
        Update an annotation (doctag) for a document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return await self._patch(
            f"/api/document/{doc_ext_id}/annotation/{doctag_ext_id}",
            body=await async_maybe_transform(
                {
                    "note": note,
                    "page_ref": page_ref,
                },
                annotation_update_params.AnnotationUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    async def delete(
        self,
        doctag_ext_id: str,
        *,
        doc_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AnnotationDeleteResponse:
        """
        Delete a specific annotation (doctag) for a document.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_ext_id:
            raise ValueError(f"Expected a non-empty value for `doc_ext_id` but received {doc_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return await self._delete(
            f"/api/document/{doc_ext_id}/annotation/{doctag_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AnnotationDeleteResponse,
        )


class AnnotationResourceWithRawResponse:
    def __init__(self, annotation: AnnotationResource) -> None:
        self._annotation = annotation

        self.create = to_raw_response_wrapper(
            annotation.create,
        )
        self.update = to_raw_response_wrapper(
            annotation.update,
        )
        self.delete = to_raw_response_wrapper(
            annotation.delete,
        )


class AsyncAnnotationResourceWithRawResponse:
    def __init__(self, annotation: AsyncAnnotationResource) -> None:
        self._annotation = annotation

        self.create = async_to_raw_response_wrapper(
            annotation.create,
        )
        self.update = async_to_raw_response_wrapper(
            annotation.update,
        )
        self.delete = async_to_raw_response_wrapper(
            annotation.delete,
        )


class AnnotationResourceWithStreamingResponse:
    def __init__(self, annotation: AnnotationResource) -> None:
        self._annotation = annotation

        self.create = to_streamed_response_wrapper(
            annotation.create,
        )
        self.update = to_streamed_response_wrapper(
            annotation.update,
        )
        self.delete = to_streamed_response_wrapper(
            annotation.delete,
        )


class AsyncAnnotationResourceWithStreamingResponse:
    def __init__(self, annotation: AsyncAnnotationResource) -> None:
        self._annotation = annotation

        self.create = async_to_streamed_response_wrapper(
            annotation.create,
        )
        self.update = async_to_streamed_response_wrapper(
            annotation.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            annotation.delete,
        )
