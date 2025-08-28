# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel

__all__ = ["DocumentResponse", "Document"]


class Document(BaseModel):
    id: Optional[str] = None
    """Unique identifier of the document."""

    document_type: Optional[str] = None
    """Functional type of the document (e.g., identity document, invoice)."""

    filename: Optional[str] = None
    """Original filename of the uploaded document."""

    name: Optional[str] = None
    """Human-readable name of the document."""

    signed_url: Optional[str] = None
    """Secure URL to access the document."""

    state: Optional[str] = None
    """Processing state of the document (e.g., WAITING, STARTED, RUNNING, PROCESSED)."""

    status: Optional[str] = None
    """Validation status of the document (e.g., need_review, approved, rejected)."""

    workspace_id: Optional[str] = None
    """Identifier of the workspace to which the document belongs."""


class DocumentResponse(BaseModel):
    documents: Optional[List[Document]] = None
    """List of documents associated with the response."""

    total_document: Optional[int] = None
    """Total number of documents available in the response."""
