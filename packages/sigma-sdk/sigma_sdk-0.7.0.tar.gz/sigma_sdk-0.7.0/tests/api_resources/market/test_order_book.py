# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sigma import Petstore, AsyncPetstore
from tests.utils import assert_matches_type
from sigma.types.market import OrderBook

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrderBook:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Petstore) -> None:
        order_book = client.market.order_book.retrieve()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Petstore) -> None:
        response = client.market.order_book.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order_book = response.parse()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Petstore) -> None:
        with client.market.order_book.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order_book = response.parse()
            assert_matches_type(OrderBook, order_book, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Petstore) -> None:
        order_book = client.market.order_book.get()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Petstore) -> None:
        response = client.market.order_book.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order_book = response.parse()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Petstore) -> None:
        with client.market.order_book.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order_book = response.parse()
            assert_matches_type(OrderBook, order_book, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOrderBook:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncPetstore) -> None:
        order_book = await async_client.market.order_book.retrieve()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncPetstore) -> None:
        response = await async_client.market.order_book.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order_book = await response.parse()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncPetstore) -> None:
        async with async_client.market.order_book.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order_book = await response.parse()
            assert_matches_type(OrderBook, order_book, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncPetstore) -> None:
        order_book = await async_client.market.order_book.get()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncPetstore) -> None:
        response = await async_client.market.order_book.with_raw_response.get()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        order_book = await response.parse()
        assert_matches_type(OrderBook, order_book, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncPetstore) -> None:
        async with async_client.market.order_book.with_streaming_response.get() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            order_book = await response.parse()
            assert_matches_type(OrderBook, order_book, path=["response"])

        assert cast(Any, response.is_closed) is True
