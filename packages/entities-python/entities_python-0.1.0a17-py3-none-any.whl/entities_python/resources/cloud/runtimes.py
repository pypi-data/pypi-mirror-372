# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.cloud import runtime_create_params, runtime_update_params
from ..._base_client import make_request_options
from ...types.cloud.runtime import Runtime
from ...types.cloud.runtime_list_response import RuntimeListResponse

__all__ = ["RuntimesResource", "AsyncRuntimesResource"]


class RuntimesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RuntimesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return RuntimesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RuntimesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return RuntimesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        identity: str,
        force_run: bool | NotGiven = NOT_GIVEN,
        max_turns: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/cloud/runtimes/",
            body=maybe_transform(
                {
                    "identity": identity,
                    "force_run": force_run,
                    "max_turns": max_turns,
                },
                runtime_create_params.RuntimeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/api/cloud/runtimes/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    def update(
        self,
        id: str,
        *,
        force_run: bool | NotGiven = NOT_GIVEN,
        identity: str | NotGiven = NOT_GIVEN,
        max_turns: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/api/cloud/runtimes/{id}/",
            body=maybe_transform(
                {
                    "force_run": force_run,
                    "identity": identity,
                    "max_turns": max_turns,
                },
                runtime_update_params.RuntimeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RuntimeListResponse:
        return self._get(
            "/api/cloud/runtimes/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RuntimeListResponse,
        )

    def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/cloud/runtimes/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncRuntimesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRuntimesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRuntimesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRuntimesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncRuntimesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        identity: str,
        force_run: bool | NotGiven = NOT_GIVEN,
        max_turns: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/cloud/runtimes/",
            body=await async_maybe_transform(
                {
                    "identity": identity,
                    "force_run": force_run,
                    "max_turns": max_turns,
                },
                runtime_create_params.RuntimeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/api/cloud/runtimes/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    async def update(
        self,
        id: str,
        *,
        force_run: bool | NotGiven = NOT_GIVEN,
        identity: str | NotGiven = NOT_GIVEN,
        max_turns: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Runtime:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/api/cloud/runtimes/{id}/",
            body=await async_maybe_transform(
                {
                    "force_run": force_run,
                    "identity": identity,
                    "max_turns": max_turns,
                },
                runtime_update_params.RuntimeUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Runtime,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RuntimeListResponse:
        return await self._get(
            "/api/cloud/runtimes/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RuntimeListResponse,
        )

    async def delete(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/cloud/runtimes/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class RuntimesResourceWithRawResponse:
    def __init__(self, runtimes: RuntimesResource) -> None:
        self._runtimes = runtimes

        self.create = to_raw_response_wrapper(
            runtimes.create,
        )
        self.retrieve = to_raw_response_wrapper(
            runtimes.retrieve,
        )
        self.update = to_raw_response_wrapper(
            runtimes.update,
        )
        self.list = to_raw_response_wrapper(
            runtimes.list,
        )
        self.delete = to_raw_response_wrapper(
            runtimes.delete,
        )


class AsyncRuntimesResourceWithRawResponse:
    def __init__(self, runtimes: AsyncRuntimesResource) -> None:
        self._runtimes = runtimes

        self.create = async_to_raw_response_wrapper(
            runtimes.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            runtimes.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            runtimes.update,
        )
        self.list = async_to_raw_response_wrapper(
            runtimes.list,
        )
        self.delete = async_to_raw_response_wrapper(
            runtimes.delete,
        )


class RuntimesResourceWithStreamingResponse:
    def __init__(self, runtimes: RuntimesResource) -> None:
        self._runtimes = runtimes

        self.create = to_streamed_response_wrapper(
            runtimes.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            runtimes.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            runtimes.update,
        )
        self.list = to_streamed_response_wrapper(
            runtimes.list,
        )
        self.delete = to_streamed_response_wrapper(
            runtimes.delete,
        )


class AsyncRuntimesResourceWithStreamingResponse:
    def __init__(self, runtimes: AsyncRuntimesResource) -> None:
        self._runtimes = runtimes

        self.create = async_to_streamed_response_wrapper(
            runtimes.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            runtimes.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            runtimes.update,
        )
        self.list = async_to_streamed_response_wrapper(
            runtimes.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            runtimes.delete,
        )
