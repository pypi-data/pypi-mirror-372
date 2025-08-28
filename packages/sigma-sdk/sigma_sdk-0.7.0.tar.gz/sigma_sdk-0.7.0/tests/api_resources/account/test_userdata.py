# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from sigma import Petstore, AsyncPetstore
from tests.utils import assert_matches_type
from sigma.types.account import UserData

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUserdata:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: Petstore) -> None:
        userdata = client.account.userdata.retrieve()
        assert_matches_type(UserData, userdata, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: Petstore) -> None:
        response = client.account.userdata.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        userdata = response.parse()
        assert_matches_type(UserData, userdata, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: Petstore) -> None:
        with client.account.userdata.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            userdata = response.parse()
            assert_matches_type(UserData, userdata, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUserdata:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncPetstore) -> None:
        userdata = await async_client.account.userdata.retrieve()
        assert_matches_type(UserData, userdata, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncPetstore) -> None:
        response = await async_client.account.userdata.with_raw_response.retrieve()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        userdata = await response.parse()
        assert_matches_type(UserData, userdata, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncPetstore) -> None:
        async with async_client.account.userdata.with_streaming_response.retrieve() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            userdata = await response.parse()
            assert_matches_type(UserData, userdata, path=["response"])

        assert cast(Any, response.is_closed) is True
