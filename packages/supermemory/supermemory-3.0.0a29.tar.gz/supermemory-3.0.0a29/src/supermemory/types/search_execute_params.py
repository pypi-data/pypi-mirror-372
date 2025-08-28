# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["SearchExecuteParams", "Filters", "FiltersUnionMember0"]


class SearchExecuteParams(TypedDict, total=False):
    q: Required[str]
    """Search query string"""

    categories_filter: Annotated[
        List[Literal["technology", "science", "business", "health"]], PropertyInfo(alias="categoriesFilter")
    ]
    """Optional category filters"""

    chunk_threshold: Annotated[float, PropertyInfo(alias="chunkThreshold")]
    """Threshold / sensitivity for chunk selection.

    0 is least sensitive (returns most chunks, more results), 1 is most sensitive
    (returns lesser chunks, accurate results)
    """

    container_tags: Annotated[List[str], PropertyInfo(alias="containerTags")]
    """Optional tags this search should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to filter memories.
    """

    doc_id: Annotated[str, PropertyInfo(alias="docId")]
    """Optional document ID to search within.

    You can use this to find chunks in a very large document.
    """

    document_threshold: Annotated[float, PropertyInfo(alias="documentThreshold")]
    """Threshold / sensitivity for document selection.

    0 is least sensitive (returns most documents, more results), 1 is most sensitive
    (returns lesser documents, accurate results)
    """

    filters: Filters
    """Optional filters to apply to the search"""

    include_full_docs: Annotated[bool, PropertyInfo(alias="includeFullDocs")]
    """If true, include full document in the response.

    This is helpful if you want a chatbot to know the full context of the document.
    """

    include_summary: Annotated[bool, PropertyInfo(alias="includeSummary")]
    """If true, include document summary in the response.

    This is helpful if you want a chatbot to know the full context of the document.
    """

    limit: int
    """Maximum number of results to return"""

    only_matching_chunks: Annotated[bool, PropertyInfo(alias="onlyMatchingChunks")]
    """If true, only return matching chunks without context.

    Normally, we send the previous and next chunk to provide more context for LLMs.
    If you only want the matching chunk, set this to true.
    """

    rerank: bool
    """If true, rerank the results based on the query.

    This is helpful if you want to ensure the most relevant results are returned.
    """

    rewrite_query: Annotated[bool, PropertyInfo(alias="rewriteQuery")]
    """If true, rewrites the query to make it easier to find documents.

    This increases the latency by about 400ms
    """


class FiltersUnionMember0(TypedDict, total=False):
    and_: Annotated[Iterable[object], PropertyInfo(alias="AND")]

    or_: Annotated[Iterable[object], PropertyInfo(alias="OR")]


Filters: TypeAlias = Union[FiltersUnionMember0, Dict[str, object]]
