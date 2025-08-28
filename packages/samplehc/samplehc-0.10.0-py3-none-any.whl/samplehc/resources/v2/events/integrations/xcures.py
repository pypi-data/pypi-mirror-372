# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.v2.events.integrations import xcure_make_request_params

__all__ = ["XcuresResource", "AsyncXcuresResource"]


class XcuresResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> XcuresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return XcuresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> XcuresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return XcuresResourceWithStreamingResponse(self)

    def make_request(
        self,
        slug: str,
        *,
        method: Literal["GET", "POST", "PUT"],
        path: str,
        body: Dict[str, object] | NotGiven = NOT_GIVEN,
        parameters: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Make an arbitrary request to xCures using the configured connection identified
        by slug. Refer to https://partner.xcures.com/api-docs for the full API
        documentation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/xcures/{slug}/request",
            body=maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "body": body,
                    "parameters": parameters,
                },
                xcure_make_request_params.XcureMakeRequestParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncXcuresResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncXcuresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncXcuresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncXcuresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncXcuresResourceWithStreamingResponse(self)

    async def make_request(
        self,
        slug: str,
        *,
        method: Literal["GET", "POST", "PUT"],
        path: str,
        body: Dict[str, object] | NotGiven = NOT_GIVEN,
        parameters: Dict[str, object] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Make an arbitrary request to xCures using the configured connection identified
        by slug. Refer to https://partner.xcures.com/api-docs for the full API
        documentation.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/xcures/{slug}/request",
            body=await async_maybe_transform(
                {
                    "method": method,
                    "path": path,
                    "body": body,
                    "parameters": parameters,
                },
                xcure_make_request_params.XcureMakeRequestParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class XcuresResourceWithRawResponse:
    def __init__(self, xcures: XcuresResource) -> None:
        self._xcures = xcures

        self.make_request = to_raw_response_wrapper(
            xcures.make_request,
        )


class AsyncXcuresResourceWithRawResponse:
    def __init__(self, xcures: AsyncXcuresResource) -> None:
        self._xcures = xcures

        self.make_request = async_to_raw_response_wrapper(
            xcures.make_request,
        )


class XcuresResourceWithStreamingResponse:
    def __init__(self, xcures: XcuresResource) -> None:
        self._xcures = xcures

        self.make_request = to_streamed_response_wrapper(
            xcures.make_request,
        )


class AsyncXcuresResourceWithStreamingResponse:
    def __init__(self, xcures: AsyncXcuresResource) -> None:
        self._xcures = xcures

        self.make_request = async_to_streamed_response_wrapper(
            xcures.make_request,
        )
