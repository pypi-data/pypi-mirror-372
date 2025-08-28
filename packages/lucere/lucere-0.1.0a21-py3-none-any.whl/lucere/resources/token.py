# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import token_generate_params
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
from .._base_client import make_request_options
from ..types.token_response import TokenResponse
from ..types.verify_response import VerifyResponse

__all__ = ["TokenResource", "AsyncTokenResource"]


class TokenResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TokenResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/jc-nana/lucere-python#accessing-raw-response-data-eg-headers
        """
        return TokenResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TokenResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/jc-nana/lucere-python#with_streaming_response
        """
        return TokenResourceWithStreamingResponse(self)

    def generate(
        self,
        *,
        role: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TokenResponse:
        """
        Handle Generate Token

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/generate-token",
            body=maybe_transform(
                {
                    "role": role,
                    "user_id": user_id,
                },
                token_generate_params.TokenGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TokenResponse,
        )

    def verify(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VerifyResponse:
        """Handle Verify Token"""
        return self._get(
            "/verify-token",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VerifyResponse,
        )


class AsyncTokenResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTokenResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/jc-nana/lucere-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTokenResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTokenResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/jc-nana/lucere-python#with_streaming_response
        """
        return AsyncTokenResourceWithStreamingResponse(self)

    async def generate(
        self,
        *,
        role: str,
        user_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TokenResponse:
        """
        Handle Generate Token

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/generate-token",
            body=await async_maybe_transform(
                {
                    "role": role,
                    "user_id": user_id,
                },
                token_generate_params.TokenGenerateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TokenResponse,
        )

    async def verify(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> VerifyResponse:
        """Handle Verify Token"""
        return await self._get(
            "/verify-token",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=VerifyResponse,
        )


class TokenResourceWithRawResponse:
    def __init__(self, token: TokenResource) -> None:
        self._token = token

        self.generate = to_raw_response_wrapper(
            token.generate,
        )
        self.verify = to_raw_response_wrapper(
            token.verify,
        )


class AsyncTokenResourceWithRawResponse:
    def __init__(self, token: AsyncTokenResource) -> None:
        self._token = token

        self.generate = async_to_raw_response_wrapper(
            token.generate,
        )
        self.verify = async_to_raw_response_wrapper(
            token.verify,
        )


class TokenResourceWithStreamingResponse:
    def __init__(self, token: TokenResource) -> None:
        self._token = token

        self.generate = to_streamed_response_wrapper(
            token.generate,
        )
        self.verify = to_streamed_response_wrapper(
            token.verify,
        )


class AsyncTokenResourceWithStreamingResponse:
    def __init__(self, token: AsyncTokenResource) -> None:
        self._token = token

        self.generate = async_to_streamed_response_wrapper(
            token.generate,
        )
        self.verify = async_to_streamed_response_wrapper(
            token.verify,
        )
