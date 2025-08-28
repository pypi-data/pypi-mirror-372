# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "SearchMemoriesResponse",
    "Result",
    "ResultContext",
    "ResultContextChild",
    "ResultContextParent",
    "ResultDocument",
]


class ResultContextChild(BaseModel):
    memory: str
    """The contextual memory content"""

    relation: Literal["updates", "extends", "derives"]
    """Relation type between this memory and its parent/child"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Contextual memory last update date"""

    metadata: Optional[Dict[str, object]] = None
    """Contextual memory metadata"""

    version: Optional[float] = None
    """
    Relative version distance from the primary memory (+1 for direct child, +2 for
    grand-child, etc.)
    """


class ResultContextParent(BaseModel):
    memory: str
    """The contextual memory content"""

    relation: Literal["updates", "extends", "derives"]
    """Relation type between this memory and its parent/child"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Contextual memory last update date"""

    metadata: Optional[Dict[str, object]] = None
    """Contextual memory metadata"""

    version: Optional[float] = None
    """
    Relative version distance from the primary memory (-1 for direct parent, -2 for
    grand-parent, etc.)
    """


class ResultContext(BaseModel):
    children: Optional[List[ResultContextChild]] = None

    parents: Optional[List[ResultContextParent]] = None


class ResultDocument(BaseModel):
    id: str
    """Document ID"""

    created_at: datetime = FieldInfo(alias="createdAt")
    """Document creation date"""

    metadata: Optional[Dict[str, object]] = None
    """Document metadata"""

    title: str
    """Document title"""

    type: str
    """Document type"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Document last update date"""


class Result(BaseModel):
    id: str
    """Memory entry ID"""

    memory: str
    """The memory content"""

    metadata: Optional[Dict[str, object]] = None
    """Memory metadata"""

    similarity: float
    """Similarity score between the query and memory entry"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """Memory last update date"""

    context: Optional[ResultContext] = None
    """Object containing arrays of parent and child contextual memories"""

    documents: Optional[List[ResultDocument]] = None
    """Associated documents for this memory entry"""

    version: Optional[float] = None
    """Version number of this memory entry"""


class SearchMemoriesResponse(BaseModel):
    results: List[Result]
    """Array of matching memory entries with similarity scores"""

    timing: float
    """Search execution time in milliseconds"""

    total: float
    """Total number of results returned"""
