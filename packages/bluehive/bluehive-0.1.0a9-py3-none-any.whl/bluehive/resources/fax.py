# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import fax_send_params
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
from ..types.fax_send_response import FaxSendResponse
from ..types.fax_list_providers_response import FaxListProvidersResponse
from ..types.fax_retrieve_status_response import FaxRetrieveStatusResponse

__all__ = ["FaxResource", "AsyncFaxResource"]


class FaxResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FaxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FaxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FaxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#with_streaming_response
        """
        return FaxResourceWithStreamingResponse(self)

    def list_providers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxListProvidersResponse:
        """Get a list of available fax providers and their configuration status."""
        return self._get(
            "/v1/fax/providers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxListProvidersResponse,
        )

    def retrieve_status(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxRetrieveStatusResponse:
        """
        Retrieve the current status and details of a fax by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v1/fax/status/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxRetrieveStatusResponse,
        )

    def send(
        self,
        *,
        document: fax_send_params.Document,
        to: str,
        from_: str | NotGiven = NOT_GIVEN,
        provider: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxSendResponse:
        """
        Send a fax document to a specified number using the configured fax provider.

        Args:
          to: Recipient fax number (E.164 format preferred)

          from_: Sender fax number (optional, uses default if not provided)

          provider: Optional provider override (uses default if not specified)

          subject: Subject line for the fax

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/fax/send",
            body=maybe_transform(
                {
                    "document": document,
                    "to": to,
                    "from_": from_,
                    "provider": provider,
                    "subject": subject,
                },
                fax_send_params.FaxSendParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxSendResponse,
        )


class AsyncFaxResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFaxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFaxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFaxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#with_streaming_response
        """
        return AsyncFaxResourceWithStreamingResponse(self)

    async def list_providers(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxListProvidersResponse:
        """Get a list of available fax providers and their configuration status."""
        return await self._get(
            "/v1/fax/providers",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxListProvidersResponse,
        )

    async def retrieve_status(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxRetrieveStatusResponse:
        """
        Retrieve the current status and details of a fax by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v1/fax/status/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxRetrieveStatusResponse,
        )

    async def send(
        self,
        *,
        document: fax_send_params.Document,
        to: str,
        from_: str | NotGiven = NOT_GIVEN,
        provider: str | NotGiven = NOT_GIVEN,
        subject: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaxSendResponse:
        """
        Send a fax document to a specified number using the configured fax provider.

        Args:
          to: Recipient fax number (E.164 format preferred)

          from_: Sender fax number (optional, uses default if not provided)

          provider: Optional provider override (uses default if not specified)

          subject: Subject line for the fax

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/fax/send",
            body=await async_maybe_transform(
                {
                    "document": document,
                    "to": to,
                    "from_": from_,
                    "provider": provider,
                    "subject": subject,
                },
                fax_send_params.FaxSendParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FaxSendResponse,
        )


class FaxResourceWithRawResponse:
    def __init__(self, fax: FaxResource) -> None:
        self._fax = fax

        self.list_providers = to_raw_response_wrapper(
            fax.list_providers,
        )
        self.retrieve_status = to_raw_response_wrapper(
            fax.retrieve_status,
        )
        self.send = to_raw_response_wrapper(
            fax.send,
        )


class AsyncFaxResourceWithRawResponse:
    def __init__(self, fax: AsyncFaxResource) -> None:
        self._fax = fax

        self.list_providers = async_to_raw_response_wrapper(
            fax.list_providers,
        )
        self.retrieve_status = async_to_raw_response_wrapper(
            fax.retrieve_status,
        )
        self.send = async_to_raw_response_wrapper(
            fax.send,
        )


class FaxResourceWithStreamingResponse:
    def __init__(self, fax: FaxResource) -> None:
        self._fax = fax

        self.list_providers = to_streamed_response_wrapper(
            fax.list_providers,
        )
        self.retrieve_status = to_streamed_response_wrapper(
            fax.retrieve_status,
        )
        self.send = to_streamed_response_wrapper(
            fax.send,
        )


class AsyncFaxResourceWithStreamingResponse:
    def __init__(self, fax: AsyncFaxResource) -> None:
        self._fax = fax

        self.list_providers = async_to_streamed_response_wrapper(
            fax.list_providers,
        )
        self.retrieve_status = async_to_streamed_response_wrapper(
            fax.retrieve_status,
        )
        self.send = async_to_streamed_response_wrapper(
            fax.send,
        )
