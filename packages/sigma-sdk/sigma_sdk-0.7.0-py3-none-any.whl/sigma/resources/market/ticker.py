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
from ...types.market.ticker import Ticker

__all__ = ["TickerResource", "AsyncTickerResource"]


class TickerResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TickerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TickerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TickerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return TickerResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Ticker:
        """Get real-time ticker"""
        return self._get(
            "/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Ticker,
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
    ) -> Ticker:
        """Get real-time ticker"""
        return self._get(
            "/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Ticker,
        )


class AsyncTickerResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTickerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTickerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTickerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncTickerResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Ticker:
        """Get real-time ticker"""
        return await self._get(
            "/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Ticker,
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
    ) -> Ticker:
        """Get real-time ticker"""
        return await self._get(
            "/market/ticker",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Ticker,
        )


class TickerResourceWithRawResponse:
    def __init__(self, ticker: TickerResource) -> None:
        self._ticker = ticker

        self.retrieve = to_raw_response_wrapper(
            ticker.retrieve,
        )
        self.get = to_raw_response_wrapper(
            ticker.get,
        )


class AsyncTickerResourceWithRawResponse:
    def __init__(self, ticker: AsyncTickerResource) -> None:
        self._ticker = ticker

        self.retrieve = async_to_raw_response_wrapper(
            ticker.retrieve,
        )
        self.get = async_to_raw_response_wrapper(
            ticker.get,
        )


class TickerResourceWithStreamingResponse:
    def __init__(self, ticker: TickerResource) -> None:
        self._ticker = ticker

        self.retrieve = to_streamed_response_wrapper(
            ticker.retrieve,
        )
        self.get = to_streamed_response_wrapper(
            ticker.get,
        )


class AsyncTickerResourceWithStreamingResponse:
    def __init__(self, ticker: AsyncTickerResource) -> None:
        self._ticker = ticker

        self.retrieve = async_to_streamed_response_wrapper(
            ticker.retrieve,
        )
        self.get = async_to_streamed_response_wrapper(
            ticker.get,
        )
