# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, Optional, cast

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.enterprise_api import recreate_create_params, recreate_retrieve_status_params
from ...types.enterprise_api.enterprise_api_response import EnterpriseAPIResponse
from ...types.enterprise_api.recreate_get_json_response import RecreateGetJsonResponse

__all__ = ["RecreateResource", "AsyncRecreateResource"]


class RecreateResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RecreateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#accessing-raw-response-data-eg-headers
        """
        return RecreateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RecreateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#with_streaming_response
        """
        return RecreateResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        file: FileTypes,
        selected_pages: str,
        is_ppt_process_enabled: str | NotGiven = NOT_GIVEN,
        is_xls_process_charts_enabled: str | NotGiven = NOT_GIVEN,
        is_xls_process_tables_enabled: str | NotGiven = NOT_GIVEN,
        selected_table_format: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """
        Enterprise Create Recreate

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "selected_pages": selected_pages,
                "is_ppt_process_enabled": is_ppt_process_enabled,
                "is_xls_process_charts_enabled": is_xls_process_charts_enabled,
                "is_xls_process_tables_enabled": is_xls_process_tables_enabled,
                "selected_table_format": selected_table_format,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/enterprise-api/recreate/",
            body=maybe_transform(body, recreate_create_params.RecreateCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    def get_json(
        self,
        recreate_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RecreateGetJsonResponse:
        """
        Return the permanent table memory for a recreate in simplified JSON form.

        Shape: {"tables": [{"headers": [...], "rows": [{"row_identifier": str, "cells":
        [...]}]}]}

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recreate_id:
            raise ValueError(f"Expected a non-empty value for `recreate_id` but received {recreate_id!r}")
        return self._get(
            f"/enterprise-api/recreate/{recreate_id}/to_json",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RecreateGetJsonResponse,
        )

    def hide(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """Enterprise Hide Recreate"""
        return self._post(
            "/enterprise-api/recreate/hide/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    def retrieve_status(
        self,
        *,
        recreate_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """
        Enterprise Fetch Recreate Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/enterprise-api/recreate/status/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"recreate_id": recreate_id}, recreate_retrieve_status_params.RecreateRetrieveStatusParams
                ),
            ),
            cast_to=EnterpriseAPIResponse,
        )


class AsyncRecreateResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRecreateResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRecreateResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRecreateResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#with_streaming_response
        """
        return AsyncRecreateResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: FileTypes,
        selected_pages: str,
        is_ppt_process_enabled: str | NotGiven = NOT_GIVEN,
        is_xls_process_charts_enabled: str | NotGiven = NOT_GIVEN,
        is_xls_process_tables_enabled: str | NotGiven = NOT_GIVEN,
        selected_table_format: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """
        Enterprise Create Recreate

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "selected_pages": selected_pages,
                "is_ppt_process_enabled": is_ppt_process_enabled,
                "is_xls_process_charts_enabled": is_xls_process_charts_enabled,
                "is_xls_process_tables_enabled": is_xls_process_tables_enabled,
                "selected_table_format": selected_table_format,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/enterprise-api/recreate/",
            body=await async_maybe_transform(body, recreate_create_params.RecreateCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    async def get_json(
        self,
        recreate_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> RecreateGetJsonResponse:
        """
        Return the permanent table memory for a recreate in simplified JSON form.

        Shape: {"tables": [{"headers": [...], "rows": [{"row_identifier": str, "cells":
        [...]}]}]}

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not recreate_id:
            raise ValueError(f"Expected a non-empty value for `recreate_id` but received {recreate_id!r}")
        return await self._get(
            f"/enterprise-api/recreate/{recreate_id}/to_json",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RecreateGetJsonResponse,
        )

    async def hide(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """Enterprise Hide Recreate"""
        return await self._post(
            "/enterprise-api/recreate/hide/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    async def retrieve_status(
        self,
        *,
        recreate_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """
        Enterprise Fetch Recreate Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/enterprise-api/recreate/status/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"recreate_id": recreate_id}, recreate_retrieve_status_params.RecreateRetrieveStatusParams
                ),
            ),
            cast_to=EnterpriseAPIResponse,
        )


class RecreateResourceWithRawResponse:
    def __init__(self, recreate: RecreateResource) -> None:
        self._recreate = recreate

        self.create = to_raw_response_wrapper(
            recreate.create,
        )
        self.get_json = to_raw_response_wrapper(
            recreate.get_json,
        )
        self.hide = to_raw_response_wrapper(
            recreate.hide,
        )
        self.retrieve_status = to_raw_response_wrapper(
            recreate.retrieve_status,
        )


class AsyncRecreateResourceWithRawResponse:
    def __init__(self, recreate: AsyncRecreateResource) -> None:
        self._recreate = recreate

        self.create = async_to_raw_response_wrapper(
            recreate.create,
        )
        self.get_json = async_to_raw_response_wrapper(
            recreate.get_json,
        )
        self.hide = async_to_raw_response_wrapper(
            recreate.hide,
        )
        self.retrieve_status = async_to_raw_response_wrapper(
            recreate.retrieve_status,
        )


class RecreateResourceWithStreamingResponse:
    def __init__(self, recreate: RecreateResource) -> None:
        self._recreate = recreate

        self.create = to_streamed_response_wrapper(
            recreate.create,
        )
        self.get_json = to_streamed_response_wrapper(
            recreate.get_json,
        )
        self.hide = to_streamed_response_wrapper(
            recreate.hide,
        )
        self.retrieve_status = to_streamed_response_wrapper(
            recreate.retrieve_status,
        )


class AsyncRecreateResourceWithStreamingResponse:
    def __init__(self, recreate: AsyncRecreateResource) -> None:
        self._recreate = recreate

        self.create = async_to_streamed_response_wrapper(
            recreate.create,
        )
        self.get_json = async_to_streamed_response_wrapper(
            recreate.get_json,
        )
        self.hide = async_to_streamed_response_wrapper(
            recreate.hide,
        )
        self.retrieve_status = async_to_streamed_response_wrapper(
            recreate.retrieve_status,
        )
