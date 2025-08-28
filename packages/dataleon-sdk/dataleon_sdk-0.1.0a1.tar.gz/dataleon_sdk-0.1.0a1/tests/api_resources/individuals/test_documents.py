# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from dataleon import Dataleon, AsyncDataleon
from tests.utils import assert_matches_type
from dataleon.types.individuals import GenericDocument, DocumentResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocuments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Dataleon) -> None:
        document = client.individuals.documents.list(
            "individual_id",
        )
        assert_matches_type(DocumentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Dataleon) -> None:
        response = client.individuals.documents.with_raw_response.list(
            "individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Dataleon) -> None:
        with client.individuals.documents.with_streaming_response.list(
            "individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            client.individuals.documents.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload(self, client: Dataleon) -> None:
        document = client.individuals.documents.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        )
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upload_with_all_params(self, client: Dataleon) -> None:
        document = client.individuals.documents.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
            file=b"raw file contents",
            url="https://example.com/sample.pdf",
        )
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upload(self, client: Dataleon) -> None:
        response = client.individuals.documents.with_raw_response.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upload(self, client: Dataleon) -> None:
        with client.individuals.documents.with_streaming_response.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(GenericDocument, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upload(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            client.individuals.documents.with_raw_response.upload(
                individual_id="",
                document_type="liasse_fiscale",
            )


class TestAsyncDocuments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncDataleon) -> None:
        document = await async_client.individuals.documents.list(
            "individual_id",
        )
        assert_matches_type(DocumentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.documents.with_raw_response.list(
            "individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.documents.with_streaming_response.list(
            "individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            await async_client.individuals.documents.with_raw_response.list(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload(self, async_client: AsyncDataleon) -> None:
        document = await async_client.individuals.documents.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        )
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upload_with_all_params(self, async_client: AsyncDataleon) -> None:
        document = await async_client.individuals.documents.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
            file=b"raw file contents",
            url="https://example.com/sample.pdf",
        )
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upload(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.documents.with_raw_response.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(GenericDocument, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upload(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.documents.with_streaming_response.upload(
            individual_id="individual_id",
            document_type="liasse_fiscale",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(GenericDocument, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upload(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            await async_client.individuals.documents.with_raw_response.upload(
                individual_id="",
                document_type="liasse_fiscale",
            )
