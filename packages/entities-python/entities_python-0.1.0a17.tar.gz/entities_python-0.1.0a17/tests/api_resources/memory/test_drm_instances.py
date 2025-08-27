# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from entities_python import Entities, AsyncEntities
from entities_python._utils import parse_datetime
from entities_python.types.memory import (
    DrmInstance,
    DrmInstanceListResponse,
    DrmInstanceGetMessagesResponse,
    DrmInstanceLogMessagesResponse,
    DrmInstanceGetMemoryContextResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDrmInstances:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.create()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.create(
            name="name",
            summarizer_model="summarizer_model",
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.retrieve(
            0,
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.update(
            id=0,
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.update(
            id=0,
            name="name",
            summarizer_model="summarizer_model",
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.update(
            id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.update(
            id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.list()
        assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.delete(
            0,
        )
        assert drm_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert drm_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert drm_instance is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_memory_context(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.get_memory_context(
            0,
        )
        assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_memory_context(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.get_memory_context(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_memory_context(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.get_memory_context(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_messages(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.get_messages(
            0,
        )
        assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_messages(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.get_messages(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_messages(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.get_messages(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_log_messages(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.log_messages(
            id=0,
            messages=[{}],
        )
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_log_messages_with_all_params(self, client: Entities) -> None:
        drm_instance = client.memory.drm_instances.log_messages(
            id=0,
            messages=[{}],
            timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_log_messages(self, client: Entities) -> None:
        response = client.memory.drm_instances.with_raw_response.log_messages(
            id=0,
            messages=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = response.parse()
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_log_messages(self, client: Entities) -> None:
        with client.memory.drm_instances.with_streaming_response.log_messages(
            id=0,
            messages=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = response.parse()
            assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDrmInstances:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.create()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.create(
            name="name",
            summarizer_model="summarizer_model",
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.retrieve(
            0,
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.update(
            id=0,
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.update(
            id=0,
            name="name",
            summarizer_model="summarizer_model",
        )
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.update(
            id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstance, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.update(
            id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstance, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.list()
        assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstanceListResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.delete(
            0,
        )
        assert drm_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.delete(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert drm_instance is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.delete(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert drm_instance is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_memory_context(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.get_memory_context(
            0,
        )
        assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_memory_context(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.get_memory_context(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_memory_context(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.get_memory_context(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstanceGetMemoryContextResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_messages(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.get_messages(
            0,
        )
        assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_messages(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.get_messages(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_messages(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.get_messages(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstanceGetMessagesResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_log_messages(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.log_messages(
            id=0,
            messages=[{}],
        )
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_log_messages_with_all_params(self, async_client: AsyncEntities) -> None:
        drm_instance = await async_client.memory.drm_instances.log_messages(
            id=0,
            messages=[{}],
            timestamp=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_log_messages(self, async_client: AsyncEntities) -> None:
        response = await async_client.memory.drm_instances.with_raw_response.log_messages(
            id=0,
            messages=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        drm_instance = await response.parse()
        assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_log_messages(self, async_client: AsyncEntities) -> None:
        async with async_client.memory.drm_instances.with_streaming_response.log_messages(
            id=0,
            messages=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            drm_instance = await response.parse()
            assert_matches_type(DrmInstanceLogMessagesResponse, drm_instance, path=["response"])

        assert cast(Any, response.is_closed) is True
