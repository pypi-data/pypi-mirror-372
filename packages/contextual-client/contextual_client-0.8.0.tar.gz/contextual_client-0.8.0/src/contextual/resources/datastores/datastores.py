# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...types import datastore_list_params, datastore_create_params, datastore_update_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .documents import (
    DocumentsResource,
    AsyncDocumentsResource,
    DocumentsResourceWithRawResponse,
    AsyncDocumentsResourceWithRawResponse,
    DocumentsResourceWithStreamingResponse,
    AsyncDocumentsResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncDatastoresPage, AsyncDatastoresPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.datastore import Datastore
from ...types.datastore_metadata import DatastoreMetadata
from ...types.create_datastore_response import CreateDatastoreResponse
from ...types.datastore_update_response import DatastoreUpdateResponse

__all__ = ["DatastoresResource", "AsyncDatastoresResource"]


class DatastoresResource(SyncAPIResource):
    @cached_property
    def documents(self) -> DocumentsResource:
        return DocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> DatastoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return DatastoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatastoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return DatastoresResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        configuration: datastore_create_params.Configuration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateDatastoreResponse:
        """Create a new `Datastore`.

        A `Datastore` is a collection of documents.

        Documents can be ingested into and
        deleted from a `Datastore`.

        A `Datastore` can be linked to one or more `Agents`, and conversely, an `Agent`
        can be associated with one or more `Datastores` to ground its responses with
        relevant data. This flexible many-to-many relationship allows `Agents` to draw
        from multiple sources of information. This linkage of `Datastore` to `Agent` is
        done through the `Create Agent` or `Edit Agent` APIs.

        > Note that self-serve users are currently required to create datastores through
        > our UI. Otherwise, they will receive the following message: "This endpoint is
        > disabled as you need to go through checkout. Please use the UI to make this
        > request."

        Args:
          name: Name of the datastore

          configuration: Configuration of the datastore. If not provided, default configuration is used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/datastores",
            body=maybe_transform(
                {
                    "name": name,
                    "configuration": configuration,
                },
                datastore_create_params.DatastoreCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateDatastoreResponse,
        )

    def update(
        self,
        datastore_id: str,
        *,
        configuration: datastore_update_params.Configuration | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatastoreUpdateResponse:
        """
        Edit Datastore Configuration

        Args:
          datastore_id: ID of the datastore to edit

          configuration: Configuration of the datastore. If not provided, current configuration is
              retained.

          name: Name of the datastore

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._put(
            f"/datastores/{datastore_id}",
            body=maybe_transform(
                {
                    "configuration": configuration,
                    "name": name,
                },
                datastore_update_params.DatastoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatastoreUpdateResponse,
        )

    def list(
        self,
        *,
        agent_id: str | NotGiven = NOT_GIVEN,
        cursor: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDatastoresPage[Datastore]:
        """
        Retrieve a list of `Datastores`.

        Performs `cursor`-based pagination if the number of `Datastores` exceeds the
        requested `limit`. The returned `cursor` can be passed to the next
        `GET /datastores` call to retrieve the next set of `Datastores`.

        Args:
          agent_id: ID of the agent used to filter datastores. If provided, only datastores linked
              to this agent will be returned.

          cursor: Cursor from the previous call to list datastores, used to retrieve the next set
              of results

          limit: Maximum number of datastores to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/datastores",
            page=SyncDatastoresPage[Datastore],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "agent_id": agent_id,
                        "cursor": cursor,
                        "limit": limit,
                    },
                    datastore_list_params.DatastoreListParams,
                ),
            ),
            model=Datastore,
        )

    def delete(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a given `Datastore`, including all the documents ingested into it.

        This
        operation is irreversible.

        This operation will fail with status code 400 if there is an active `Agent`
        associated with the `Datastore`.

        Args:
          datastore_id: ID of the datastore to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._delete(
            f"/datastores/{datastore_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def metadata(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatastoreMetadata:
        """
        Get the details of a given `Datastore`, including its name, create time, and the
        list of `Agents` which are currently configured to use the `Datastore`.

        Args:
          datastore_id: ID of the datastore for which to get details

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._get(
            f"/datastores/{datastore_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatastoreMetadata,
        )

    def reset(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Reset the give `Datastore`.

        This operation is irreversible and it deletes all
        the documents associated with the datastore.

        Args:
          datastore_id: ID of the datastore to edit

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._put(
            f"/datastores/{datastore_id}/reset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncDatastoresResource(AsyncAPIResource):
    @cached_property
    def documents(self) -> AsyncDocumentsResource:
        return AsyncDocumentsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncDatastoresResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDatastoresResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatastoresResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return AsyncDatastoresResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        configuration: datastore_create_params.Configuration | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CreateDatastoreResponse:
        """Create a new `Datastore`.

        A `Datastore` is a collection of documents.

        Documents can be ingested into and
        deleted from a `Datastore`.

        A `Datastore` can be linked to one or more `Agents`, and conversely, an `Agent`
        can be associated with one or more `Datastores` to ground its responses with
        relevant data. This flexible many-to-many relationship allows `Agents` to draw
        from multiple sources of information. This linkage of `Datastore` to `Agent` is
        done through the `Create Agent` or `Edit Agent` APIs.

        > Note that self-serve users are currently required to create datastores through
        > our UI. Otherwise, they will receive the following message: "This endpoint is
        > disabled as you need to go through checkout. Please use the UI to make this
        > request."

        Args:
          name: Name of the datastore

          configuration: Configuration of the datastore. If not provided, default configuration is used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/datastores",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "configuration": configuration,
                },
                datastore_create_params.DatastoreCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CreateDatastoreResponse,
        )

    async def update(
        self,
        datastore_id: str,
        *,
        configuration: datastore_update_params.Configuration | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatastoreUpdateResponse:
        """
        Edit Datastore Configuration

        Args:
          datastore_id: ID of the datastore to edit

          configuration: Configuration of the datastore. If not provided, current configuration is
              retained.

          name: Name of the datastore

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return await self._put(
            f"/datastores/{datastore_id}",
            body=await async_maybe_transform(
                {
                    "configuration": configuration,
                    "name": name,
                },
                datastore_update_params.DatastoreUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatastoreUpdateResponse,
        )

    def list(
        self,
        *,
        agent_id: str | NotGiven = NOT_GIVEN,
        cursor: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Datastore, AsyncDatastoresPage[Datastore]]:
        """
        Retrieve a list of `Datastores`.

        Performs `cursor`-based pagination if the number of `Datastores` exceeds the
        requested `limit`. The returned `cursor` can be passed to the next
        `GET /datastores` call to retrieve the next set of `Datastores`.

        Args:
          agent_id: ID of the agent used to filter datastores. If provided, only datastores linked
              to this agent will be returned.

          cursor: Cursor from the previous call to list datastores, used to retrieve the next set
              of results

          limit: Maximum number of datastores to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/datastores",
            page=AsyncDatastoresPage[Datastore],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "agent_id": agent_id,
                        "cursor": cursor,
                        "limit": limit,
                    },
                    datastore_list_params.DatastoreListParams,
                ),
            ),
            model=Datastore,
        )

    async def delete(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a given `Datastore`, including all the documents ingested into it.

        This
        operation is irreversible.

        This operation will fail with status code 400 if there is an active `Agent`
        associated with the `Datastore`.

        Args:
          datastore_id: ID of the datastore to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return await self._delete(
            f"/datastores/{datastore_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def metadata(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatastoreMetadata:
        """
        Get the details of a given `Datastore`, including its name, create time, and the
        list of `Agents` which are currently configured to use the `Datastore`.

        Args:
          datastore_id: ID of the datastore for which to get details

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return await self._get(
            f"/datastores/{datastore_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatastoreMetadata,
        )

    async def reset(
        self,
        datastore_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Reset the give `Datastore`.

        This operation is irreversible and it deletes all
        the documents associated with the datastore.

        Args:
          datastore_id: ID of the datastore to edit

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return await self._put(
            f"/datastores/{datastore_id}/reset",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class DatastoresResourceWithRawResponse:
    def __init__(self, datastores: DatastoresResource) -> None:
        self._datastores = datastores

        self.create = to_raw_response_wrapper(
            datastores.create,
        )
        self.update = to_raw_response_wrapper(
            datastores.update,
        )
        self.list = to_raw_response_wrapper(
            datastores.list,
        )
        self.delete = to_raw_response_wrapper(
            datastores.delete,
        )
        self.metadata = to_raw_response_wrapper(
            datastores.metadata,
        )
        self.reset = to_raw_response_wrapper(
            datastores.reset,
        )

    @cached_property
    def documents(self) -> DocumentsResourceWithRawResponse:
        return DocumentsResourceWithRawResponse(self._datastores.documents)


class AsyncDatastoresResourceWithRawResponse:
    def __init__(self, datastores: AsyncDatastoresResource) -> None:
        self._datastores = datastores

        self.create = async_to_raw_response_wrapper(
            datastores.create,
        )
        self.update = async_to_raw_response_wrapper(
            datastores.update,
        )
        self.list = async_to_raw_response_wrapper(
            datastores.list,
        )
        self.delete = async_to_raw_response_wrapper(
            datastores.delete,
        )
        self.metadata = async_to_raw_response_wrapper(
            datastores.metadata,
        )
        self.reset = async_to_raw_response_wrapper(
            datastores.reset,
        )

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithRawResponse:
        return AsyncDocumentsResourceWithRawResponse(self._datastores.documents)


class DatastoresResourceWithStreamingResponse:
    def __init__(self, datastores: DatastoresResource) -> None:
        self._datastores = datastores

        self.create = to_streamed_response_wrapper(
            datastores.create,
        )
        self.update = to_streamed_response_wrapper(
            datastores.update,
        )
        self.list = to_streamed_response_wrapper(
            datastores.list,
        )
        self.delete = to_streamed_response_wrapper(
            datastores.delete,
        )
        self.metadata = to_streamed_response_wrapper(
            datastores.metadata,
        )
        self.reset = to_streamed_response_wrapper(
            datastores.reset,
        )

    @cached_property
    def documents(self) -> DocumentsResourceWithStreamingResponse:
        return DocumentsResourceWithStreamingResponse(self._datastores.documents)


class AsyncDatastoresResourceWithStreamingResponse:
    def __init__(self, datastores: AsyncDatastoresResource) -> None:
        self._datastores = datastores

        self.create = async_to_streamed_response_wrapper(
            datastores.create,
        )
        self.update = async_to_streamed_response_wrapper(
            datastores.update,
        )
        self.list = async_to_streamed_response_wrapper(
            datastores.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            datastores.delete,
        )
        self.metadata = async_to_streamed_response_wrapper(
            datastores.metadata,
        )
        self.reset = async_to_streamed_response_wrapper(
            datastores.reset,
        )

    @cached_property
    def documents(self) -> AsyncDocumentsResourceWithStreamingResponse:
        return AsyncDocumentsResourceWithStreamingResponse(self._datastores.documents)
