# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime

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
from ..._base_client import make_request_options
from ...types.memory import drm_instance_create_params, drm_instance_update_params, drm_instance_log_messages_params
from ...types.memory.drm_instance import DrmInstance
from ...types.memory.drm_instance_list_response import DrmInstanceListResponse
from ...types.memory.drm_instance_get_messages_response import DrmInstanceGetMessagesResponse
from ...types.memory.drm_instance_log_messages_response import DrmInstanceLogMessagesResponse
from ...types.memory.drm_instance_get_memory_context_response import DrmInstanceGetMemoryContextResponse

__all__ = ["DrmInstancesResource", "AsyncDrmInstancesResource"]


class DrmInstancesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DrmInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return DrmInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DrmInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return DrmInstancesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str | NotGiven = NOT_GIVEN,
        summarizer_model: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/memory/drm-instances/",
            body=maybe_transform(
                {
                    "name": name,
                    "summarizer_model": summarizer_model,
                },
                drm_instance_create_params.DrmInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
        )

    def retrieve(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/memory/drm-instances/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
        )

    def update(
        self,
        id: int,
        *,
        name: str | NotGiven = NOT_GIVEN,
        summarizer_model: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/api/memory/drm-instances/{id}/",
            body=maybe_transform(
                {
                    "name": name,
                    "summarizer_model": summarizer_model,
                },
                drm_instance_update_params.DrmInstanceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
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
    ) -> DrmInstanceListResponse:
        return self._get(
            "/api/memory/drm-instances/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceListResponse,
        )

    def delete(
        self,
        id: int,
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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/memory/drm-instances/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_memory_context(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceGetMemoryContextResponse:
        """
        Get memory context for this DRM instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/memory/drm-instances/{id}/memory-context/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceGetMemoryContextResponse,
        )

    def get_messages(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceGetMessagesResponse:
        """
        Get messages for this DRM instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/api/memory/drm-instances/{id}/messages/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceGetMessagesResponse,
        )

    def log_messages(
        self,
        id: int,
        *,
        messages: Iterable[object],
        timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceLogMessagesResponse:
        """
        Log messages to this DRM instance

        Args:
          messages: Array of OpenAI-format messages

          timestamp: Optional timestamp for all messages (defaults to now)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            f"/api/memory/drm-instances/{id}/log-messages/",
            body=maybe_transform(
                {
                    "messages": messages,
                    "timestamp": timestamp,
                },
                drm_instance_log_messages_params.DrmInstanceLogMessagesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceLogMessagesResponse,
        )


class AsyncDrmInstancesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDrmInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDrmInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDrmInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncDrmInstancesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str | NotGiven = NOT_GIVEN,
        summarizer_model: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/memory/drm-instances/",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "summarizer_model": summarizer_model,
                },
                drm_instance_create_params.DrmInstanceCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
        )

    async def retrieve(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/memory/drm-instances/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
        )

    async def update(
        self,
        id: int,
        *,
        name: str | NotGiven = NOT_GIVEN,
        summarizer_model: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstance:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/api/memory/drm-instances/{id}/",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "summarizer_model": summarizer_model,
                },
                drm_instance_update_params.DrmInstanceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstance,
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
    ) -> DrmInstanceListResponse:
        return await self._get(
            "/api/memory/drm-instances/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceListResponse,
        )

    async def delete(
        self,
        id: int,
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
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/memory/drm-instances/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_memory_context(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceGetMemoryContextResponse:
        """
        Get memory context for this DRM instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/memory/drm-instances/{id}/memory-context/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceGetMemoryContextResponse,
        )

    async def get_messages(
        self,
        id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceGetMessagesResponse:
        """
        Get messages for this DRM instance

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/api/memory/drm-instances/{id}/messages/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceGetMessagesResponse,
        )

    async def log_messages(
        self,
        id: int,
        *,
        messages: Iterable[object],
        timestamp: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DrmInstanceLogMessagesResponse:
        """
        Log messages to this DRM instance

        Args:
          messages: Array of OpenAI-format messages

          timestamp: Optional timestamp for all messages (defaults to now)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            f"/api/memory/drm-instances/{id}/log-messages/",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "timestamp": timestamp,
                },
                drm_instance_log_messages_params.DrmInstanceLogMessagesParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DrmInstanceLogMessagesResponse,
        )


class DrmInstancesResourceWithRawResponse:
    def __init__(self, drm_instances: DrmInstancesResource) -> None:
        self._drm_instances = drm_instances

        self.create = to_raw_response_wrapper(
            drm_instances.create,
        )
        self.retrieve = to_raw_response_wrapper(
            drm_instances.retrieve,
        )
        self.update = to_raw_response_wrapper(
            drm_instances.update,
        )
        self.list = to_raw_response_wrapper(
            drm_instances.list,
        )
        self.delete = to_raw_response_wrapper(
            drm_instances.delete,
        )
        self.get_memory_context = to_raw_response_wrapper(
            drm_instances.get_memory_context,
        )
        self.get_messages = to_raw_response_wrapper(
            drm_instances.get_messages,
        )
        self.log_messages = to_raw_response_wrapper(
            drm_instances.log_messages,
        )


class AsyncDrmInstancesResourceWithRawResponse:
    def __init__(self, drm_instances: AsyncDrmInstancesResource) -> None:
        self._drm_instances = drm_instances

        self.create = async_to_raw_response_wrapper(
            drm_instances.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            drm_instances.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            drm_instances.update,
        )
        self.list = async_to_raw_response_wrapper(
            drm_instances.list,
        )
        self.delete = async_to_raw_response_wrapper(
            drm_instances.delete,
        )
        self.get_memory_context = async_to_raw_response_wrapper(
            drm_instances.get_memory_context,
        )
        self.get_messages = async_to_raw_response_wrapper(
            drm_instances.get_messages,
        )
        self.log_messages = async_to_raw_response_wrapper(
            drm_instances.log_messages,
        )


class DrmInstancesResourceWithStreamingResponse:
    def __init__(self, drm_instances: DrmInstancesResource) -> None:
        self._drm_instances = drm_instances

        self.create = to_streamed_response_wrapper(
            drm_instances.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            drm_instances.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            drm_instances.update,
        )
        self.list = to_streamed_response_wrapper(
            drm_instances.list,
        )
        self.delete = to_streamed_response_wrapper(
            drm_instances.delete,
        )
        self.get_memory_context = to_streamed_response_wrapper(
            drm_instances.get_memory_context,
        )
        self.get_messages = to_streamed_response_wrapper(
            drm_instances.get_messages,
        )
        self.log_messages = to_streamed_response_wrapper(
            drm_instances.log_messages,
        )


class AsyncDrmInstancesResourceWithStreamingResponse:
    def __init__(self, drm_instances: AsyncDrmInstancesResource) -> None:
        self._drm_instances = drm_instances

        self.create = async_to_streamed_response_wrapper(
            drm_instances.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            drm_instances.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            drm_instances.update,
        )
        self.list = async_to_streamed_response_wrapper(
            drm_instances.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            drm_instances.delete,
        )
        self.get_memory_context = async_to_streamed_response_wrapper(
            drm_instances.get_memory_context,
        )
        self.get_messages = async_to_streamed_response_wrapper(
            drm_instances.get_messages,
        )
        self.log_messages = async_to_streamed_response_wrapper(
            drm_instances.log_messages,
        )
