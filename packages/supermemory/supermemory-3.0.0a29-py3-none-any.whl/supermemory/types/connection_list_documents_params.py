# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ConnectionListDocumentsParams"]


class ConnectionListDocumentsParams(TypedDict, total=False):
    container_tags: Annotated[List[str], PropertyInfo(alias="containerTags")]
    """Optional comma-separated list of container tags to filter documents by"""
