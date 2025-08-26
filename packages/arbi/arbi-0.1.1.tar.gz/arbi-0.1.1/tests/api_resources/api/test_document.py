# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from arbi import Arbi, AsyncArbi
from arbi._utils import parse_date
from tests.utils import assert_matches_type
from arbi.types.api import (
    DocResponse,
    DocumentDeleteResponse,
    DocumentUpdateResponse,
    DocumentGetTagsResponse,
    DocumentGetParsedResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocument:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Arbi) -> None:
        document = client.api.document.update(
            document_ext_id="doc",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Arbi) -> None:
        document = client.api.document.update(
            document_ext_id="doc",
            doc_date=parse_date("2019-12-27"),
            shared=True,
            title="title",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.update(
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.update(
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.update(
                document_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Arbi) -> None:
        document = client.api.document.delete(
            "doc",
        )
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.delete(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.delete(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentDeleteResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_download(self, client: Arbi) -> None:
        document = client.api.document.download(
            "doc",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_download(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.download(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_download(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.download(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_download(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.download(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Arbi) -> None:
        document = client.api.document.get(
            "doc",
        )
        assert_matches_type(DocResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.get(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.get(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_parsed(self, client: Arbi) -> None:
        document = client.api.document.get_parsed(
            stage="marker",
            document_ext_id="doc",
        )
        assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_parsed(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.get_parsed(
            stage="marker",
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_parsed(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.get_parsed(
            stage="marker",
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_parsed(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.get_parsed(
                stage="marker",
                document_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_tags(self, client: Arbi) -> None:
        document = client.api.document.get_tags(
            "doc",
        )
        assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_tags(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.get_tags(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_tags(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.get_tags(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_tags(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            client.api.document.with_raw_response.get_tags(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload(self, client: Arbi) -> None:
        document = client.api.document.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_with_all_params(self, client: Arbi) -> None:
        document = client.api.document.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
            config_ext_id="config_ext_id",
            shared=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_view(self, client: Arbi) -> None:
        document = client.api.document.view(
            document_ext_id="doc",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_view_with_all_params(self, client: Arbi) -> None:
        document = client.api.document.view(
            document_ext_id="doc",
            page=0,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_view(self, client: Arbi) -> None:
        response = client.api.document.with_raw_response.view(
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_view(self, client: Arbi) -> None:
        with client.api.document.with_streaming_response.view(
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_view(self, client: Arbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            client.api.document.with_raw_response.view(
                document_ext_id="",
            )


class TestAsyncDocument:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.update(
            document_ext_id="doc",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.update(
            document_ext_id="doc",
            doc_date=parse_date("2019-12-27"),
            shared=True,
            title="title",
        )
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.update(
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentUpdateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.update(
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentUpdateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.update(
                document_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.delete(
            "doc",
        )
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.delete(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentDeleteResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.delete(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentDeleteResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_download(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.download(
            "doc",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_download(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.download(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_download(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.download(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_download(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.download(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.get(
            "doc",
        )
        assert_matches_type(DocResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.get(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.get(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.get(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_parsed(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.get_parsed(
            stage="marker",
            document_ext_id="doc",
        )
        assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_parsed(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.get_parsed(
            stage="marker",
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_parsed(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.get_parsed(
            stage="marker",
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetParsedResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_parsed(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.get_parsed(
                stage="marker",
                document_ext_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_tags(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.get_tags(
            "doc",
        )
        assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_tags(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.get_tags(
            "doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_tags(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.get_tags(
            "doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetTagsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_tags(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.get_tags(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
            config_ext_id="config_ext_id",
            shared=True,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.upload(
            workspace_ext_id="wrk",
            files=[b"raw file contents"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_view(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.view(
            document_ext_id="doc",
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_view_with_all_params(self, async_client: AsyncArbi) -> None:
        document = await async_client.api.document.view(
            document_ext_id="doc",
            page=0,
        )
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_view(self, async_client: AsyncArbi) -> None:
        response = await async_client.api.document.with_raw_response.view(
            document_ext_id="doc",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(object, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_view(self, async_client: AsyncArbi) -> None:
        async with async_client.api.document.with_streaming_response.view(
            document_ext_id="doc",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(object, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_view(self, async_client: AsyncArbi) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `document_ext_id` but received ''"):
            await async_client.api.document.with_raw_response.view(
                document_ext_id="",
            )
