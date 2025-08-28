# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = ["SearchMemoriesParams", "Filters", "FiltersUnionMember0", "Include"]


class SearchMemoriesParams(TypedDict, total=False):
    q: Required[str]
    """Search query string"""

    container_tag: Annotated[str, PropertyInfo(alias="containerTag")]
    """Optional tag this search should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to filter memories.
    """

    filters: Filters
    """Optional filters to apply to the search"""

    include: Include

    limit: int
    """Maximum number of results to return"""

    rerank: bool
    """If true, rerank the results based on the query.

    This is helpful if you want to ensure the most relevant results are returned.
    """

    rewrite_query: Annotated[bool, PropertyInfo(alias="rewriteQuery")]
    """If true, rewrites the query to make it easier to find documents.

    This increases the latency by about 400ms
    """

    threshold: float
    """Threshold / sensitivity for memories selection.

    0 is least sensitive (returns most memories, more results), 1 is most sensitive
    (returns lesser memories, accurate results)
    """


class FiltersUnionMember0(TypedDict, total=False):
    and_: Annotated[Iterable[object], PropertyInfo(alias="AND")]

    or_: Annotated[Iterable[object], PropertyInfo(alias="OR")]


Filters: TypeAlias = Union[FiltersUnionMember0, Dict[str, object]]


class Include(TypedDict, total=False):
    documents: bool

    related_memories: Annotated[bool, PropertyInfo(alias="relatedMemories")]

    summaries: bool
