# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ConnectionGetByTagsParams"]


class ConnectionGetByTagsParams(TypedDict, total=False):
    container_tags: Required[Annotated[List[str], PropertyInfo(alias="containerTags")]]
    """Comma-separated list of container tags to filter connection by"""
