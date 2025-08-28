# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sigma import Petstore, AsyncPetstore
from sigma.types import Order, TradingListResponse
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTrading:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Petstore) -> None:
        trading = client.trading.list()
        assert_matches_type(TradingListResponse, trading, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Petstore) -> None:
        response = client.trading.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trading = response.parse()
        assert_matches_type(TradingListResponse, trading, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Petstore) -> None:
        with client.trading.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trading = response.parse()
            assert_matches_type(TradingListResponse, trading, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_submit(self, client: Petstore) -> None:
        trading = client.trading.submit()
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    def test_method_submit_with_all_params(self, client: Petstore) -> None:
        trading = client.trading.submit(
            order_id="orderId",
            price="price",
            quantity="quantity",
            side="buy",
            symbol="symbol",
            type="market",
        )
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    def test_raw_response_submit(self, client: Petstore) -> None:
        response = client.trading.with_raw_response.submit()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trading = response.parse()
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    def test_streaming_response_submit(self, client: Petstore) -> None:
        with client.trading.with_streaming_response.submit() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trading = response.parse()
            assert_matches_type(Order, trading, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTrading:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncPetstore) -> None:
        trading = await async_client.trading.list()
        assert_matches_type(TradingListResponse, trading, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncPetstore) -> None:
        response = await async_client.trading.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trading = await response.parse()
        assert_matches_type(TradingListResponse, trading, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncPetstore) -> None:
        async with async_client.trading.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trading = await response.parse()
            assert_matches_type(TradingListResponse, trading, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_submit(self, async_client: AsyncPetstore) -> None:
        trading = await async_client.trading.submit()
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncPetstore) -> None:
        trading = await async_client.trading.submit(
            order_id="orderId",
            price="price",
            quantity="quantity",
            side="buy",
            symbol="symbol",
            type="market",
        )
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncPetstore) -> None:
        response = await async_client.trading.with_raw_response.submit()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        trading = await response.parse()
        assert_matches_type(Order, trading, path=["response"])

    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncPetstore) -> None:
        async with async_client.trading.with_streaming_response.submit() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            trading = await response.parse()
            assert_matches_type(Order, trading, path=["response"])

        assert cast(Any, response.is_closed) is True
