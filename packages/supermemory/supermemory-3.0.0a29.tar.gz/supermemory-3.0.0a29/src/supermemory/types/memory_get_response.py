# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["MemoryGetResponse"]


class MemoryGetResponse(BaseModel):
    id: str
    """Unique identifier of the memory."""

    connection_id: Optional[str] = FieldInfo(alias="connectionId", default=None)
    """Optional ID of connection the memory was created from.

    This is useful for identifying the source of the memory.
    """

    content: Optional[str] = None
    """The content to extract and process into a memory.

    This can be a URL to a website, a PDF, an image, or a video.

    Plaintext: Any plaintext format

    URL: A URL to a website, PDF, image, or video

    We automatically detect the content type from the url's response format.
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

    og_image: Optional[str] = FieldInfo(alias="ogImage", default=None)

    source: Optional[str] = None
    """Source of the memory"""

    status: Literal["unknown", "queued", "extracting", "chunking", "embedding", "indexing", "done", "failed"]
    """Status of the memory"""

    summary: Optional[str] = None
    """Summary of the memory content"""

    summary_embedding_model: Optional[str] = FieldInfo(alias="summaryEmbeddingModel", default=None)

    summary_embedding_model_new: Optional[str] = FieldInfo(alias="summaryEmbeddingModelNew", default=None)

    summary_embedding_new: Optional[List[float]] = FieldInfo(alias="summaryEmbeddingNew", default=None)

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

    raw: None = None
    """Raw content of the memory"""

    url: Optional[str] = None
    """URL of the memory"""
