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
from ...types.portfolio.open_position import OpenPosition

__all__ = ["OpenPositionResource", "AsyncOpenPositionResource"]


class OpenPositionResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OpenPositionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OpenPositionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OpenPositionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return OpenPositionResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpenPosition:
        """Get open positions"""
        return self._get(
            "/portfolio/openPosition",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenPosition,
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
    ) -> OpenPosition:
        """Get open positions"""
        return self._get(
            "/portfolio/openPosition",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenPosition,
        )


class AsyncOpenPositionResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOpenPositionResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOpenPositionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOpenPositionResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncOpenPositionResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OpenPosition:
        """Get open positions"""
        return await self._get(
            "/portfolio/openPosition",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenPosition,
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
    ) -> OpenPosition:
        """Get open positions"""
        return await self._get(
            "/portfolio/openPosition",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OpenPosition,
        )


class OpenPositionResourceWithRawResponse:
    def __init__(self, open_position: OpenPositionResource) -> None:
        self._open_position = open_position

        self.retrieve = to_raw_response_wrapper(
            open_position.retrieve,
        )
        self.get = to_raw_response_wrapper(
            open_position.get,
        )


class AsyncOpenPositionResourceWithRawResponse:
    def __init__(self, open_position: AsyncOpenPositionResource) -> None:
        self._open_position = open_position

        self.retrieve = async_to_raw_response_wrapper(
            open_position.retrieve,
        )
        self.get = async_to_raw_response_wrapper(
            open_position.get,
        )


class OpenPositionResourceWithStreamingResponse:
    def __init__(self, open_position: OpenPositionResource) -> None:
        self._open_position = open_position

        self.retrieve = to_streamed_response_wrapper(
            open_position.retrieve,
        )
        self.get = to_streamed_response_wrapper(
            open_position.get,
        )


class AsyncOpenPositionResourceWithStreamingResponse:
    def __init__(self, open_position: AsyncOpenPositionResource) -> None:
        self._open_position = open_position

        self.retrieve = async_to_streamed_response_wrapper(
            open_position.retrieve,
        )
        self.get = async_to_streamed_response_wrapper(
            open_position.get,
        )
