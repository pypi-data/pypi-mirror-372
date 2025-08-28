# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sigma import Petstore, AsyncPetstore
from tests.utils import assert_matches_type
from sigma.types.portfolio import Credit

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCredit:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Petstore) -> None:
        credit = client.portfolio.credit.retrieve()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Petstore) -> None:
        response = client.portfolio.credit.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credit = response.parse()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Petstore) -> None:
        with client.portfolio.credit.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credit = response.parse()
            assert_matches_type(Credit, credit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Petstore) -> None:
        credit = client.portfolio.credit.get()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Petstore) -> None:
        response = client.portfolio.credit.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credit = response.parse()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Petstore) -> None:
        with client.portfolio.credit.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credit = response.parse()
            assert_matches_type(Credit, credit, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCredit:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncPetstore) -> None:
        credit = await async_client.portfolio.credit.retrieve()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncPetstore) -> None:
        response = await async_client.portfolio.credit.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credit = await response.parse()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncPetstore) -> None:
        async with async_client.portfolio.credit.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credit = await response.parse()
            assert_matches_type(Credit, credit, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncPetstore) -> None:
        credit = await async_client.portfolio.credit.get()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncPetstore) -> None:
        response = await async_client.portfolio.credit.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credit = await response.parse()
        assert_matches_type(Credit, credit, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncPetstore) -> None:
        async with async_client.portfolio.credit.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credit = await response.parse()
            assert_matches_type(Credit, credit, path=["response"])

        assert cast(Any, response.is_closed) is True
