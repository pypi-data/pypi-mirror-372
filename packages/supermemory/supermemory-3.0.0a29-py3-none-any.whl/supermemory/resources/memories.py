# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Mapping, cast
from typing_extensions import Literal

import httpx

from ..types import memory_add_params, memory_list_params, memory_update_params, memory_upload_file_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.memory_add_response import MemoryAddResponse
from ..types.memory_get_response import MemoryGetResponse
from ..types.memory_list_response import MemoryListResponse
from ..types.memory_update_response import MemoryUpdateResponse
from ..types.memory_upload_file_response import MemoryUploadFileResponse

__all__ = ["MemoriesResource", "AsyncMemoriesResource"]


class MemoriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MemoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return MemoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MemoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return MemoriesResourceWithStreamingResponse(self)

    def update(
        self,
        id: str,
        *,
        container_tag: str | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, Union[str, float, bool]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryUpdateResponse:
        """
        Update a memory with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this memory should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group memories.

          content: The content to extract and process into a memory. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the memory. This could be an ID from your database that
              will uniquely identify this memory.

          metadata: Optional metadata for the memory. This is used to store additional information
              about the memory. You can use this to store any additional information you need
              about the memory. Metadata can be filtered through. Keys must be strings and are
              case sensitive. Values can be strings, numbers, or booleans. You cannot nest
              objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._patch(
            f"/v3/memories/{id}",
            body=maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                memory_update_params.MemoryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUpdateResponse,
        )

    def list(
        self,
        *,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        filters: str | NotGiven = NOT_GIVEN,
        include_content: bool | NotGiven = NOT_GIVEN,
        limit: Union[str, float] | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        page: Union[str, float] | NotGiven = NOT_GIVEN,
        sort: Literal["createdAt", "updatedAt"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryListResponse:
        """
        Retrieves a paginated list of memories with their metadata and workflow status

        Args:
          container_tags: Optional tags this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          filters: Optional filters to apply to the search

          include_content: Whether to include the content field in the response. Warning: This can make
              responses significantly larger.

          limit: Number of items per page

          order: Sort order

          page: Page number to fetch

          sort: Field to sort by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/memories/list",
            body=maybe_transform(
                {
                    "container_tags": container_tags,
                    "filters": filters,
                    "include_content": include_content,
                    "limit": limit,
                    "order": order,
                    "page": page,
                    "sort": sort,
                },
                memory_list_params.MemoryListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryListResponse,
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
        Delete a memory by ID

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
            f"/v3/memories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def add(
        self,
        *,
        container_tag: str | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, Union[str, float, bool]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryAddResponse:
        """
        Add a memory with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this memory should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group memories.

          content: The content to extract and process into a memory. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the memory. This could be an ID from your database that
              will uniquely identify this memory.

          metadata: Optional metadata for the memory. This is used to store additional information
              about the memory. You can use this to store any additional information you need
              about the memory. Metadata can be filtered through. Keys must be strings and are
              case sensitive. Values can be strings, numbers, or booleans. You cannot nest
              objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v3/memories",
            body=maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                memory_add_params.MemoryAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryAddResponse,
        )

    def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryGetResponse:
        """
        Get a memory by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/v3/memories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryGetResponse,
        )

    def upload_file(
        self,
        *,
        file: FileTypes,
        container_tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryUploadFileResponse:
        """
        Upload a file to be processed

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "container_tags": container_tags,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/v3/memories/file",
            body=maybe_transform(body, memory_upload_file_params.MemoryUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUploadFileResponse,
        )


class AsyncMemoriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMemoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/supermemoryai/python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMemoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMemoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/supermemoryai/python-sdk#with_streaming_response
        """
        return AsyncMemoriesResourceWithStreamingResponse(self)

    async def update(
        self,
        id: str,
        *,
        container_tag: str | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, Union[str, float, bool]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryUpdateResponse:
        """
        Update a memory with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this memory should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group memories.

          content: The content to extract and process into a memory. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the memory. This could be an ID from your database that
              will uniquely identify this memory.

          metadata: Optional metadata for the memory. This is used to store additional information
              about the memory. You can use this to store any additional information you need
              about the memory. Metadata can be filtered through. Keys must be strings and are
              case sensitive. Values can be strings, numbers, or booleans. You cannot nest
              objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._patch(
            f"/v3/memories/{id}",
            body=await async_maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                memory_update_params.MemoryUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUpdateResponse,
        )

    async def list(
        self,
        *,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        filters: str | NotGiven = NOT_GIVEN,
        include_content: bool | NotGiven = NOT_GIVEN,
        limit: Union[str, float] | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        page: Union[str, float] | NotGiven = NOT_GIVEN,
        sort: Literal["createdAt", "updatedAt"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryListResponse:
        """
        Retrieves a paginated list of memories with their metadata and workflow status

        Args:
          container_tags: Optional tags this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          filters: Optional filters to apply to the search

          include_content: Whether to include the content field in the response. Warning: This can make
              responses significantly larger.

          limit: Number of items per page

          order: Sort order

          page: Page number to fetch

          sort: Field to sort by

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/memories/list",
            body=await async_maybe_transform(
                {
                    "container_tags": container_tags,
                    "filters": filters,
                    "include_content": include_content,
                    "limit": limit,
                    "order": order,
                    "page": page,
                    "sort": sort,
                },
                memory_list_params.MemoryListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryListResponse,
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
        Delete a memory by ID

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
            f"/v3/memories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def add(
        self,
        *,
        container_tag: str | NotGiven = NOT_GIVEN,
        container_tags: List[str] | NotGiven = NOT_GIVEN,
        content: str | NotGiven = NOT_GIVEN,
        custom_id: str | NotGiven = NOT_GIVEN,
        metadata: Dict[str, Union[str, float, bool]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryAddResponse:
        """
        Add a memory with any content type (text, url, file, etc.) and metadata

        Args:
          container_tag: Optional tag this memory should be containerized by. This can be an ID for your
              user, a project ID, or any other identifier you wish to use to group memories.

          container_tags: (DEPRECATED: Use containerTag instead) Optional tags this memory should be
              containerized by. This can be an ID for your user, a project ID, or any other
              identifier you wish to use to group memories.

          content: The content to extract and process into a memory. This can be a URL to a
              website, a PDF, an image, or a video.

              Plaintext: Any plaintext format

              URL: A URL to a website, PDF, image, or video

              We automatically detect the content type from the url's response format.

          custom_id: Optional custom ID of the memory. This could be an ID from your database that
              will uniquely identify this memory.

          metadata: Optional metadata for the memory. This is used to store additional information
              about the memory. You can use this to store any additional information you need
              about the memory. Metadata can be filtered through. Keys must be strings and are
              case sensitive. Values can be strings, numbers, or booleans. You cannot nest
              objects.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v3/memories",
            body=await async_maybe_transform(
                {
                    "container_tag": container_tag,
                    "container_tags": container_tags,
                    "content": content,
                    "custom_id": custom_id,
                    "metadata": metadata,
                },
                memory_add_params.MemoryAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryAddResponse,
        )

    async def get(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryGetResponse:
        """
        Get a memory by ID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/v3/memories/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryGetResponse,
        )

    async def upload_file(
        self,
        *,
        file: FileTypes,
        container_tags: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> MemoryUploadFileResponse:
        """
        Upload a file to be processed

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "container_tags": container_tags,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/v3/memories/file",
            body=await async_maybe_transform(body, memory_upload_file_params.MemoryUploadFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemoryUploadFileResponse,
        )


class MemoriesResourceWithRawResponse:
    def __init__(self, memories: MemoriesResource) -> None:
        self._memories = memories

        self.update = to_raw_response_wrapper(
            memories.update,
        )
        self.list = to_raw_response_wrapper(
            memories.list,
        )
        self.delete = to_raw_response_wrapper(
            memories.delete,
        )
        self.add = to_raw_response_wrapper(
            memories.add,
        )
        self.get = to_raw_response_wrapper(
            memories.get,
        )
        self.upload_file = to_raw_response_wrapper(
            memories.upload_file,
        )


class AsyncMemoriesResourceWithRawResponse:
    def __init__(self, memories: AsyncMemoriesResource) -> None:
        self._memories = memories

        self.update = async_to_raw_response_wrapper(
            memories.update,
        )
        self.list = async_to_raw_response_wrapper(
            memories.list,
        )
        self.delete = async_to_raw_response_wrapper(
            memories.delete,
        )
        self.add = async_to_raw_response_wrapper(
            memories.add,
        )
        self.get = async_to_raw_response_wrapper(
            memories.get,
        )
        self.upload_file = async_to_raw_response_wrapper(
            memories.upload_file,
        )


class MemoriesResourceWithStreamingResponse:
    def __init__(self, memories: MemoriesResource) -> None:
        self._memories = memories

        self.update = to_streamed_response_wrapper(
            memories.update,
        )
        self.list = to_streamed_response_wrapper(
            memories.list,
        )
        self.delete = to_streamed_response_wrapper(
            memories.delete,
        )
        self.add = to_streamed_response_wrapper(
            memories.add,
        )
        self.get = to_streamed_response_wrapper(
            memories.get,
        )
        self.upload_file = to_streamed_response_wrapper(
            memories.upload_file,
        )


class AsyncMemoriesResourceWithStreamingResponse:
    def __init__(self, memories: AsyncMemoriesResource) -> None:
        self._memories = memories

        self.update = async_to_streamed_response_wrapper(
            memories.update,
        )
        self.list = async_to_streamed_response_wrapper(
            memories.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            memories.delete,
        )
        self.add = async_to_streamed_response_wrapper(
            memories.add,
        )
        self.get = async_to_streamed_response_wrapper(
            memories.get,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            memories.upload_file,
        )
