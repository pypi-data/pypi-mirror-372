# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Mapping, cast
from datetime import datetime
from typing_extensions import Literal

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
from ...pagination import SyncDocumentsPage, AsyncDocumentsPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.datastores import (
    document_list_params,
    document_ingest_params,
    document_set_metadata_params,
    document_get_parse_result_params,
)
from ...types.datastores.document_metadata import DocumentMetadata
from ...types.datastores.ingestion_response import IngestionResponse
from ...types.datastores.document_get_parse_result_response import DocumentGetParseResultResponse

__all__ = ["DocumentsResource", "AsyncDocumentsResource"]


class DocumentsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return DocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return DocumentsResourceWithStreamingResponse(self)

    def list(
        self,
        datastore_id: str,
        *,
        cursor: str | NotGiven = NOT_GIVEN,
        document_name_prefix: str | NotGiven = NOT_GIVEN,
        ingestion_job_status: List[Literal["pending", "processing", "retrying", "completed", "failed", "cancelled"]]
        | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        uploaded_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        uploaded_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncDocumentsPage[DocumentMetadata]:
        """
        Get list of documents in a given `Datastore`, including document `id`, `name`,
        and ingestion job `status`.

        Performs `cursor`-based pagination if the number of documents exceeds the
        requested `limit`. The returned `cursor` can be passed to the next
        `GET /datastores/{datastore_id}/documents` call to retrieve the next set of
        documents.

        Args:
          datastore_id: Datastore ID of the datastore to retrieve documents for

          cursor: Cursor from the previous call to list documents, used to retrieve the next set
              of results

          document_name_prefix: Filters documents with the given prefix.

          ingestion_job_status: Filters documents whose ingestion job status matches (one of) the provided
              status(es).

          limit: Maximum number of documents to return

          uploaded_after: Filters documents uploaded at or after specified timestamp.

          uploaded_before: Filters documents uploaded at or before specified timestamp.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._get_api_list(
            f"/datastores/{datastore_id}/documents",
            page=SyncDocumentsPage[DocumentMetadata],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "document_name_prefix": document_name_prefix,
                        "ingestion_job_status": ingestion_job_status,
                        "limit": limit,
                        "uploaded_after": uploaded_after,
                        "uploaded_before": uploaded_before,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=DocumentMetadata,
        )

    def delete(
        self,
        document_id: str,
        *,
        datastore_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a given document from its `Datastore`.

        This operation is irreversible.

        Args:
          datastore_id: Datastore ID of the datastore from which to delete the document

          document_id: Document ID of the document to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._delete(
            f"/datastores/{datastore_id}/documents/{document_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def get_parse_result(
        self,
        document_id: str,
        *,
        datastore_id: str,
        output_types: List[Literal["markdown-document", "markdown-per-page", "blocks-per-page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetParseResultResponse:
        """
        Get the parse results that are generated during ingestion for a given document.
        Retrieving parse results for existing documents ingested before the release of
        this endpoint is not supported and will return a 404 error.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          output_types: The desired output format(s) of the parsed file. Must be `markdown-document`,
              `markdown-per-page`, and/or `blocks-per-page`. Specify multiple values to get
              multiple formats in the response. `markdown-document` parses the whole document
              into a single concatenated markdown output. `markdown-per-page` provides
              markdown output per page. `blocks-per-page` provides a structured JSON
              representation of the content blocks on each page, sorted by reading order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._get(
            f"/datastores/{datastore_id}/documents/{document_id}/parse",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"output_types": output_types}, document_get_parse_result_params.DocumentGetParseResultParams
                ),
            ),
            cast_to=DocumentGetParseResultResponse,
        )

    def ingest(
        self,
        datastore_id: str,
        *,
        file: FileTypes,
        metadata: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestionResponse:
        """Ingest a document into a given `Datastore`.

        Ingestion is an asynchronous task.

        Returns a document `id` which can be used to
        track the status of the ingestion job through calls to the
        `GET /datastores/{datastore_id}/documents/{document_id}/metadata` API.

        This `id` can also be used to delete the document through the
        `DELETE /datastores/{datastore_id}/documents/{document_id}` API.

        `file` must be a PDF, HTML, DOC(X) or PPT(X) file. The filename must end with
        one of the following extensions: `.pdf`, `.html`, `.htm`, `.mhtml`, `.doc`,
        `.docx`, `.ppt`, `.pptx`.

        Args:
          datastore_id: Datastore ID of the datastore in which to ingest the document

          file: File to ingest.

          metadata: Metadata request in JSON format. `custom_metadata` is a flat dictionary
              containing one or more key-value pairs, where each value must be a primitive
              type (`str`, `bool`, `float`, or `int`). The default maximum metadata fields
              that can be used is 15, contact support if more is needed.The combined size of
              the metadata must not exceed **2 KB** when encoded as JSON.The strings with date
              format must stay in date format or be avoided if not in date format.The
              `custom_metadata.url` field is automatically included in returned attributions
              during query time, if provided.

              **Example Request Body:**

              ```json
              {
                "custom_metadata": {
                  "topic": "science",
                  "difficulty": 3
                }
              }
              ```

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "metadata": metadata,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/datastores/{datastore_id}/documents",
            body=maybe_transform(body, document_ingest_params.DocumentIngestParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestionResponse,
        )

    def metadata(
        self,
        document_id: str,
        *,
        datastore_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentMetadata:
        """
        Get details of a given document, including its `name` and ingestion job
        `status`.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._get(
            f"/datastores/{datastore_id}/documents/{document_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentMetadata,
        )

    def set_metadata(
        self,
        document_id: str,
        *,
        datastore_id: str,
        custom_metadata: Dict[str, Union[bool, float, str]] | NotGiven = NOT_GIVEN,
        custom_metadata_config: Dict[str, document_set_metadata_params.CustomMetadataConfig] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentMetadata:
        """
        Post details of a given document that will enrich the chunk and be added to the
        context or just for filtering. If Just for filtering, start with "\\__" in the
        key.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          custom_metadata: Custom metadata for the document, provided by the user at ingestion time.Must be
              a JSON-serializable dictionary with string keys and simple primitive values
              (str, int, float, bool). The total size must not exceed 2 KB.The strings with
              date format must stay in date format or be avodied if not in date format.The
              'custom_metadata.url' field is automatically included in returned attributions
              during query time, if provided.The default maximum metadata fields that can be
              used is 15, contact support if more is needed.

          custom_metadata_config: A dictionary mapping metadata field names to the configuration to use for each
              field.

                      - If a metadata field is not present in the dictionary, the default configuration will be used.

                      - If the dictionary is not provided, metadata will be added in chunks but will not be retrievable.

                      Limits: - Maximum characters per metadata field (for prompt or rerank): 400

                      - Maximum number of metadata fields (for prompt or retrieval): 10

                      Contact support@contextual.ai to request quota increases.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return self._post(
            f"/datastores/{datastore_id}/documents/{document_id}/metadata",
            body=maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "custom_metadata_config": custom_metadata_config,
                },
                document_set_metadata_params.DocumentSetMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentMetadata,
        )


class AsyncDocumentsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/ContextualAI/contextual-client-python#with_streaming_response
        """
        return AsyncDocumentsResourceWithStreamingResponse(self)

    def list(
        self,
        datastore_id: str,
        *,
        cursor: str | NotGiven = NOT_GIVEN,
        document_name_prefix: str | NotGiven = NOT_GIVEN,
        ingestion_job_status: List[Literal["pending", "processing", "retrying", "completed", "failed", "cancelled"]]
        | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        uploaded_after: Union[str, datetime] | NotGiven = NOT_GIVEN,
        uploaded_before: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[DocumentMetadata, AsyncDocumentsPage[DocumentMetadata]]:
        """
        Get list of documents in a given `Datastore`, including document `id`, `name`,
        and ingestion job `status`.

        Performs `cursor`-based pagination if the number of documents exceeds the
        requested `limit`. The returned `cursor` can be passed to the next
        `GET /datastores/{datastore_id}/documents` call to retrieve the next set of
        documents.

        Args:
          datastore_id: Datastore ID of the datastore to retrieve documents for

          cursor: Cursor from the previous call to list documents, used to retrieve the next set
              of results

          document_name_prefix: Filters documents with the given prefix.

          ingestion_job_status: Filters documents whose ingestion job status matches (one of) the provided
              status(es).

          limit: Maximum number of documents to return

          uploaded_after: Filters documents uploaded at or after specified timestamp.

          uploaded_before: Filters documents uploaded at or before specified timestamp.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        return self._get_api_list(
            f"/datastores/{datastore_id}/documents",
            page=AsyncDocumentsPage[DocumentMetadata],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "document_name_prefix": document_name_prefix,
                        "ingestion_job_status": ingestion_job_status,
                        "limit": limit,
                        "uploaded_after": uploaded_after,
                        "uploaded_before": uploaded_before,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            model=DocumentMetadata,
        )

    async def delete(
        self,
        document_id: str,
        *,
        datastore_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Delete a given document from its `Datastore`.

        This operation is irreversible.

        Args:
          datastore_id: Datastore ID of the datastore from which to delete the document

          document_id: Document ID of the document to delete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._delete(
            f"/datastores/{datastore_id}/documents/{document_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def get_parse_result(
        self,
        document_id: str,
        *,
        datastore_id: str,
        output_types: List[Literal["markdown-document", "markdown-per-page", "blocks-per-page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentGetParseResultResponse:
        """
        Get the parse results that are generated during ingestion for a given document.
        Retrieving parse results for existing documents ingested before the release of
        this endpoint is not supported and will return a 404 error.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          output_types: The desired output format(s) of the parsed file. Must be `markdown-document`,
              `markdown-per-page`, and/or `blocks-per-page`. Specify multiple values to get
              multiple formats in the response. `markdown-document` parses the whole document
              into a single concatenated markdown output. `markdown-per-page` provides
              markdown output per page. `blocks-per-page` provides a structured JSON
              representation of the content blocks on each page, sorted by reading order.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._get(
            f"/datastores/{datastore_id}/documents/{document_id}/parse",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"output_types": output_types}, document_get_parse_result_params.DocumentGetParseResultParams
                ),
            ),
            cast_to=DocumentGetParseResultResponse,
        )

    async def ingest(
        self,
        datastore_id: str,
        *,
        file: FileTypes,
        metadata: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> IngestionResponse:
        """Ingest a document into a given `Datastore`.

        Ingestion is an asynchronous task.

        Returns a document `id` which can be used to
        track the status of the ingestion job through calls to the
        `GET /datastores/{datastore_id}/documents/{document_id}/metadata` API.

        This `id` can also be used to delete the document through the
        `DELETE /datastores/{datastore_id}/documents/{document_id}` API.

        `file` must be a PDF, HTML, DOC(X) or PPT(X) file. The filename must end with
        one of the following extensions: `.pdf`, `.html`, `.htm`, `.mhtml`, `.doc`,
        `.docx`, `.ppt`, `.pptx`.

        Args:
          datastore_id: Datastore ID of the datastore in which to ingest the document

          file: File to ingest.

          metadata: Metadata request in JSON format. `custom_metadata` is a flat dictionary
              containing one or more key-value pairs, where each value must be a primitive
              type (`str`, `bool`, `float`, or `int`). The default maximum metadata fields
              that can be used is 15, contact support if more is needed.The combined size of
              the metadata must not exceed **2 KB** when encoded as JSON.The strings with date
              format must stay in date format or be avoided if not in date format.The
              `custom_metadata.url` field is automatically included in returned attributions
              during query time, if provided.

              **Example Request Body:**

              ```json
              {
                "custom_metadata": {
                  "topic": "science",
                  "difficulty": 3
                }
              }
              ```

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "metadata": metadata,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/datastores/{datastore_id}/documents",
            body=await async_maybe_transform(body, document_ingest_params.DocumentIngestParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=IngestionResponse,
        )

    async def metadata(
        self,
        document_id: str,
        *,
        datastore_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentMetadata:
        """
        Get details of a given document, including its `name` and ingestion job
        `status`.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._get(
            f"/datastores/{datastore_id}/documents/{document_id}/metadata",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentMetadata,
        )

    async def set_metadata(
        self,
        document_id: str,
        *,
        datastore_id: str,
        custom_metadata: Dict[str, Union[bool, float, str]] | NotGiven = NOT_GIVEN,
        custom_metadata_config: Dict[str, document_set_metadata_params.CustomMetadataConfig] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DocumentMetadata:
        """
        Post details of a given document that will enrich the chunk and be added to the
        context or just for filtering. If Just for filtering, start with "\\__" in the
        key.

        Args:
          datastore_id: Datastore ID of the datastore from which to retrieve the document

          document_id: Document ID of the document to retrieve details for

          custom_metadata: Custom metadata for the document, provided by the user at ingestion time.Must be
              a JSON-serializable dictionary with string keys and simple primitive values
              (str, int, float, bool). The total size must not exceed 2 KB.The strings with
              date format must stay in date format or be avodied if not in date format.The
              'custom_metadata.url' field is automatically included in returned attributions
              during query time, if provided.The default maximum metadata fields that can be
              used is 15, contact support if more is needed.

          custom_metadata_config: A dictionary mapping metadata field names to the configuration to use for each
              field.

                      - If a metadata field is not present in the dictionary, the default configuration will be used.

                      - If the dictionary is not provided, metadata will be added in chunks but will not be retrievable.

                      Limits: - Maximum characters per metadata field (for prompt or rerank): 400

                      - Maximum number of metadata fields (for prompt or retrieval): 10

                      Contact support@contextual.ai to request quota increases.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not datastore_id:
            raise ValueError(f"Expected a non-empty value for `datastore_id` but received {datastore_id!r}")
        if not document_id:
            raise ValueError(f"Expected a non-empty value for `document_id` but received {document_id!r}")
        return await self._post(
            f"/datastores/{datastore_id}/documents/{document_id}/metadata",
            body=await async_maybe_transform(
                {
                    "custom_metadata": custom_metadata,
                    "custom_metadata_config": custom_metadata_config,
                },
                document_set_metadata_params.DocumentSetMetadataParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentMetadata,
        )


class DocumentsResourceWithRawResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.list = to_raw_response_wrapper(
            documents.list,
        )
        self.delete = to_raw_response_wrapper(
            documents.delete,
        )
        self.get_parse_result = to_raw_response_wrapper(
            documents.get_parse_result,
        )
        self.ingest = to_raw_response_wrapper(
            documents.ingest,
        )
        self.metadata = to_raw_response_wrapper(
            documents.metadata,
        )
        self.set_metadata = to_raw_response_wrapper(
            documents.set_metadata,
        )


class AsyncDocumentsResourceWithRawResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.list = async_to_raw_response_wrapper(
            documents.list,
        )
        self.delete = async_to_raw_response_wrapper(
            documents.delete,
        )
        self.get_parse_result = async_to_raw_response_wrapper(
            documents.get_parse_result,
        )
        self.ingest = async_to_raw_response_wrapper(
            documents.ingest,
        )
        self.metadata = async_to_raw_response_wrapper(
            documents.metadata,
        )
        self.set_metadata = async_to_raw_response_wrapper(
            documents.set_metadata,
        )


class DocumentsResourceWithStreamingResponse:
    def __init__(self, documents: DocumentsResource) -> None:
        self._documents = documents

        self.list = to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = to_streamed_response_wrapper(
            documents.delete,
        )
        self.get_parse_result = to_streamed_response_wrapper(
            documents.get_parse_result,
        )
        self.ingest = to_streamed_response_wrapper(
            documents.ingest,
        )
        self.metadata = to_streamed_response_wrapper(
            documents.metadata,
        )
        self.set_metadata = to_streamed_response_wrapper(
            documents.set_metadata,
        )


class AsyncDocumentsResourceWithStreamingResponse:
    def __init__(self, documents: AsyncDocumentsResource) -> None:
        self._documents = documents

        self.list = async_to_streamed_response_wrapper(
            documents.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            documents.delete,
        )
        self.get_parse_result = async_to_streamed_response_wrapper(
            documents.get_parse_result,
        )
        self.ingest = async_to_streamed_response_wrapper(
            documents.ingest,
        )
        self.metadata = async_to_streamed_response_wrapper(
            documents.metadata,
        )
        self.set_metadata = async_to_streamed_response_wrapper(
            documents.set_metadata,
        )
