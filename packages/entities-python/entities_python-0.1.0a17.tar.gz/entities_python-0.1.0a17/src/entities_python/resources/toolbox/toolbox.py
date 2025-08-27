# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .tools import (
    ToolsResource,
    AsyncToolsResource,
    ToolsResourceWithRawResponse,
    AsyncToolsResourceWithRawResponse,
    ToolsResourceWithStreamingResponse,
    AsyncToolsResourceWithStreamingResponse,
)
from .adapters import (
    AdaptersResource,
    AsyncAdaptersResource,
    AdaptersResourceWithRawResponse,
    AsyncAdaptersResourceWithRawResponse,
    AdaptersResourceWithStreamingResponse,
    AsyncAdaptersResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ToolboxResource", "AsyncToolboxResource"]


class ToolboxResource(SyncAPIResource):
    @cached_property
    def adapters(self) -> AdaptersResource:
        return AdaptersResource(self._client)

    @cached_property
    def tools(self) -> ToolsResource:
        return ToolsResource(self._client)

    @cached_property
    def with_raw_response(self) -> ToolboxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return ToolboxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ToolboxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return ToolboxResourceWithStreamingResponse(self)


class AsyncToolboxResource(AsyncAPIResource):
    @cached_property
    def adapters(self) -> AsyncAdaptersResource:
        return AsyncAdaptersResource(self._client)

    @cached_property
    def tools(self) -> AsyncToolsResource:
        return AsyncToolsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncToolboxResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncToolboxResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncToolboxResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncToolboxResourceWithStreamingResponse(self)


class ToolboxResourceWithRawResponse:
    def __init__(self, toolbox: ToolboxResource) -> None:
        self._toolbox = toolbox

    @cached_property
    def adapters(self) -> AdaptersResourceWithRawResponse:
        return AdaptersResourceWithRawResponse(self._toolbox.adapters)

    @cached_property
    def tools(self) -> ToolsResourceWithRawResponse:
        return ToolsResourceWithRawResponse(self._toolbox.tools)


class AsyncToolboxResourceWithRawResponse:
    def __init__(self, toolbox: AsyncToolboxResource) -> None:
        self._toolbox = toolbox

    @cached_property
    def adapters(self) -> AsyncAdaptersResourceWithRawResponse:
        return AsyncAdaptersResourceWithRawResponse(self._toolbox.adapters)

    @cached_property
    def tools(self) -> AsyncToolsResourceWithRawResponse:
        return AsyncToolsResourceWithRawResponse(self._toolbox.tools)


class ToolboxResourceWithStreamingResponse:
    def __init__(self, toolbox: ToolboxResource) -> None:
        self._toolbox = toolbox

    @cached_property
    def adapters(self) -> AdaptersResourceWithStreamingResponse:
        return AdaptersResourceWithStreamingResponse(self._toolbox.adapters)

    @cached_property
    def tools(self) -> ToolsResourceWithStreamingResponse:
        return ToolsResourceWithStreamingResponse(self._toolbox.tools)


class AsyncToolboxResourceWithStreamingResponse:
    def __init__(self, toolbox: AsyncToolboxResource) -> None:
        self._toolbox = toolbox

    @cached_property
    def adapters(self) -> AsyncAdaptersResourceWithStreamingResponse:
        return AsyncAdaptersResourceWithStreamingResponse(self._toolbox.adapters)

    @cached_property
    def tools(self) -> AsyncToolsResourceWithStreamingResponse:
        return AsyncToolsResourceWithStreamingResponse(self._toolbox.tools)
