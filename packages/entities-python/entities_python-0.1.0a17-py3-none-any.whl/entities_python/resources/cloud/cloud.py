# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .runtimes import (
    RuntimesResource,
    AsyncRuntimesResource,
    RuntimesResourceWithRawResponse,
    AsyncRuntimesResourceWithRawResponse,
    RuntimesResourceWithStreamingResponse,
    AsyncRuntimesResourceWithStreamingResponse,
)
from ..._compat import cached_property
from .identities import (
    IdentitiesResource,
    AsyncIdentitiesResource,
    IdentitiesResourceWithRawResponse,
    AsyncIdentitiesResourceWithRawResponse,
    IdentitiesResourceWithStreamingResponse,
    AsyncIdentitiesResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["CloudResource", "AsyncCloudResource"]


class CloudResource(SyncAPIResource):
    @cached_property
    def runtimes(self) -> RuntimesResource:
        return RuntimesResource(self._client)

    @cached_property
    def identities(self) -> IdentitiesResource:
        return IdentitiesResource(self._client)

    @cached_property
    def with_raw_response(self) -> CloudResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return CloudResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CloudResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return CloudResourceWithStreamingResponse(self)


class AsyncCloudResource(AsyncAPIResource):
    @cached_property
    def runtimes(self) -> AsyncRuntimesResource:
        return AsyncRuntimesResource(self._client)

    @cached_property
    def identities(self) -> AsyncIdentitiesResource:
        return AsyncIdentitiesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncCloudResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncCloudResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCloudResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncCloudResourceWithStreamingResponse(self)


class CloudResourceWithRawResponse:
    def __init__(self, cloud: CloudResource) -> None:
        self._cloud = cloud

    @cached_property
    def runtimes(self) -> RuntimesResourceWithRawResponse:
        return RuntimesResourceWithRawResponse(self._cloud.runtimes)

    @cached_property
    def identities(self) -> IdentitiesResourceWithRawResponse:
        return IdentitiesResourceWithRawResponse(self._cloud.identities)


class AsyncCloudResourceWithRawResponse:
    def __init__(self, cloud: AsyncCloudResource) -> None:
        self._cloud = cloud

    @cached_property
    def runtimes(self) -> AsyncRuntimesResourceWithRawResponse:
        return AsyncRuntimesResourceWithRawResponse(self._cloud.runtimes)

    @cached_property
    def identities(self) -> AsyncIdentitiesResourceWithRawResponse:
        return AsyncIdentitiesResourceWithRawResponse(self._cloud.identities)


class CloudResourceWithStreamingResponse:
    def __init__(self, cloud: CloudResource) -> None:
        self._cloud = cloud

    @cached_property
    def runtimes(self) -> RuntimesResourceWithStreamingResponse:
        return RuntimesResourceWithStreamingResponse(self._cloud.runtimes)

    @cached_property
    def identities(self) -> IdentitiesResourceWithStreamingResponse:
        return IdentitiesResourceWithStreamingResponse(self._cloud.identities)


class AsyncCloudResourceWithStreamingResponse:
    def __init__(self, cloud: AsyncCloudResource) -> None:
        self._cloud = cloud

    @cached_property
    def runtimes(self) -> AsyncRuntimesResourceWithStreamingResponse:
        return AsyncRuntimesResourceWithStreamingResponse(self._cloud.runtimes)

    @cached_property
    def identities(self) -> AsyncIdentitiesResourceWithStreamingResponse:
        return AsyncIdentitiesResourceWithStreamingResponse(self._cloud.identities)
