# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from dataleon import Dataleon, AsyncDataleon
from tests.utils import assert_matches_type
from dataleon.types import (
    Individual,
    IndividualListResponse,
)
from dataleon._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestIndividuals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Dataleon) -> None:
        individual = client.individuals.create(
            workspace_id="wk_123",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Dataleon) -> None:
        individual = client.individuals.create(
            workspace_id="wk_123",
            person={
                "birthday": "15/05/1985",
                "email": "john.doe@example.com",
                "first_name": "John",
                "gender": "M",
                "last_name": "Doe",
                "maiden_name": "John Doe",
                "phone_number": "+33 1 23 45 67 89",
            },
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Dataleon) -> None:
        response = client.individuals.with_raw_response.create(
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Dataleon) -> None:
        with client.individuals.with_streaming_response.create(
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Dataleon) -> None:
        individual = client.individuals.retrieve(
            individual_id="individual_id",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: Dataleon) -> None:
        individual = client.individuals.retrieve(
            individual_id="individual_id",
            document=True,
            scope="scope",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Dataleon) -> None:
        response = client.individuals.with_raw_response.retrieve(
            individual_id="individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Dataleon) -> None:
        with client.individuals.with_streaming_response.retrieve(
            individual_id="individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            client.individuals.with_raw_response.retrieve(
                individual_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Dataleon) -> None:
        individual = client.individuals.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Dataleon) -> None:
        individual = client.individuals.update(
            individual_id="individual_id",
            workspace_id="wk_123",
            person={
                "birthday": "15/05/1985",
                "email": "john.doe@example.com",
                "first_name": "John",
                "gender": "M",
                "last_name": "Doe",
                "maiden_name": "John Doe",
                "phone_number": "+33 1 23 45 67 89",
            },
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Dataleon) -> None:
        response = client.individuals.with_raw_response.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Dataleon) -> None:
        with client.individuals.with_streaming_response.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            client.individuals.with_raw_response.update(
                individual_id="",
                workspace_id="wk_123",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Dataleon) -> None:
        individual = client.individuals.list()
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Dataleon) -> None:
        individual = client.individuals.list(
            end_date=parse_date("2019-12-27"),
            limit=1,
            offset=0,
            source_id="source_id",
            start_date=parse_date("2019-12-27"),
            state="VOID",
            status="rejected",
            workspace_id="workspace_id",
        )
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Dataleon) -> None:
        response = client.individuals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = response.parse()
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Dataleon) -> None:
        with client.individuals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = response.parse()
            assert_matches_type(IndividualListResponse, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Dataleon) -> None:
        individual = client.individuals.delete(
            "individual_id",
        )
        assert individual is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Dataleon) -> None:
        response = client.individuals.with_raw_response.delete(
            "individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = response.parse()
        assert individual is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Dataleon) -> None:
        with client.individuals.with_streaming_response.delete(
            "individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = response.parse()
            assert individual is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Dataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            client.individuals.with_raw_response.delete(
                "",
            )


class TestAsyncIndividuals:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.create(
            workspace_id="wk_123",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.create(
            workspace_id="wk_123",
            person={
                "birthday": "15/05/1985",
                "email": "john.doe@example.com",
                "first_name": "John",
                "gender": "M",
                "last_name": "Doe",
                "maiden_name": "John Doe",
                "phone_number": "+33 1 23 45 67 89",
            },
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.with_raw_response.create(
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = await response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.with_streaming_response.create(
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = await response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.retrieve(
            individual_id="individual_id",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.retrieve(
            individual_id="individual_id",
            document=True,
            scope="scope",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.with_raw_response.retrieve(
            individual_id="individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = await response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.with_streaming_response.retrieve(
            individual_id="individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = await response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            await async_client.individuals.with_raw_response.retrieve(
                individual_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.update(
            individual_id="individual_id",
            workspace_id="wk_123",
            person={
                "birthday": "15/05/1985",
                "email": "john.doe@example.com",
                "first_name": "John",
                "gender": "M",
                "last_name": "Doe",
                "maiden_name": "John Doe",
                "phone_number": "+33 1 23 45 67 89",
            },
            source_id="ID54410069066",
            technical_data={
                "active_aml_suspicions": False,
                "callback_url": "https://example.com/callback",
                "callback_url_notification": "https://example.com/notify",
                "language": "fra",
                "raw_data": True,
            },
        )
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.with_raw_response.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = await response.parse()
        assert_matches_type(Individual, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.with_streaming_response.update(
            individual_id="individual_id",
            workspace_id="wk_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = await response.parse()
            assert_matches_type(Individual, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            await async_client.individuals.with_raw_response.update(
                individual_id="",
                workspace_id="wk_123",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.list()
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.list(
            end_date=parse_date("2019-12-27"),
            limit=1,
            offset=0,
            source_id="source_id",
            start_date=parse_date("2019-12-27"),
            state="VOID",
            status="rejected",
            workspace_id="workspace_id",
        )
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = await response.parse()
        assert_matches_type(IndividualListResponse, individual, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = await response.parse()
            assert_matches_type(IndividualListResponse, individual, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncDataleon) -> None:
        individual = await async_client.individuals.delete(
            "individual_id",
        )
        assert individual is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncDataleon) -> None:
        response = await async_client.individuals.with_raw_response.delete(
            "individual_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        individual = await response.parse()
        assert individual is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncDataleon) -> None:
        async with async_client.individuals.with_streaming_response.delete(
            "individual_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            individual = await response.parse()
            assert individual is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncDataleon) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `individual_id` but received ''"):
            await async_client.individuals.with_raw_response.delete(
                "",
            )
