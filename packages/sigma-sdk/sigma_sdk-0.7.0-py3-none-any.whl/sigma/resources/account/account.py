# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .userdata import (
    UserdataResource,
    AsyncUserdataResource,
    UserdataResourceWithRawResponse,
    AsyncUserdataResourceWithRawResponse,
    UserdataResourceWithStreamingResponse,
    AsyncUserdataResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["AccountResource", "AsyncAccountResource"]


class AccountResource(SyncAPIResource):
    @cached_property
    def userdata(self) -> UserdataResource:
        return UserdataResource(self._client)

    @cached_property
    def with_raw_response(self) -> AccountResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AccountResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AccountResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AccountResourceWithStreamingResponse(self)


class AsyncAccountResource(AsyncAPIResource):
    @cached_property
    def userdata(self) -> AsyncUserdataResource:
        return AsyncUserdataResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAccountResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAccountResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAccountResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/SigmaEf5ect/sigma-sdk-python#with_streaming_response
        """
        return AsyncAccountResourceWithStreamingResponse(self)


class AccountResourceWithRawResponse:
    def __init__(self, account: AccountResource) -> None:
        self._account = account

    @cached_property
    def userdata(self) -> UserdataResourceWithRawResponse:
        return UserdataResourceWithRawResponse(self._account.userdata)


class AsyncAccountResourceWithRawResponse:
    def __init__(self, account: AsyncAccountResource) -> None:
        self._account = account

    @cached_property
    def userdata(self) -> AsyncUserdataResourceWithRawResponse:
        return AsyncUserdataResourceWithRawResponse(self._account.userdata)


class AccountResourceWithStreamingResponse:
    def __init__(self, account: AccountResource) -> None:
        self._account = account

    @cached_property
    def userdata(self) -> UserdataResourceWithStreamingResponse:
        return UserdataResourceWithStreamingResponse(self._account.userdata)


class AsyncAccountResourceWithStreamingResponse:
    def __init__(self, account: AsyncAccountResource) -> None:
        self._account = account

    @cached_property
    def userdata(self) -> AsyncUserdataResourceWithStreamingResponse:
        return AsyncUserdataResourceWithStreamingResponse(self._account.userdata)
