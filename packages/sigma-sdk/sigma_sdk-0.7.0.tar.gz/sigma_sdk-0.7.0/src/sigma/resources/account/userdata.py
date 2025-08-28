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
from ...types.account.user_data import UserData

__all__ = ["UserdataResource", "AsyncUserdataResource"]


class UserdataResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserdataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return UserdataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserdataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return UserdataResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserData:
        """Get user data"""
        return self._get(
            "/account/userdata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserData,
        )


class AsyncUserdataResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserdataResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUserdataResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserdataResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncUserdataResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> UserData:
        """Get user data"""
        return await self._get(
            "/account/userdata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserData,
        )


class UserdataResourceWithRawResponse:
    def __init__(self, userdata: UserdataResource) -> None:
        self._userdata = userdata

        self.retrieve = to_raw_response_wrapper(
            userdata.retrieve,
        )


class AsyncUserdataResourceWithRawResponse:
    def __init__(self, userdata: AsyncUserdataResource) -> None:
        self._userdata = userdata

        self.retrieve = async_to_raw_response_wrapper(
            userdata.retrieve,
        )


class UserdataResourceWithStreamingResponse:
    def __init__(self, userdata: UserdataResource) -> None:
        self._userdata = userdata

        self.retrieve = to_streamed_response_wrapper(
            userdata.retrieve,
        )


class AsyncUserdataResourceWithStreamingResponse:
    def __init__(self, userdata: AsyncUserdataResource) -> None:
        self._userdata = userdata

        self.retrieve = async_to_streamed_response_wrapper(
            userdata.retrieve,
        )
