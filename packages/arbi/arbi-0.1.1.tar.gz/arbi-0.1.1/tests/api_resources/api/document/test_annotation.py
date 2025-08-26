# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from arbi import Arbi, AsyncArbi
from tests.utils import assert_matches_type
from arbi.types.api.document import (
    DocTagResponse,
    AnnotationDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAnnotation:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Arbi) -> None:
        annotation = client.api.document.annotation.create(
            doc_ext_id="doc",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Arbi) -> None:
        annotation = client.api.document.annotation.create(
            doc_ext_id="doc",
            note="note",
            page_ref=0,
            tag_name="tag_name",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Arbi) -> None:
        response = client.api.document.annotation.with_raw_response.create(
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = response.parse()
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Arbi) -> None:
        with client.api.document.annotation.with_streaming_response.create(
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = response.parse()
            assert_matches_type(DocTagResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            client.api.document.annotation.with_raw_response.create(
                doc_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Arbi) -> None:
        annotation = client.api.document.annotation.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Arbi) -> None:
        annotation = client.api.document.annotation.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
            note="note",
            page_ref=0,
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Arbi) -> None:
        response = client.api.document.annotation.with_raw_response.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = response.parse()
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Arbi) -> None:
        with client.api.document.annotation.with_streaming_response.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = response.parse()
            assert_matches_type(DocTagResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            client.api.document.annotation.with_raw_response.update(
                doctag_ext_id="dtj",
                doc_ext_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doctag_ext_id` but received ''"):
            client.api.document.annotation.with_raw_response.update(
                doctag_ext_id="",
                doc_ext_id="doc",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Arbi) -> None:
        annotation = client.api.document.annotation.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )
        assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Arbi) -> None:
        response = client.api.document.annotation.with_raw_response.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = response.parse()
        assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Arbi) -> None:
        with client.api.document.annotation.with_streaming_response.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = response.parse()
            assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            client.api.document.annotation.with_raw_response.delete(
                doctag_ext_id="dtj",
                doc_ext_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doctag_ext_id` but received ''"):
            client.api.document.annotation.with_raw_response.delete(
                doctag_ext_id="",
                doc_ext_id="doc",
            )


class TestAsyncAnnotation:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncArbi) -> None:
        annotation = await async_client.api.document.annotation.create(
            doc_ext_id="doc",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncArbi) -> None:
        annotation = await async_client.api.document.annotation.create(
            doc_ext_id="doc",
            note="note",
            page_ref=0,
            tag_name="tag_name",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.annotation.with_raw_response.create(
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = await response.parse()
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.annotation.with_streaming_response.create(
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = await response.parse()
            assert_matches_type(DocTagResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            await async_client.api.document.annotation.with_raw_response.create(
                doc_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncArbi) -> None:
        annotation = await async_client.api.document.annotation.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncArbi) -> None:
        annotation = await async_client.api.document.annotation.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
            note="note",
            page_ref=0,
        )
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.annotation.with_raw_response.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = await response.parse()
        assert_matches_type(DocTagResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.annotation.with_streaming_response.update(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = await response.parse()
            assert_matches_type(DocTagResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            await async_client.api.document.annotation.with_raw_response.update(
                doctag_ext_id="dtj",
                doc_ext_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doctag_ext_id` but received ''"):
            await async_client.api.document.annotation.with_raw_response.update(
                doctag_ext_id="",
                doc_ext_id="doc",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncArbi) -> None:
        annotation = await async_client.api.document.annotation.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )
        assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.annotation.with_raw_response.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        annotation = await response.parse()
        assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.annotation.with_streaming_response.delete(
            doctag_ext_id="dtj",
            doc_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            annotation = await response.parse()
            assert_matches_type(AnnotationDeleteResponse, annotation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            await async_client.api.document.annotation.with_raw_response.delete(
                doctag_ext_id="dtj",
                doc_ext_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doctag_ext_id` but received ''"):
            await async_client.api.document.annotation.with_raw_response.delete(
                doctag_ext_id="",
                doc_ext_id="doc",
            )
