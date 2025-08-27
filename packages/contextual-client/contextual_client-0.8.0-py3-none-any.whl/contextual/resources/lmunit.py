# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import lmunit_create_params
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
from ..types.lmunit_create_response import LMUnitCreateResponse

__all__ = ["LMUnitResource", "AsyncLMUnitResource"]


class LMUnitResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LMUnitResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return LMUnitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LMUnitResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return LMUnitResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        query: str,
        response: str,
        unit_test: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LMUnitCreateResponse:
        """
        Given a `query`, `response`, and a `unit_test`, return the response's `score` on
        the unit test on a 5-point continuous scale. The total input cannot exceed 7000
        tokens.

        See a code example in [our blog post](https://contextual.ai/news/lmunit/). Email
        [lmunit-feedback@contextual.ai](mailto:lmunit-feedback@contextual.ai) with any
        feedback or questions.

        > 🚀 Obtain an LMUnit API key by completing
        > [this form](https://contextual.ai/request-lmunit-api/)

        Args:
          query: The prompt to which the model responds

          response: The model response to evaluate

          unit_test: A natural language statement or question against which to evaluate the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/lmunit",
            body=maybe_transform(
                {
                    "query": query,
                    "response": response,
                    "unit_test": unit_test,
                },
                lmunit_create_params.LMUnitCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LMUnitCreateResponse,
        )


class AsyncLMUnitResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLMUnitResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLMUnitResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLMUnitResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return AsyncLMUnitResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        query: str,
        response: str,
        unit_test: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LMUnitCreateResponse:
        """
        Given a `query`, `response`, and a `unit_test`, return the response's `score` on
        the unit test on a 5-point continuous scale. The total input cannot exceed 7000
        tokens.

        See a code example in [our blog post](https://contextual.ai/news/lmunit/). Email
        [lmunit-feedback@contextual.ai](mailto:lmunit-feedback@contextual.ai) with any
        feedback or questions.

        > 🚀 Obtain an LMUnit API key by completing
        > [this form](https://contextual.ai/request-lmunit-api/)

        Args:
          query: The prompt to which the model responds

          response: The model response to evaluate

          unit_test: A natural language statement or question against which to evaluate the response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/lmunit",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "response": response,
                    "unit_test": unit_test,
                },
                lmunit_create_params.LMUnitCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LMUnitCreateResponse,
        )


class LMUnitResourceWithRawResponse:
    def __init__(self, lmunit: LMUnitResource) -> None:
        self._lmunit = lmunit

        self.create = to_raw_response_wrapper(
            lmunit.create,
        )


class AsyncLMUnitResourceWithRawResponse:
    def __init__(self, lmunit: AsyncLMUnitResource) -> None:
        self._lmunit = lmunit

        self.create = async_to_raw_response_wrapper(
            lmunit.create,
        )


class LMUnitResourceWithStreamingResponse:
    def __init__(self, lmunit: LMUnitResource) -> None:
        self._lmunit = lmunit

        self.create = to_streamed_response_wrapper(
            lmunit.create,
        )


class AsyncLMUnitResourceWithStreamingResponse:
    def __init__(self, lmunit: AsyncLMUnitResource) -> None:
        self._lmunit = lmunit

        self.create = async_to_streamed_response_wrapper(
            lmunit.create,
        )
