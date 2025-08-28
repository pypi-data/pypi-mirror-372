# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["MemoryAddParams"]


class MemoryAddParams(TypedDict, total=False):
    container_tag: Annotated[str, PropertyInfo(alias="containerTag")]
    """Optional tag this memory should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group memories.
    """

    container_tags: Annotated[List[str], PropertyInfo(alias="containerTags")]
    """
    (DEPRECATED: Use containerTag instead) Optional tags this memory should be
    containerized by. This can be an ID for your user, a project ID, or any other
    identifier you wish to use to group memories.
    """

    content: str
    """The content to extract and process into a memory.

    This can be a URL to a website, a PDF, an image, or a video.

    Plaintext: Any plaintext format

    URL: A URL to a website, PDF, image, or video

    We automatically detect the content type from the url's response format.
    """

    custom_id: Annotated[str, PropertyInfo(alias="customId")]
    """Optional custom ID of the memory.

    This could be an ID from your database that will uniquely identify this memory.
    """

    metadata: Dict[str, Union[str, float, bool]]
    """Optional metadata for the memory.

    This is used to store additional information about the memory. You can use this
    to store any additional information you need about the memory. Metadata can be
    filtered through. Keys must be strings and are case sensitive. Values can be
    strings, numbers, or booleans. You cannot nest objects.
    """
