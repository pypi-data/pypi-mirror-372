# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import provider_lookup_params
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
from ..types.provider_lookup_response import ProviderLookupResponse

__all__ = ["ProvidersResource", "AsyncProvidersResource"]


class ProvidersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#with_streaming_response
        """
        return ProvidersResourceWithStreamingResponse(self)

    def lookup(
        self,
        *,
        firstname: str | NotGiven = NOT_GIVEN,
        lastname: str | NotGiven = NOT_GIVEN,
        npi: str | NotGiven = NOT_GIVEN,
        zipcode: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProviderLookupResponse:
        """
        Search for healthcare providers by NPI number, name, or location proximity.

        Args:
          firstname: Provider first name

          lastname: Provider last name

          npi: Provider NPI number

          zipcode: ZIP code to filter results by proximity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/providers/lookup",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "firstname": firstname,
                        "lastname": lastname,
                        "npi": npi,
                        "zipcode": zipcode,
                    },
                    provider_lookup_params.ProviderLookupParams,
                ),
            ),
            cast_to=ProviderLookupResponse,
        )


class AsyncProvidersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProvidersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProvidersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProvidersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/bluehive-health/bluehive-sdk-python#with_streaming_response
        """
        return AsyncProvidersResourceWithStreamingResponse(self)

    async def lookup(
        self,
        *,
        firstname: str | NotGiven = NOT_GIVEN,
        lastname: str | NotGiven = NOT_GIVEN,
        npi: str | NotGiven = NOT_GIVEN,
        zipcode: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProviderLookupResponse:
        """
        Search for healthcare providers by NPI number, name, or location proximity.

        Args:
          firstname: Provider first name

          lastname: Provider last name

          npi: Provider NPI number

          zipcode: ZIP code to filter results by proximity

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/providers/lookup",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "firstname": firstname,
                        "lastname": lastname,
                        "npi": npi,
                        "zipcode": zipcode,
                    },
                    provider_lookup_params.ProviderLookupParams,
                ),
            ),
            cast_to=ProviderLookupResponse,
        )


class ProvidersResourceWithRawResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.lookup = to_raw_response_wrapper(
            providers.lookup,
        )


class AsyncProvidersResourceWithRawResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.lookup = async_to_raw_response_wrapper(
            providers.lookup,
        )


class ProvidersResourceWithStreamingResponse:
    def __init__(self, providers: ProvidersResource) -> None:
        self._providers = providers

        self.lookup = to_streamed_response_wrapper(
            providers.lookup,
        )


class AsyncProvidersResourceWithStreamingResponse:
    def __init__(self, providers: AsyncProvidersResource) -> None:
        self._providers = providers

        self.lookup = async_to_streamed_response_wrapper(
            providers.lookup,
        )
