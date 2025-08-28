# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .credit import (
    CreditResource,
    AsyncCreditResource,
    CreditResourceWithRawResponse,
    AsyncCreditResourceWithRawResponse,
    CreditResourceWithStreamingResponse,
    AsyncCreditResourceWithStreamingResponse,
)
from .balance import (
    BalanceResource,
    AsyncBalanceResource,
    BalanceResourceWithRawResponse,
    AsyncBalanceResourceWithRawResponse,
    BalanceResourceWithStreamingResponse,
    AsyncBalanceResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .open_position import (
    OpenPositionResource,
    AsyncOpenPositionResource,
    OpenPositionResourceWithRawResponse,
    AsyncOpenPositionResourceWithRawResponse,
    OpenPositionResourceWithStreamingResponse,
    AsyncOpenPositionResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.portfolio.portfolio import Portfolio

__all__ = ["PortfolioResource", "AsyncPortfolioResource"]


class PortfolioResource(SyncAPIResource):
    @cached_property
    def balance(self) -> BalanceResource:
        return BalanceResource(self._client)

    @cached_property
    def open_position(self) -> OpenPositionResource:
        return OpenPositionResource(self._client)

    @cached_property
    def credit(self) -> CreditResource:
        return CreditResource(self._client)

    @cached_property
    def with_raw_response(self) -> PortfolioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PortfolioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PortfolioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return PortfolioResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Portfolio:
        """Get portfolio data"""
        return self._get(
            "/portfolio",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Portfolio,
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
    ) -> Portfolio:
        """Get portfolio data"""
        return self._get(
            "/portfolio",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Portfolio,
        )


class AsyncPortfolioResource(AsyncAPIResource):
    @cached_property
    def balance(self) -> AsyncBalanceResource:
        return AsyncBalanceResource(self._client)

    @cached_property
    def open_position(self) -> AsyncOpenPositionResource:
        return AsyncOpenPositionResource(self._client)

    @cached_property
    def credit(self) -> AsyncCreditResource:
        return AsyncCreditResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPortfolioResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPortfolioResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPortfolioResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncPortfolioResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Portfolio:
        """Get portfolio data"""
        return await self._get(
            "/portfolio",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Portfolio,
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
    ) -> Portfolio:
        """Get portfolio data"""
        return await self._get(
            "/portfolio",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Portfolio,
        )


class PortfolioResourceWithRawResponse:
    def __init__(self, portfolio: PortfolioResource) -> None:
        self._portfolio = portfolio

        self.retrieve = to_raw_response_wrapper(
            portfolio.retrieve,
        )
        self.get = to_raw_response_wrapper(
            portfolio.get,
        )

    @cached_property
    def balance(self) -> BalanceResourceWithRawResponse:
        return BalanceResourceWithRawResponse(self._portfolio.balance)

    @cached_property
    def open_position(self) -> OpenPositionResourceWithRawResponse:
        return OpenPositionResourceWithRawResponse(self._portfolio.open_position)

    @cached_property
    def credit(self) -> CreditResourceWithRawResponse:
        return CreditResourceWithRawResponse(self._portfolio.credit)


class AsyncPortfolioResourceWithRawResponse:
    def __init__(self, portfolio: AsyncPortfolioResource) -> None:
        self._portfolio = portfolio

        self.retrieve = async_to_raw_response_wrapper(
            portfolio.retrieve,
        )
        self.get = async_to_raw_response_wrapper(
            portfolio.get,
        )

    @cached_property
    def balance(self) -> AsyncBalanceResourceWithRawResponse:
        return AsyncBalanceResourceWithRawResponse(self._portfolio.balance)

    @cached_property
    def open_position(self) -> AsyncOpenPositionResourceWithRawResponse:
        return AsyncOpenPositionResourceWithRawResponse(self._portfolio.open_position)

    @cached_property
    def credit(self) -> AsyncCreditResourceWithRawResponse:
        return AsyncCreditResourceWithRawResponse(self._portfolio.credit)


class PortfolioResourceWithStreamingResponse:
    def __init__(self, portfolio: PortfolioResource) -> None:
        self._portfolio = portfolio

        self.retrieve = to_streamed_response_wrapper(
            portfolio.retrieve,
        )
        self.get = to_streamed_response_wrapper(
            portfolio.get,
        )

    @cached_property
    def balance(self) -> BalanceResourceWithStreamingResponse:
        return BalanceResourceWithStreamingResponse(self._portfolio.balance)

    @cached_property
    def open_position(self) -> OpenPositionResourceWithStreamingResponse:
        return OpenPositionResourceWithStreamingResponse(self._portfolio.open_position)

    @cached_property
    def credit(self) -> CreditResourceWithStreamingResponse:
        return CreditResourceWithStreamingResponse(self._portfolio.credit)


class AsyncPortfolioResourceWithStreamingResponse:
    def __init__(self, portfolio: AsyncPortfolioResource) -> None:
        self._portfolio = portfolio

        self.retrieve = async_to_streamed_response_wrapper(
            portfolio.retrieve,
        )
        self.get = async_to_streamed_response_wrapper(
            portfolio.get,
        )

    @cached_property
    def balance(self) -> AsyncBalanceResourceWithStreamingResponse:
        return AsyncBalanceResourceWithStreamingResponse(self._portfolio.balance)

    @cached_property
    def open_position(self) -> AsyncOpenPositionResourceWithStreamingResponse:
        return AsyncOpenPositionResourceWithStreamingResponse(self._portfolio.open_position)

    @cached_property
    def credit(self) -> AsyncCreditResourceWithStreamingResponse:
        return AsyncCreditResourceWithStreamingResponse(self._portfolio.credit)
