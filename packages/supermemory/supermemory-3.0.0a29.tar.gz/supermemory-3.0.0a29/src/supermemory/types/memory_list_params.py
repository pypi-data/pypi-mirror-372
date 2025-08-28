# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["MemoryListParams"]


class MemoryListParams(TypedDict, total=False):
    container_tags: Annotated[List[str], PropertyInfo(alias="containerTags")]
    """Optional tags this memory should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group memories.
    """

    filters: str
    """Optional filters to apply to the search"""

    include_content: Annotated[bool, PropertyInfo(alias="includeContent")]
    """Whether to include the content field in the response.

    Warning: This can make responses significantly larger.
    """

    limit: Union[str, float]
    """Number of items per page"""

    order: Literal["asc", "desc"]
    """Sort order"""

    page: Union[str, float]
    """Page number to fetch"""

    sort: Literal["createdAt", "updatedAt"]
    """Field to sort by"""
