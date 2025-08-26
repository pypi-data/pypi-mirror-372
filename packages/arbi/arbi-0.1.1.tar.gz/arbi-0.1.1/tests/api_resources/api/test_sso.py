# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from arbi import Arbi, AsyncArbi
from tests.utils import assert_matches_type
from arbi.types.api import (
    SSOLoginResponse,
    SSOInviteResponse,
    SSORotatePasscodeResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSSO:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_invite(self, client: Arbi) -> None:
        sso = client.api.sso.invite(
            email="dev@stainless.com",
        )
        assert_matches_type(SSOInviteResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_invite(self, client: Arbi) -> None:
        response = client.api.sso.with_raw_response.invite(
            email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = response.parse()
        assert_matches_type(SSOInviteResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_invite(self, client: Arbi) -> None:
        with client.api.sso.with_streaming_response.invite(
            email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = response.parse()
            assert_matches_type(SSOInviteResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login(self, client: Arbi) -> None:
        sso = client.api.sso.login(
            token="token",
            email="email",
        )
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login_with_all_params(self, client: Arbi) -> None:
        sso = client.api.sso.login(
            token="token",
            email="email",
            passcode="passcode",
        )
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_login(self, client: Arbi) -> None:
        response = client.api.sso.with_raw_response.login(
            token="token",
            email="email",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = response.parse()
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_login(self, client: Arbi) -> None:
        with client.api.sso.with_streaming_response.login(
            token="token",
            email="email",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = response.parse()
            assert_matches_type(SSOLoginResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_rotate_passcode(self, client: Arbi) -> None:
        sso = client.api.sso.rotate_passcode()
        assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_rotate_passcode(self, client: Arbi) -> None:
        response = client.api.sso.with_raw_response.rotate_passcode()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = response.parse()
        assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_rotate_passcode(self, client: Arbi) -> None:
        with client.api.sso.with_streaming_response.rotate_passcode() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = response.parse()
            assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSSO:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_invite(self, async_client: AsyncArbi) -> None:
        sso = await async_client.api.sso.invite(
            email="dev@stainless.com",
        )
        assert_matches_type(SSOInviteResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_invite(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.sso.with_raw_response.invite(
            email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = await response.parse()
        assert_matches_type(SSOInviteResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_invite(self, async_client: AsyncArbi) -> None:
        async with async_client.api.sso.with_streaming_response.invite(
            email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = await response.parse()
            assert_matches_type(SSOInviteResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login(self, async_client: AsyncArbi) -> None:
        sso = await async_client.api.sso.login(
            token="token",
            email="email",
        )
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login_with_all_params(self, async_client: AsyncArbi) -> None:
        sso = await async_client.api.sso.login(
            token="token",
            email="email",
            passcode="passcode",
        )
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_login(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.sso.with_raw_response.login(
            token="token",
            email="email",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = await response.parse()
        assert_matches_type(SSOLoginResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_login(self, async_client: AsyncArbi) -> None:
        async with async_client.api.sso.with_streaming_response.login(
            token="token",
            email="email",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = await response.parse()
            assert_matches_type(SSOLoginResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_rotate_passcode(self, async_client: AsyncArbi) -> None:
        sso = await async_client.api.sso.rotate_passcode()
        assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_rotate_passcode(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.sso.with_raw_response.rotate_passcode()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sso = await response.parse()
        assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_rotate_passcode(self, async_client: AsyncArbi) -> None:
        async with async_client.api.sso.with_streaming_response.rotate_passcode() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sso = await response.parse()
            assert_matches_type(SSORotatePasscodeResponse, sso, path=["response"])

        assert cast(Any, response.is_closed) is True
