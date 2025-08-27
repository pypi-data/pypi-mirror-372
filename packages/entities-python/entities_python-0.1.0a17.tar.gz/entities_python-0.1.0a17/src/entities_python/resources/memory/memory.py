# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from .drm_instances import (
    DrmInstancesResource,
    AsyncDrmInstancesResource,
    DrmInstancesResourceWithRawResponse,
    AsyncDrmInstancesResourceWithRawResponse,
    DrmInstancesResourceWithStreamingResponse,
    AsyncDrmInstancesResourceWithStreamingResponse,
)

__all__ = ["MemoryResource", "AsyncMemoryResource"]


class MemoryResource(SyncAPIResource):
    @cached_property
    def drm_instances(self) -> DrmInstancesResource:
        return DrmInstancesResource(self._client)

    @cached_property
    def with_raw_response(self) -> MemoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return MemoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MemoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return MemoryResourceWithStreamingResponse(self)


class AsyncMemoryResource(AsyncAPIResource):
    @cached_property
    def drm_instances(self) -> AsyncDrmInstancesResource:
        return AsyncDrmInstancesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncMemoryResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMemoryResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMemoryResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncMemoryResourceWithStreamingResponse(self)


class MemoryResourceWithRawResponse:
    def __init__(self, memory: MemoryResource) -> None:
        self._memory = memory

    @cached_property
    def drm_instances(self) -> DrmInstancesResourceWithRawResponse:
        return DrmInstancesResourceWithRawResponse(self._memory.drm_instances)


class AsyncMemoryResourceWithRawResponse:
    def __init__(self, memory: AsyncMemoryResource) -> None:
        self._memory = memory

    @cached_property
    def drm_instances(self) -> AsyncDrmInstancesResourceWithRawResponse:
        return AsyncDrmInstancesResourceWithRawResponse(self._memory.drm_instances)


class MemoryResourceWithStreamingResponse:
    def __init__(self, memory: MemoryResource) -> None:
        self._memory = memory

    @cached_property
    def drm_instances(self) -> DrmInstancesResourceWithStreamingResponse:
        return DrmInstancesResourceWithStreamingResponse(self._memory.drm_instances)


class AsyncMemoryResourceWithStreamingResponse:
    def __init__(self, memory: AsyncMemoryResource) -> None:
        self._memory = memory

    @cached_property
    def drm_instances(self) -> AsyncDrmInstancesResourceWithStreamingResponse:
        return AsyncDrmInstancesResourceWithStreamingResponse(self._memory.drm_instances)
