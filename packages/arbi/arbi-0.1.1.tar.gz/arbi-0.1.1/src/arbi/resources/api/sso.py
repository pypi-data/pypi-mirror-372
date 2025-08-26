# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

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
from ...types.api import sso_login_params, sso_invite_params
from ..._base_client import make_request_options
from ...types.api.sso_login_response import SSOLoginResponse
from ...types.api.sso_invite_response import SSOInviteResponse
from ...types.api.sso_rotate_passcode_response import SSORotatePasscodeResponse

__all__ = ["SSOResource", "AsyncSSOResource"]


class SSOResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SSOResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return SSOResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SSOResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return SSOResourceWithStreamingResponse(self)

    def invite(
        self,
        *,
        email: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSOInviteResponse:
        """Invite a user to the deployment via email.

        Creates a pre-registered user account
        with blocked status and no sub field. The central server will send the user an
        invitation email with a passcode.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/sso/invite",
            body=maybe_transform({"email": email}, sso_invite_params.SSOInviteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSOInviteResponse,
        )

    def login(
        self,
        *,
        token: str,
        email: str,
        passcode: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSOLoginResponse:
        """Handle SSO login with JWT token authentication.

        Creates a new user account if
        needed or validates existing user credentials.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/sso/login",
            body=maybe_transform(
                {
                    "token": token,
                    "email": email,
                    "passcode": passcode,
                },
                sso_login_params.SSOLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSOLoginResponse,
        )

    def rotate_passcode(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSORotatePasscodeResponse:
        """
        Generate a new passcode for the current user.

        This endpoint gets a new passcode from the central server and re-wraps the
        user's private key with the new passcode. The user must be authenticated with a
        valid token to use this endpoint.
        """
        return self._post(
            "/api/sso/rotate_passcode",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSORotatePasscodeResponse,
        )


class AsyncSSOResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSSOResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSSOResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSSOResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AsyncSSOResourceWithStreamingResponse(self)

    async def invite(
        self,
        *,
        email: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSOInviteResponse:
        """Invite a user to the deployment via email.

        Creates a pre-registered user account
        with blocked status and no sub field. The central server will send the user an
        invitation email with a passcode.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/sso/invite",
            body=await async_maybe_transform({"email": email}, sso_invite_params.SSOInviteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSOInviteResponse,
        )

    async def login(
        self,
        *,
        token: str,
        email: str,
        passcode: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSOLoginResponse:
        """Handle SSO login with JWT token authentication.

        Creates a new user account if
        needed or validates existing user credentials.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/sso/login",
            body=await async_maybe_transform(
                {
                    "token": token,
                    "email": email,
                    "passcode": passcode,
                },
                sso_login_params.SSOLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSOLoginResponse,
        )

    async def rotate_passcode(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SSORotatePasscodeResponse:
        """
        Generate a new passcode for the current user.

        This endpoint gets a new passcode from the central server and re-wraps the
        user's private key with the new passcode. The user must be authenticated with a
        valid token to use this endpoint.
        """
        return await self._post(
            "/api/sso/rotate_passcode",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SSORotatePasscodeResponse,
        )


class SSOResourceWithRawResponse:
    def __init__(self, sso: SSOResource) -> None:
        self._sso = sso

        self.invite = to_raw_response_wrapper(
            sso.invite,
        )
        self.login = to_raw_response_wrapper(
            sso.login,
        )
        self.rotate_passcode = to_raw_response_wrapper(
            sso.rotate_passcode,
        )


class AsyncSSOResourceWithRawResponse:
    def __init__(self, sso: AsyncSSOResource) -> None:
        self._sso = sso

        self.invite = async_to_raw_response_wrapper(
            sso.invite,
        )
        self.login = async_to_raw_response_wrapper(
            sso.login,
        )
        self.rotate_passcode = async_to_raw_response_wrapper(
            sso.rotate_passcode,
        )


class SSOResourceWithStreamingResponse:
    def __init__(self, sso: SSOResource) -> None:
        self._sso = sso

        self.invite = to_streamed_response_wrapper(
            sso.invite,
        )
        self.login = to_streamed_response_wrapper(
            sso.login,
        )
        self.rotate_passcode = to_streamed_response_wrapper(
            sso.rotate_passcode,
        )


class AsyncSSOResourceWithStreamingResponse:
    def __init__(self, sso: AsyncSSOResource) -> None:
        self._sso = sso

        self.invite = async_to_streamed_response_wrapper(
            sso.invite,
        )
        self.login = async_to_streamed_response_wrapper(
            sso.login,
        )
        self.rotate_passcode = async_to_streamed_response_wrapper(
            sso.rotate_passcode,
        )
