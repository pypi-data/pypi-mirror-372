# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.market.order_book import OrderBook

__all__ = ["OrderBookResource", "AsyncOrderBookResource"]


class OrderBookResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrderBookResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OrderBookResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrderBookResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return OrderBookResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderBook:
        """Get real-time order book"""
        return self._get(
            "/market/orderBook",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderBook,
        )

    def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderBook:
        """Get real-time order book"""
        return self._get(
            "/market/orderBook",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderBook,
        )


class AsyncOrderBookResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrderBookResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrderBookResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrderBookResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncOrderBookResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderBook:
        """Get real-time order book"""
        return await self._get(
            "/market/orderBook",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderBook,
        )

    async def get(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OrderBook:
        """Get real-time order book"""
        return await self._get(
            "/market/orderBook",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OrderBook,
        )


class OrderBookResourceWithRawResponse:
    def __init__(self, order_book: OrderBookResource) -> None:
        self._order_book = order_book

        self.retrieve = to_raw_response_wrapper(
            order_book.retrieve,
        )
        self.get = to_raw_response_wrapper(
            order_book.get,
        )


class AsyncOrderBookResourceWithRawResponse:
    def __init__(self, order_book: AsyncOrderBookResource) -> None:
        self._order_book = order_book

        self.retrieve = async_to_raw_response_wrapper(
            order_book.retrieve,
        )
        self.get = async_to_raw_response_wrapper(
            order_book.get,
        )


class OrderBookResourceWithStreamingResponse:
    def __init__(self, order_book: OrderBookResource) -> None:
        self._order_book = order_book

        self.retrieve = to_streamed_response_wrapper(
            order_book.retrieve,
        )
        self.get = to_streamed_response_wrapper(
            order_book.get,
        )


class AsyncOrderBookResourceWithStreamingResponse:
    def __init__(self, order_book: AsyncOrderBookResource) -> None:
        self._order_book = order_book

        self.retrieve = async_to_streamed_response_wrapper(
            order_book.retrieve,
        )
        self.get = async_to_streamed_response_wrapper(
            order_book.get,
        )
