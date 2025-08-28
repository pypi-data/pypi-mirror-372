# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lucere import Lucere, AsyncLucere
from tests.utils import assert_matches_type
from lucere.types import TokenResponse, VerifyResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestToken:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_generate(self, client: Lucere) -> None:
        token = client.token.generate(
            role="role",
            user_id="user_id",
        )
        assert_matches_type(TokenResponse, token, path=["response"])

    @parametrize
    def test_raw_response_generate(self, client: Lucere) -> None:
        response = client.token.with_raw_response.generate(
            role="role",
            user_id="user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        token = response.parse()
        assert_matches_type(TokenResponse, token, path=["response"])

    @parametrize
    def test_streaming_response_generate(self, client: Lucere) -> None:
        with client.token.with_streaming_response.generate(
            role="role",
            user_id="user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            token = response.parse()
            assert_matches_type(TokenResponse, token, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_verify(self, client: Lucere) -> None:
        token = client.token.verify()
        assert_matches_type(VerifyResponse, token, path=["response"])

    @parametrize
    def test_raw_response_verify(self, client: Lucere) -> None:
        response = client.token.with_raw_response.verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        token = response.parse()
        assert_matches_type(VerifyResponse, token, path=["response"])

    @parametrize
    def test_streaming_response_verify(self, client: Lucere) -> None:
        with client.token.with_streaming_response.verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            token = response.parse()
            assert_matches_type(VerifyResponse, token, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncToken:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_generate(self, async_client: AsyncLucere) -> None:
        token = await async_client.token.generate(
            role="role",
            user_id="user_id",
        )
        assert_matches_type(TokenResponse, token, path=["response"])

    @parametrize
    async def test_raw_response_generate(self, async_client: AsyncLucere) -> None:
        response = await async_client.token.with_raw_response.generate(
            role="role",
            user_id="user_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        token = await response.parse()
        assert_matches_type(TokenResponse, token, path=["response"])

    @parametrize
    async def test_streaming_response_generate(self, async_client: AsyncLucere) -> None:
        async with async_client.token.with_streaming_response.generate(
            role="role",
            user_id="user_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            token = await response.parse()
            assert_matches_type(TokenResponse, token, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_verify(self, async_client: AsyncLucere) -> None:
        token = await async_client.token.verify()
        assert_matches_type(VerifyResponse, token, path=["response"])

    @parametrize
    async def test_raw_response_verify(self, async_client: AsyncLucere) -> None:
        response = await async_client.token.with_raw_response.verify()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        token = await response.parse()
        assert_matches_type(VerifyResponse, token, path=["response"])

    @parametrize
    async def test_streaming_response_verify(self, async_client: AsyncLucere) -> None:
        async with async_client.token.with_streaming_response.verify() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            token = await response.parse()
            assert_matches_type(VerifyResponse, token, path=["response"])

        assert cast(Any, response.is_closed) is True
