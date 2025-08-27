# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
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
from ...types.cloud import identity_create_params, identity_update_params
from ..._base_client import make_request_options
from ...types.cloud.identity import Identity
from ...types.cloud.identity_list_response import IdentityListResponse

__all__ = ["IdentitiesResource", "AsyncIdentitiesResource"]


class IdentitiesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> IdentitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return IdentitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IdentitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return IdentitiesResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        memory: int,
        model: str,
        name: str,
        locked_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        sleep_until: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        timezone: str | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Identity:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/cloud/identities/",
            body=maybe_transform(
                {
                    "memory": memory,
                    "model": model,
                    "name": name,
                    "locked_at": locked_at,
                    "sleep_until": sleep_until,
                    "system_prompt": system_prompt,
                    "timezone": timezone,
                    "tools": tools,
                },
                identity_create_params.IdentityCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
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
    ) -> Identity:
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
            f"/api/cloud/identities/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
        )

    def update(
        self,
        id: str,
        *,
        memory: int,
        model: str,
        name: str,
        locked_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        sleep_until: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        timezone: str | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Identity:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/api/cloud/identities/{id}/",
            body=maybe_transform(
                {
                    "memory": memory,
                    "model": model,
                    "name": name,
                    "locked_at": locked_at,
                    "sleep_until": sleep_until,
                    "system_prompt": system_prompt,
                    "timezone": timezone,
                    "tools": tools,
                },
                identity_update_params.IdentityUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
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
    ) -> IdentityListResponse:
        return self._get(
            "/api/cloud/identities/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityListResponse,
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
            f"/api/cloud/identities/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncIdentitiesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncIdentitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Orin-Labs/entities-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIdentitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIdentitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Orin-Labs/entities-python#with_streaming_response
        """
        return AsyncIdentitiesResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        memory: int,
        model: str,
        name: str,
        locked_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        sleep_until: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        timezone: str | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Identity:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/cloud/identities/",
            body=await async_maybe_transform(
                {
                    "memory": memory,
                    "model": model,
                    "name": name,
                    "locked_at": locked_at,
                    "sleep_until": sleep_until,
                    "system_prompt": system_prompt,
                    "timezone": timezone,
                    "tools": tools,
                },
                identity_create_params.IdentityCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
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
    ) -> Identity:
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
            f"/api/cloud/identities/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
        )

    async def update(
        self,
        id: str,
        *,
        memory: int,
        model: str,
        name: str,
        locked_at: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        sleep_until: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        system_prompt: str | NotGiven = NOT_GIVEN,
        timezone: str | NotGiven = NOT_GIVEN,
        tools: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Identity:
        """
        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/api/cloud/identities/{id}/",
            body=await async_maybe_transform(
                {
                    "memory": memory,
                    "model": model,
                    "name": name,
                    "locked_at": locked_at,
                    "sleep_until": sleep_until,
                    "system_prompt": system_prompt,
                    "timezone": timezone,
                    "tools": tools,
                },
                identity_update_params.IdentityUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Identity,
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
    ) -> IdentityListResponse:
        return await self._get(
            "/api/cloud/identities/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IdentityListResponse,
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
            f"/api/cloud/identities/{id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class IdentitiesResourceWithRawResponse:
    def __init__(self, identities: IdentitiesResource) -> None:
        self._identities = identities

        self.create = to_raw_response_wrapper(
            identities.create,
        )
        self.retrieve = to_raw_response_wrapper(
            identities.retrieve,
        )
        self.update = to_raw_response_wrapper(
            identities.update,
        )
        self.list = to_raw_response_wrapper(
            identities.list,
        )
        self.delete = to_raw_response_wrapper(
            identities.delete,
        )


class AsyncIdentitiesResourceWithRawResponse:
    def __init__(self, identities: AsyncIdentitiesResource) -> None:
        self._identities = identities

        self.create = async_to_raw_response_wrapper(
            identities.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            identities.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            identities.update,
        )
        self.list = async_to_raw_response_wrapper(
            identities.list,
        )
        self.delete = async_to_raw_response_wrapper(
            identities.delete,
        )


class IdentitiesResourceWithStreamingResponse:
    def __init__(self, identities: IdentitiesResource) -> None:
        self._identities = identities

        self.create = to_streamed_response_wrapper(
            identities.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            identities.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            identities.update,
        )
        self.list = to_streamed_response_wrapper(
            identities.list,
        )
        self.delete = to_streamed_response_wrapper(
            identities.delete,
        )


class AsyncIdentitiesResourceWithStreamingResponse:
    def __init__(self, identities: AsyncIdentitiesResource) -> None:
        self._identities = identities

        self.create = async_to_streamed_response_wrapper(
            identities.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            identities.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            identities.update,
        )
        self.list = async_to_streamed_response_wrapper(
            identities.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            identities.delete,
        )
