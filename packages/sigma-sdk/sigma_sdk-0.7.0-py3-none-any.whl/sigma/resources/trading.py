# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import trading_submit_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..types.order import Order
from .._base_client import make_request_options
from ..types.trading_list_response import TradingListResponse

__all__ = ["TradingResource", "AsyncTradingResource"]


class TradingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TradingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return TradingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TradingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return TradingResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TradingListResponse:
        """Get historical orders"""
        return self._get(
            "/trading/orders",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TradingListResponse,
        )

    def submit(
        self,
        *,
        order_id: str | NotGiven = NOT_GIVEN,
        price: str | NotGiven = NOT_GIVEN,
        quantity: str | NotGiven = NOT_GIVEN,
        side: Literal["buy", "sell"] | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        type: Literal["market", "limit"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Submit a new order

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/trading/order",
            body=maybe_transform(
                {
                    "order_id": order_id,
                    "price": price,
                    "quantity": quantity,
                    "side": side,
                    "symbol": symbol,
                    "type": type,
                },
                trading_submit_params.TradingSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )


class AsyncTradingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTradingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTradingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTradingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncTradingResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TradingListResponse:
        """Get historical orders"""
        return await self._get(
            "/trading/orders",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TradingListResponse,
        )

    async def submit(
        self,
        *,
        order_id: str | NotGiven = NOT_GIVEN,
        price: str | NotGiven = NOT_GIVEN,
        quantity: str | NotGiven = NOT_GIVEN,
        side: Literal["buy", "sell"] | NotGiven = NOT_GIVEN,
        symbol: str | NotGiven = NOT_GIVEN,
        type: Literal["market", "limit"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Order:
        """
        Submit a new order

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/trading/order",
            body=await async_maybe_transform(
                {
                    "order_id": order_id,
                    "price": price,
                    "quantity": quantity,
                    "side": side,
                    "symbol": symbol,
                    "type": type,
                },
                trading_submit_params.TradingSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Order,
        )


class TradingResourceWithRawResponse:
    def __init__(self, trading: TradingResource) -> None:
        self._trading = trading

        self.list = to_raw_response_wrapper(
            trading.list,
        )
        self.submit = to_raw_response_wrapper(
            trading.submit,
        )


class AsyncTradingResourceWithRawResponse:
    def __init__(self, trading: AsyncTradingResource) -> None:
        self._trading = trading

        self.list = async_to_raw_response_wrapper(
            trading.list,
        )
        self.submit = async_to_raw_response_wrapper(
            trading.submit,
        )


class TradingResourceWithStreamingResponse:
    def __init__(self, trading: TradingResource) -> None:
        self._trading = trading

        self.list = to_streamed_response_wrapper(
            trading.list,
        )
        self.submit = to_streamed_response_wrapper(
            trading.submit,
        )


class AsyncTradingResourceWithStreamingResponse:
    def __init__(self, trading: AsyncTradingResource) -> None:
        self._trading = trading

        self.list = async_to_streamed_response_wrapper(
            trading.list,
        )
        self.submit = async_to_streamed_response_wrapper(
            trading.submit,
        )
