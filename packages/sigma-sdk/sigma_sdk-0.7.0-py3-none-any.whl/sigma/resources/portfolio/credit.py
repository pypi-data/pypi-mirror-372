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
from ...types.portfolio.credit import Credit

__all__ = ["CreditResource", "AsyncCreditResource"]


class CreditResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CreditResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return CreditResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CreditResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return CreditResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Credit:
        """Get credit data"""
        return self._get(
            "/portfolio/credit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Credit,
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
    ) -> Credit:
        """Get credit data"""
        return self._get(
            "/portfolio/credit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Credit,
        )


class AsyncCreditResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCreditResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCreditResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCreditResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncCreditResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Credit:
        """Get credit data"""
        return await self._get(
            "/portfolio/credit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Credit,
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
    ) -> Credit:
        """Get credit data"""
        return await self._get(
            "/portfolio/credit",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Credit,
        )


class CreditResourceWithRawResponse:
    def __init__(self, credit: CreditResource) -> None:
        self._credit = credit

        self.retrieve = to_raw_response_wrapper(
            credit.retrieve,
        )
        self.get = to_raw_response_wrapper(
            credit.get,
        )


class AsyncCreditResourceWithRawResponse:
    def __init__(self, credit: AsyncCreditResource) -> None:
        self._credit = credit

        self.retrieve = async_to_raw_response_wrapper(
            credit.retrieve,
        )
        self.get = async_to_raw_response_wrapper(
            credit.get,
        )


class CreditResourceWithStreamingResponse:
    def __init__(self, credit: CreditResource) -> None:
        self._credit = credit

        self.retrieve = to_streamed_response_wrapper(
            credit.retrieve,
        )
        self.get = to_streamed_response_wrapper(
            credit.get,
        )


class AsyncCreditResourceWithStreamingResponse:
    def __init__(self, credit: AsyncCreditResource) -> None:
        self._credit = credit

        self.retrieve = async_to_streamed_response_wrapper(
            credit.retrieve,
        )
        self.get = async_to_streamed_response_wrapper(
            credit.get,
        )
