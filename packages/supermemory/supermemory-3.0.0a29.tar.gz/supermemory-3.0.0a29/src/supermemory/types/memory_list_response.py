# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MemoryListResponse", "Memory", "Pagination"]


class Memory(BaseModel):
    id: str
    """Unique identifier of the memory."""

    connection_id: Optional[str] = FieldInfo(alias="connectionId", default=None)
    """Optional ID of connection the memory was created from.

    This is useful for identifying the source of the memory.
    """

    created_at: datetime = FieldInfo(alias="createdAt")
    """Creation timestamp"""

    custom_id: Optional[str] = FieldInfo(alias="customId", default=None)
    """Optional custom ID of the memory.

    This could be an ID from your database that will uniquely identify this memory.
    """

    metadata: Union[str, float, bool, Dict[str, object], List[object], None] = None
    """Optional metadata for the memory.

    This is used to store additional information about the memory. You can use this
    to store any additional information you need about the memory. Metadata can be
    filtered through. Keys must be strings and are case sensitive. Values can be
    strings, numbers, or booleans. You cannot nest objects.
    """

    status: Literal["unknown", "queued", "extracting", "chunking", "embedding", "indexing", "done", "failed"]
    """Status of the memory"""

    summary: Optional[str] = None
    """Summary of the memory content"""

    title: Optional[str] = None
    """Title of the memory"""

    type: Literal[
        "text",
        "pdf",
        "tweet",
        "google_doc",
        "google_slide",
        "google_sheet",
        "image",
        "video",
        "notion_doc",
        "webpage",
        "onedrive",
    ]
    """Type of the memory"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Last update timestamp"""

    container_tags: Optional[List[str]] = FieldInfo(alias="containerTags", default=None)
    """Optional tags this memory should be containerized by.

    This can be an ID for your user, a project ID, or any other identifier you wish
    to use to group memories.
    """

    content: Optional[str] = None
    """Content of the memory (only included when includeContent=true)"""


class Pagination(BaseModel):
    current_page: float = FieldInfo(alias="currentPage")

    limit: float

    total_items: float = FieldInfo(alias="totalItems")

    total_pages: float = FieldInfo(alias="totalPages")


class MemoryListResponse(BaseModel):
    memories: List[Memory]

    pagination: Pagination
    """Pagination metadata"""
