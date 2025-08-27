# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestXcures:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_make_request(self, client: SampleHealthcare) -> None:
        xcure = client.v2.events.integrations.xcures.make_request(
            slug="slug",
            method="GET",
            path="path",
        )
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_make_request_with_all_params(self, client: SampleHealthcare) -> None:
        xcure = client.v2.events.integrations.xcures.make_request(
            slug="slug",
            method="GET",
            path="path",
            body={"foo": "bar"},
            parameters={"foo": "bar"},
        )
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_make_request(self, client: SampleHealthcare) -> None:
        response = client.v2.events.integrations.xcures.with_raw_response.make_request(
            slug="slug",
            method="GET",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        xcure = response.parse()
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_make_request(self, client: SampleHealthcare) -> None:
        with client.v2.events.integrations.xcures.with_streaming_response.make_request(
            slug="slug",
            method="GET",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            xcure = response.parse()
            assert_matches_type(object, xcure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_make_request(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            client.v2.events.integrations.xcures.with_raw_response.make_request(
                slug="",
                method="GET",
                path="path",
            )


class TestAsyncXcures:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_make_request(self, async_client: AsyncSampleHealthcare) -> None:
        xcure = await async_client.v2.events.integrations.xcures.make_request(
            slug="slug",
            method="GET",
            path="path",
        )
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_make_request_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        xcure = await async_client.v2.events.integrations.xcures.make_request(
            slug="slug",
            method="GET",
            path="path",
            body={"foo": "bar"},
            parameters={"foo": "bar"},
        )
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_make_request(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.events.integrations.xcures.with_raw_response.make_request(
            slug="slug",
            method="GET",
            path="path",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        xcure = await response.parse()
        assert_matches_type(object, xcure, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_make_request(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.events.integrations.xcures.with_streaming_response.make_request(
            slug="slug",
            method="GET",
            path="path",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            xcure = await response.parse()
            assert_matches_type(object, xcure, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_make_request(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `slug` but received ''"):
            await async_client.v2.events.integrations.xcures.with_raw_response.make_request(
                slug="",
                method="GET",
                path="path",
            )
