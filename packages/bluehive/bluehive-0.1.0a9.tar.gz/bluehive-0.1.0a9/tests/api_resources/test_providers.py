# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bluehive import BlueHive, AsyncBlueHive
from tests.utils import assert_matches_type
from bluehive.types import ProviderLookupResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProviders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_lookup(self, client: BlueHive) -> None:
        provider = client.providers.lookup()
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_lookup_with_all_params(self, client: BlueHive) -> None:
        provider = client.providers.lookup(
            firstname="firstname",
            lastname="lastname",
            npi="npi",
            zipcode="zipcode",
        )
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_lookup(self, client: BlueHive) -> None:
        response = client.providers.with_raw_response.lookup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = response.parse()
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_lookup(self, client: BlueHive) -> None:
        with client.providers.with_streaming_response.lookup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = response.parse()
            assert_matches_type(ProviderLookupResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProviders:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_lookup(self, async_client: AsyncBlueHive) -> None:
        provider = await async_client.providers.lookup()
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_lookup_with_all_params(self, async_client: AsyncBlueHive) -> None:
        provider = await async_client.providers.lookup(
            firstname="firstname",
            lastname="lastname",
            npi="npi",
            zipcode="zipcode",
        )
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_lookup(self, async_client: AsyncBlueHive) -> None:
        response = await async_client.providers.with_raw_response.lookup()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provider = await response.parse()
        assert_matches_type(ProviderLookupResponse, provider, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_lookup(self, async_client: AsyncBlueHive) -> None:
        async with async_client.providers.with_streaming_response.lookup() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provider = await response.parse()
            assert_matches_type(ProviderLookupResponse, provider, path=["response"])

        assert cast(Any, response.is_closed) is True
