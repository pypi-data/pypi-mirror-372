# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.api import tag_create_params, tag_update_params, tag_apply_to_docs_params, tag_remove_from_docs_params
from ..._base_client import make_request_options
from ...types.api.tag_create_response import TagCreateResponse
from ...types.api.tag_delete_response import TagDeleteResponse
from ...types.api.tag_update_response import TagUpdateResponse
from ...types.api.tag_get_docs_response import TagGetDocsResponse
from ...types.api.tag_apply_to_docs_response import TagApplyToDocsResponse
from ...types.api.tag_remove_from_docs_response import TagRemoveFromDocsResponse

__all__ = ["TagResource", "AsyncTagResource"]


class TagResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TagResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return TagResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TagResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return TagResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        workspace_ext_id: str,
        parent_ext_id: Optional[str] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagCreateResponse:
        """
        Create a new tag for a given workspace.

        If 'shared' is provided, the tag will be set to shared or private accordingly.
        If 'shared' is not provided, it defaults to True (shared).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/tag/create",
            body=maybe_transform(
                {
                    "name": name,
                    "workspace_ext_id": workspace_ext_id,
                    "parent_ext_id": parent_ext_id,
                    "shared": shared,
                },
                tag_create_params.TagCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagCreateResponse,
        )

    def update(
        self,
        tag_ext_id: str,
        *,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagUpdateResponse:
        """
        Update a tag by its external ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return self._patch(
            f"/api/tag/{tag_ext_id}",
            body=maybe_transform(
                {
                    "name": name,
                    "shared": shared,
                },
                tag_update_params.TagUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagUpdateResponse,
        )

    def delete(
        self,
        tag_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagDeleteResponse:
        """
        Delete a tag by its external ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return self._delete(
            f"/api/tag/{tag_ext_id}/delete",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagDeleteResponse,
        )

    def apply_to_docs(
        self,
        tag_ext_id: str,
        *,
        doc_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagApplyToDocsResponse:
        """
        Apply a tag to a list of documents.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return self._post(
            f"/api/tag/{tag_ext_id}/apply",
            body=maybe_transform({"doc_ids": doc_ids}, tag_apply_to_docs_params.TagApplyToDocsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagApplyToDocsResponse,
        )

    def get_docs(
        self,
        tag_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagGetDocsResponse:
        """
        Get all doctags for a given tag.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return self._get(
            f"/api/tag/{tag_ext_id}/docs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagGetDocsResponse,
        )

    def remove_from_docs(
        self,
        tag_ext_id: str,
        *,
        doc_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagRemoveFromDocsResponse:
        """
        Remove a tag from a list of documents.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return self._delete(
            f"/api/tag/{tag_ext_id}/remove",
            body=maybe_transform({"doc_ids": doc_ids}, tag_remove_from_docs_params.TagRemoveFromDocsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagRemoveFromDocsResponse,
        )


class AsyncTagResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTagResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTagResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTagResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AsyncTagResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        workspace_ext_id: str,
        parent_ext_id: Optional[str] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagCreateResponse:
        """
        Create a new tag for a given workspace.

        If 'shared' is provided, the tag will be set to shared or private accordingly.
        If 'shared' is not provided, it defaults to True (shared).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/tag/create",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "workspace_ext_id": workspace_ext_id,
                    "parent_ext_id": parent_ext_id,
                    "shared": shared,
                },
                tag_create_params.TagCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagCreateResponse,
        )

    async def update(
        self,
        tag_ext_id: str,
        *,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        shared: Optional[bool] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagUpdateResponse:
        """
        Update a tag by its external ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return await self._patch(
            f"/api/tag/{tag_ext_id}",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "shared": shared,
                },
                tag_update_params.TagUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagUpdateResponse,
        )

    async def delete(
        self,
        tag_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagDeleteResponse:
        """
        Delete a tag by its external ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return await self._delete(
            f"/api/tag/{tag_ext_id}/delete",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagDeleteResponse,
        )

    async def apply_to_docs(
        self,
        tag_ext_id: str,
        *,
        doc_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagApplyToDocsResponse:
        """
        Apply a tag to a list of documents.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return await self._post(
            f"/api/tag/{tag_ext_id}/apply",
            body=await async_maybe_transform({"doc_ids": doc_ids}, tag_apply_to_docs_params.TagApplyToDocsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagApplyToDocsResponse,
        )

    async def get_docs(
        self,
        tag_ext_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagGetDocsResponse:
        """
        Get all doctags for a given tag.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return await self._get(
            f"/api/tag/{tag_ext_id}/docs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagGetDocsResponse,
        )

    async def remove_from_docs(
        self,
        tag_ext_id: str,
        *,
        doc_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TagRemoveFromDocsResponse:
        """
        Remove a tag from a list of documents.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tag_ext_id:
            raise ValueError(f"Expected a non-empty value for `tag_ext_id` but received {tag_ext_id!r}")
        return await self._delete(
            f"/api/tag/{tag_ext_id}/remove",
            body=await async_maybe_transform({"doc_ids": doc_ids}, tag_remove_from_docs_params.TagRemoveFromDocsParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TagRemoveFromDocsResponse,
        )


class TagResourceWithRawResponse:
    def __init__(self, tag: TagResource) -> None:
        self._tag = tag

        self.create = to_raw_response_wrapper(
            tag.create,
        )
        self.update = to_raw_response_wrapper(
            tag.update,
        )
        self.delete = to_raw_response_wrapper(
            tag.delete,
        )
        self.apply_to_docs = to_raw_response_wrapper(
            tag.apply_to_docs,
        )
        self.get_docs = to_raw_response_wrapper(
            tag.get_docs,
        )
        self.remove_from_docs = to_raw_response_wrapper(
            tag.remove_from_docs,
        )


class AsyncTagResourceWithRawResponse:
    def __init__(self, tag: AsyncTagResource) -> None:
        self._tag = tag

        self.create = async_to_raw_response_wrapper(
            tag.create,
        )
        self.update = async_to_raw_response_wrapper(
            tag.update,
        )
        self.delete = async_to_raw_response_wrapper(
            tag.delete,
        )
        self.apply_to_docs = async_to_raw_response_wrapper(
            tag.apply_to_docs,
        )
        self.get_docs = async_to_raw_response_wrapper(
            tag.get_docs,
        )
        self.remove_from_docs = async_to_raw_response_wrapper(
            tag.remove_from_docs,
        )


class TagResourceWithStreamingResponse:
    def __init__(self, tag: TagResource) -> None:
        self._tag = tag

        self.create = to_streamed_response_wrapper(
            tag.create,
        )
        self.update = to_streamed_response_wrapper(
            tag.update,
        )
        self.delete = to_streamed_response_wrapper(
            tag.delete,
        )
        self.apply_to_docs = to_streamed_response_wrapper(
            tag.apply_to_docs,
        )
        self.get_docs = to_streamed_response_wrapper(
            tag.get_docs,
        )
        self.remove_from_docs = to_streamed_response_wrapper(
            tag.remove_from_docs,
        )


class AsyncTagResourceWithStreamingResponse:
    def __init__(self, tag: AsyncTagResource) -> None:
        self._tag = tag

        self.create = async_to_streamed_response_wrapper(
            tag.create,
        )
        self.update = async_to_streamed_response_wrapper(
            tag.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            tag.delete,
        )
        self.apply_to_docs = async_to_streamed_response_wrapper(
            tag.apply_to_docs,
        )
        self.get_docs = async_to_streamed_response_wrapper(
            tag.get_docs,
        )
        self.remove_from_docs = async_to_streamed_response_wrapper(
            tag.remove_from_docs,
        )
