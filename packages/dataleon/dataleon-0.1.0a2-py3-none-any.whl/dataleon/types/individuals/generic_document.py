# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from ..._models import BaseModel
from ..shared.check import Check

__all__ = ["GenericDocument", "Table", "Value"]


class Table(BaseModel):
    operation: Optional[List[object]] = None
    """List of operations or actions associated with the table."""


class Value(BaseModel):
    confidence: Optional[float] = None
    """Confidence score (between 0 and 1) for the extracted value."""

    name: Optional[str] = None
    """Name or label of the extracted field."""

    value: Optional[List[int]] = None
    """List of integer values related to the field (e.g., bounding box coordinates)."""


class GenericDocument(BaseModel):
    id: Optional[str] = None
    """Unique identifier of the document."""

    checks: Optional[List[Check]] = None
    """List of verification checks performed on the document."""

    created_at: Optional[datetime] = None
    """Timestamp when the document was created or uploaded."""

    document_type: Optional[str] = None
    """Type/category of the document."""

    name: Optional[str] = None
    """Name or label for the document."""

    signed_url: Optional[str] = None
    """Signed URL for accessing the document file."""

    state: Optional[str] = None
    """Current processing state of the document (e.g., WAITING, PROCESSED)."""

    status: Optional[str] = None
    """Status of the document reception or approval."""

    tables: Optional[List[Table]] = None
    """List of tables extracted from the document, each containing operations."""

    values: Optional[List[Value]] = None
    """Extracted key-value pairs from the document, including confidence scores."""
