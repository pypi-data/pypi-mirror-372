# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from bluehive import BlueHive, AsyncBlueHive
from tests.utils import assert_matches_type
from bluehive.types import FaxSendResponse, FaxListProvidersResponse, FaxRetrieveStatusResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFax:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_providers(self, client: BlueHive) -> None:
        fax = client.fax.list_providers()
        assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_providers(self, client: BlueHive) -> None:
        response = client.fax.with_raw_response.list_providers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = response.parse()
        assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_providers(self, client: BlueHive) -> None:
        with client.fax.with_streaming_response.list_providers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = response.parse()
            assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status(self, client: BlueHive) -> None:
        fax = client.fax.retrieve_status(
            "id",
        )
        assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_status(self, client: BlueHive) -> None:
        response = client.fax.with_raw_response.retrieve_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = response.parse()
        assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_status(self, client: BlueHive) -> None:
        with client.fax.with_streaming_response.retrieve_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = response.parse()
            assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_status(self, client: BlueHive) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.fax.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send(self, client: BlueHive) -> None:
        fax = client.fax.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        )
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_with_all_params(self, client: BlueHive) -> None:
        fax = client.fax.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
                "filename": "filename",
            },
            to="to",
            from_="from",
            provider="provider",
            subject="subject",
        )
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send(self, client: BlueHive) -> None:
        response = client.fax.with_raw_response.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = response.parse()
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send(self, client: BlueHive) -> None:
        with client.fax.with_streaming_response.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = response.parse()
            assert_matches_type(FaxSendResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFax:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_providers(self, async_client: AsyncBlueHive) -> None:
        fax = await async_client.fax.list_providers()
        assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_providers(self, async_client: AsyncBlueHive) -> None:
        response = await async_client.fax.with_raw_response.list_providers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = await response.parse()
        assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_providers(self, async_client: AsyncBlueHive) -> None:
        async with async_client.fax.with_streaming_response.list_providers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = await response.parse()
            assert_matches_type(FaxListProvidersResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncBlueHive) -> None:
        fax = await async_client.fax.retrieve_status(
            "id",
        )
        assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncBlueHive) -> None:
        response = await async_client.fax.with_raw_response.retrieve_status(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = await response.parse()
        assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncBlueHive) -> None:
        async with async_client.fax.with_streaming_response.retrieve_status(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = await response.parse()
            assert_matches_type(FaxRetrieveStatusResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_status(self, async_client: AsyncBlueHive) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.fax.with_raw_response.retrieve_status(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send(self, async_client: AsyncBlueHive) -> None:
        fax = await async_client.fax.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        )
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_with_all_params(self, async_client: AsyncBlueHive) -> None:
        fax = await async_client.fax.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
                "filename": "filename",
            },
            to="to",
            from_="from",
            provider="provider",
            subject="subject",
        )
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send(self, async_client: AsyncBlueHive) -> None:
        response = await async_client.fax.with_raw_response.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fax = await response.parse()
        assert_matches_type(FaxSendResponse, fax, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send(self, async_client: AsyncBlueHive) -> None:
        async with async_client.fax.with_streaming_response.send(
            document={
                "content": "content",
                "content_type": "application/pdf",
            },
            to="to",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fax = await response.parse()
            assert_matches_type(FaxSendResponse, fax, path=["response"])

        assert cast(Any, response.is_closed) is True
